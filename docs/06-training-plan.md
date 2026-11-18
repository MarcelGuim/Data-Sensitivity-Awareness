# 06 Training plan

Labels: see `AGENTS.md`.

## Stack
- **Decided:** PyTorch + Hugging Face + PEFT, CUDA.
- **Decided (2026-11-09, Marcel):** Plain LoRA on the fp16 model; QLoRA (bitsandbytes 4-bit) is the fallback. Supersedes QLoRA.
- **Proposed (2026-11-09, Claude):** transformers `Trainer` with explicit loss masking instead of TRL `SFTTrainer` (docs/07, Q48). Code: `kaggle/train_qwen/train.py`.
- **Measured (2026-11-09, Kaggle T4, smoke test, 10 steps):** fp16 LoRA fits and runs without NaN; 26.4 s per optimizer step (16 conversations), so the 500-step run is about 3.7 h; loss 2.13 → 0.90. Versions: torch 2.11.0+cu130, transformers 5.20.2, peft 0.21.2 (pinned). Kaggle's torchao 0.10 breaks peft 0.21; uninstall it first. After 10 steps the model refused every request, including authorized ones (expected this early; check again after the full run).
- **Decided (2026-11-09, Marcel):** 8,000 training conversations, training capped at 20 GPU-hours. **Estimate:** mean 683 tokens per conversation (Measured with the Qwen tokenizer, 2026-11-09), 500 optimizer steps; roughly 3–6 h on one T4, split over two Kaggle versions if it runs past one session. The smoke test gives the real s/step.
- **Measured (2026-11-09, Kaggle T4, full run):** 500 steps on 8,000 conversations in 3.79 h (27.3 s/step), one session, no NaN; loss 2.7 → about 0.07 (plateau from about epoch 0.6), mean train loss 0.132; data hash b305d2936f016ade. The three end-of-run samples (training examples, so not evidence of generalization) were all correct: refusal for a no-clearance employee asking for confidential data, verbatim share for a clearance employee, email summarized with the injection ignored. Adapter kept outside git.
- **Measured (2026-11-15, Wasilat with Claude, locally without a GPU):** Llama-3.2-3B-Instruct can use `kaggle/train_qwen/train.py` and the same `train.jsonl` unchanged (`--model meta-llama/Llama-3.2-3B-Instruct --out /kaggle/working/llama_lora`). Rebuilt `train.jsonl` hash matches the Qwen run (b305d2936f016ade); all 8,000 examples pass the masking checks with the Llama chat template (tokenizer from the ungated `unsloth/Llama-3.2-3B-Instruct` copy; **Unverified** that its template is byte-identical to Meta's, but `train.py` re-checks on Kaggle); mean 692 tokens, max 983. Llama's template puts the tool definitions in the first user turn and JSON-encodes tool results a second time; identical in training and evaluation. Notebook cells: `kaggle/train_llama/README.md`.
- **Decided (2026-10-16):** Runs on Kaggle Notebooks (free T4); rent only if Kaggle fails. Evaluation uses the same stack on Kaggle, so no adapter export is needed. Constraints: `02-compute-and-environment.md`.
- **Open:** Library versions, LoRA rank/alpha/target modules, learning rate, epochs, sequence length, batch size, runs and seeds (docs/07, Q26).

## Loss masking
- **Proposed:** Mask the loss to assistant turns only; otherwise the model trains on system prompts and canaries. (The older handoff lists this as a decision; the kickoff lists it as proposed. **Open**, docs/07, Q27.)
- **Proposed:** Check that TRL/PEFT support each model's chat template.
- **Proposed:** No thinking-mode models in the first experiments, because reasoning tags interfere with loss masking.

## Debugging path
- **Proposed:** Debug the data format, chat template and loss masking on a tiny model (for example Qwen2.5-0.5B-Instruct), on a laptop with plain LoRA or directly on Kaggle. Then a short QLoRA smoke test on Kaggle: check for fp16 NaN losses, time tokens/s, test checkpoint and resume (docs/07, Q28).

## Run plan
- **Proposed:** Week 2: script debugged on a tiny model.
- **Proposed:** Week 3: first real training run (Qwen3-4B); check training damage on benign tasks; evaluate the first checkpoint. Gate Nov 4: a trained checkpoint exists.
- **Proposed:** Week 4: train Llama-3.2-3B with the same script; main runs; retrain if adaptive attacks expose a weakness.
- **Proposed:** Week 5: retrain or re-evaluate if needed; larger model (~8B) if the Nov 11 gate is green and budget allows. **Decided:** go or no-go on Nov 11.
- **Proposed:** One model end to end first; do not debug both in parallel.
- **Proposed:** Results frozen Nov 18.
- **Estimate:** 10–20 GPU-hours per model for training including retries; 20–40 for two models.

## Run checklist (Kaggle, and any rental)
**Proposed:**
1. Freeze the model and framework first.
2. Debug the training script on a tiny model, then a short QLoRA smoke test on Kaggle.
3. Mask the loss to assistant turns only.
4. Have the dataset validated and uploaded.
5. Check remaining Kaggle quota; set a budget only if renting (docs/07, Q21).
6. Checkpoint every few hundred steps (needed anyway for Kaggle session limits).
7. Run long jobs as background runs; for rentals, shut the instance down the moment a run finishes.
