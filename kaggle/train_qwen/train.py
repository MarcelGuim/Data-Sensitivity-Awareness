"""LoRA fine-tuning of Qwen3-4B-Instruct-2507 for setup (c) (docs/06). Kaggle, CUDA.

Data: train.jsonl next to this file (built by scripts/prepare_kaggle.py): each line is a full
conversation whose last turn is the target assistant reply. Only that reply (and its end
token) carries loss; system prompt, user turn, tool call and tool result are masked to -100.

Precision:
  --precision fp16  plain LoRA on the fp16 model (default; Decided 2026-11-09, docs/07)
  --precision 4bit  QLoRA fallback (NF4 base) if fp16 runs out of memory or gives NaN losses
Evaluate the adapter with the same precision as (a) and (b).

Resume: checkpoints go to <out>/checkpoints every --save-steps optimizer steps. In a new Kaggle
session, add the previous version's output as input and pass --resume-dir <that>/qwen_lora;
the checkpoints are copied over and training continues from the last one.

Examples (Kaggle notebook cells, folder uploaded as a dataset):
  !python /kaggle/input/<train-folder>/train.py --max-steps 10 --save-steps 5   # smoke test
  !python /kaggle/input/<train-folder>/train.py                                  # full run
Output: /kaggle/working/qwen_lora/adapter (the LoRA weights for setup c) and train_meta.json.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def tokenize_example(tok, ex, max_len):
    """input_ids and labels with loss on the final assistant turn only. Stops loudly if the
    chat template does not render the prompt as an exact prefix of the full conversation."""
    msgs, tools = ex["messages"], ex.get("tools")
    if msgs[-1]["role"] != "assistant":
        sys.exit(f"{ex['task_id']}: last message is not the assistant target")
    prompt = tok.apply_chat_template(msgs[:-1], tools=tools, add_generation_prompt=True, tokenize=False)
    full = tok.apply_chat_template(msgs, tools=tools, tokenize=False)
    if not full.startswith(prompt):
        sys.exit(f"{ex['task_id']}: chat template is not prefix-stable; loss masking would be wrong.\n"
                 f"PROMPT END: {prompt[-200:]!r}\nFULL AT THAT POINT: {full[len(prompt) - 200:len(prompt) + 50]!r}")
    target_text = full[len(prompt):]
    if "<think>" in target_text:
        sys.exit(f"{ex['task_id']}: the template adds a <think> block to the target; use the non-thinking model")
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    if f_ids[:len(p_ids)] != p_ids:
        sys.exit(f"{ex['task_id']}: tokens of the prompt are not a prefix of the full conversation")
    if len(f_ids) > max_len:
        return None
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    return {"input_ids": f_ids, "labels": labels}, target_text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    ap.add_argument("--data", default=str(HERE / "train.jsonl"))
    ap.add_argument("--out", default="/kaggle/working/qwen_lora" if Path("/kaggle/working").exists()
                    else "runs/qwen_lora")
    ap.add_argument("--resume-dir", help="qwen_lora folder from an earlier Kaggle version")
    ap.add_argument("--precision", default="fp16", choices=["fp16", "4bit"])
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--max-steps", type=int, default=-1, help="for smoke tests")
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--save-steps", type=int, default=25)
    ap.add_argument("--limit", type=int, default=0, help="use only the first N examples")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpu", default="0", help="use one GPU only (matters on 2-GPU machines)")
    ap.add_argument("--max-hours", type=float, default=0,
                    help="save a checkpoint and stop after this many hours (from script start), exiting "
                         "normally so Kaggle keeps the output; 0 = no limit")
    args = ap.parse_args()
    start = time.time()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    import torch
    import transformers
    from packaging import version
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer, TrainerCallback,
                              TrainingArguments, set_seed)
    from transformers.trainer_utils import get_last_checkpoint
    try:
        import peft
        from peft import LoraConfig, get_peft_model
    except ImportError:
        sys.exit("peft missing: run `!pip uninstall -y -q torchao` and `!pip install -q peft` first")
    if not torch.cuda.is_available():
        sys.exit("No GPU. Kaggle: Settings > Accelerator > GPU T4.")
    if version.parse(transformers.__version__) < version.parse("4.51.0"):
        sys.exit(f"transformers {transformers.__version__} is too old for Qwen3; pip install -U transformers")
    set_seed(args.seed)

    out = Path(args.out)
    ckpt_dir = out / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    if args.resume_dir and get_last_checkpoint(str(ckpt_dir)) is None:
        src = Path(args.resume_dir) / "checkpoints"
        if get_last_checkpoint(str(src)) is None:
            sys.exit(f"--resume-dir has no checkpoint: {src}")
        shutil.copytree(src, ckpt_dir, dirs_exist_ok=True)
        print(f"copied checkpoints from {src}")

    # ---- data ----
    raw = Path(args.data).read_bytes()
    examples = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    if args.limit:
        examples = examples[:args.limit]
    for ex in examples:
        wording = ex["task_id"].split("/")[3]
        if (ex.get("split") != "train" or ex.get("sector") in {"healthcare", "finance"}
                or ex["family"] in {"indirect_document", "encoding"}
                or not re.fullmatch(r"[a-z]+-t\d+|email-\d+", wording)):
            sys.exit(f"held-out data in the training file: {ex['task_id']}")
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    data, dropped, lengths = [], 0, []
    for i, ex in enumerate(examples):
        r = tokenize_example(tok, ex, args.max_len)
        if r is None:
            dropped += 1
            continue
        feats, target_text = r
        data.append(feats)
        lengths.append(len(feats["input_ids"]))
        if i == 0:
            print("---- example 0: text that carries loss ----")
            print(repr(target_text))
            print("-------------------------------------------")
    if dropped > 0.01 * len(examples):
        sys.exit(f"{dropped} of {len(examples)} examples exceed --max-len {args.max_len}")
    print(f"{len(data)} examples, {dropped} dropped; tokens per example: "
          f"mean {sum(lengths) / len(lengths):.0f}, max {max(lengths)}")

    def collate(batch):
        n = max(len(b["input_ids"]) for b in batch)
        pad = tok.pad_token_id
        ids = [b["input_ids"] + [pad] * (n - len(b["input_ids"])) for b in batch]
        lab = [b["labels"] + [-100] * (n - len(b["labels"])) for b in batch]
        att = [[1] * len(b["input_ids"]) + [0] * (n - len(b["input_ids"])) for b in batch]
        return {"input_ids": torch.tensor(ids), "labels": torch.tensor(lab),
                "attention_mask": torch.tensor(att)}

    # ---- model ----
    dkey = "dtype" if version.parse(transformers.__version__) >= version.parse("4.56.0") else "torch_dtype"
    kw = {"device_map": {"": 0}, dkey: torch.float16}
    if args.precision == "4bit":
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, **kw)
    model.config.use_cache = False
    if args.precision == "4bit":
        from peft import prepare_model_for_kbit_training
        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False})
    else:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(
        r=args.rank, lora_alpha=args.alpha, lora_dropout=args.dropout,
        target_modules=TARGET_MODULES, task_type="CAUSAL_LM"))
    for p in model.parameters():
        if p.requires_grad:
            p.data = p.data.float()  # fp16 AMP needs fp32 trainable weights
    model.print_trainable_parameters()

    steps_per_epoch = math.ceil(len(data) / (args.batch_size * args.grad_accum))
    total = args.max_steps if args.max_steps > 0 else math.ceil(steps_per_epoch * args.epochs)
    log_path = out / "log.jsonl"

    class Log(TrainerCallback):
        def on_log(self, a, state, control, logs=None, **kw):
            if not logs:
                return
            with open(log_path, "a") as f:
                f.write(json.dumps({"step": state.global_step, "time": time.time(), **logs}) + "\n")
            loss = logs.get("loss")
            if loss is not None and (math.isnan(loss) or math.isinf(loss)):
                print("NaN/inf loss: stop. Try --precision 4bit or a lower --lr.")
                control.should_training_stop = True

    class TimeLimit(TrainerCallback):
        stopped = False

        def on_step_end(self, a, state, control, **kw):
            if args.max_hours and time.time() - start > args.max_hours * 3600:
                control.should_save = True
                control.should_training_stop = True
                TimeLimit.stopped = True

    targs = TrainingArguments(
        output_dir=str(ckpt_dir), per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum, num_train_epochs=args.epochs,
        max_steps=args.max_steps, learning_rate=args.lr, lr_scheduler_type="cosine",
        warmup_steps=max(1, int(0.03 * total)), weight_decay=0.0, max_grad_norm=1.0,
        logging_steps=5, save_strategy="steps", save_steps=args.save_steps, save_total_limit=2,
        fp16=True, bf16=False, report_to="none", remove_unused_columns=False,
        dataloader_num_workers=2, seed=args.seed, optim="adamw_torch")
    trainer = Trainer(model=model, args=targs, train_dataset=data, data_collator=collate,
                      callbacks=[Log(), TimeLimit()])
    last = get_last_checkpoint(str(ckpt_dir))
    print(f"{total} optimizer steps ({args.batch_size} x {args.grad_accum} per step); "
          f"resume from: {last or 'start'}")
    t0 = time.time()
    result = trainer.train(resume_from_checkpoint=last)
    hours = (time.time() - t0) / 3600
    if TimeLimit.stopped and trainer.state.global_step < trainer.state.max_steps:
        print(f"--max-hours {args.max_hours} reached at step {trainer.state.global_step}/{trainer.state.max_steps}; "
              f"checkpoint saved in {ckpt_dir}. Resume in a new version with --resume-dir (README). "
              "No adapter is written until training finishes.")
        return

    adapter_dir = out / "adapter"
    model.save_pretrained(str(adapter_dir))
    tok.save_pretrained(str(adapter_dir))
    meta = {"model": args.model, "precision": args.precision, "args": vars(args),
            "data_sha256_16": hashlib.sha256(raw).hexdigest()[:16], "examples": len(data),
            "optimizer_steps": trainer.state.global_step, "train_loss": result.training_loss,
            "hours_this_session": round(hours, 2), "gpu": torch.cuda.get_device_name(0),
            "torch": torch.__version__, "transformers": transformers.__version__,
            "peft": peft.__version__,
            "model_revision": getattr(model.config, "_commit_hash", None)}
    if (HERE / "build_info.json").exists():
        meta["build_info"] = json.loads((HERE / "build_info.json").read_text())
    (out / "train_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    print(f"adapter saved: {adapter_dir}")

    # ---- sanity check: three training conversations, greedy, with the adapter ----
    model.eval()
    model.config.use_cache = True
    tok.padding_side = "left"
    shown = set()
    for ex in examples:
        if ex["behaviour"] in shown:
            continue
        shown.add(ex["behaviour"])
        prompt = tok.apply_chat_template(ex["messages"][:-1], tools=ex.get("tools"),
                                         add_generation_prompt=True, tokenize=False)
        enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
            o = model.generate(**enc, do_sample=False, max_new_tokens=120, pad_token_id=tok.pad_token_id)
        print(f"\n[{ex['behaviour']} / {ex['family']} / {ex['requester_level']} / {ex['item_tier']}]")
        print("target:", ex["messages"][-1]["content"][:300])
        print("model: ", tok.decode(o[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)[:300])
        if len(shown) == 3:
            break


if __name__ == "__main__":
    main()
