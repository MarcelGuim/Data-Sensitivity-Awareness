# LoRA training of Llama-3.2-3B-Instruct for setup (c), on Kaggle

Same script and same data as the Qwen run (`kaggle/train_qwen/`, Marcel's files, unchanged); only the
model and output folder change, so the two models are trained identically. Everything in `kaggle/train_qwen/README.md`
(stopping safely, resuming, out-of-memory and NaN fixes) applies here too.

**Measured (2026-11-15, locally, no GPU, Llama 3.2 tokenizer from the ungated `unsloth/Llama-3.2-3B-Instruct`
copy):** the rebuilt `train.jsonl` has the same hash as the Qwen run (b305d2936f016ade). All 8,000
examples pass `train.py`'s masking checks with the Llama chat template (prompt is an exact prefix;
loss only on the final reply and its `<|eot_id|>`); none exceed 2,048 tokens (mean 692, max 983).
`train.py` repeats these checks with Meta's own tokenizer on Kaggle and stops if they fail.

## One-time setup
1. **Llama access:** on huggingface.co, open `meta-llama/Llama-3.2-3B-Instruct`, fill in the form and
   accept the license. Wait for approval (Settings > Gated Repositories shows the status).
2. Hugging Face > Settings > Access Tokens > create a **Read** token.
3. Build the data locally (it is not in git):
   `python3 scripts/dataset/build_tasks.py --data data/full && python3 scripts/prepare_kaggle.py`
4. kaggle.com > Datasets > New Dataset > upload the three files in `kaggle/train_qwen/`
   (`train.py`, `train.jsonl`, `build_info.json`), e.g. as `ece1776-train-llama`.
5. New notebook > Add Input > that dataset. Settings: Accelerator **GPU T4**, Internet **on**.
   Add-ons > Secrets > add `HF_TOKEN` (your token) and switch it on for this notebook.

## Notebook cells
```python
!pip uninstall -y -q torchao   # Kaggle's torchao 0.10 makes recent peft fail to start; we do not use it
!pip install -q peft==0.21.2
import glob, os
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")   # Llama is gated; never paste the token
T = os.path.dirname(glob.glob("/kaggle/input/**/train.py", recursive=True)[0])
M = "meta-llama/Llama-3.2-3B-Instruct"
print(T)
```
```python
# smoke test (interactive, ~10 min): memory, masking, NaN, seconds per step
!python {T}/train.py --model {M} --out /kaggle/working/llama_smoke --max-steps 10 --save-steps 5
```
Check: no `NaN/inf loss` line, the loss goes down, the printed "text that carries loss" is only the
assistant reply ending in `<|eot_id|>`, and note the seconds per step.
```python
# full run: "Save Version > Save & Run All" (background)
!python {T}/train.py --model {M} --out /kaggle/working/llama_lora --max-hours 11
```
Same defaults as Qwen: r 16, alpha 32, all linear layers, lr 2e-4, 1 epoch, 16 per step, 500 steps.
**Estimate:** a little under Qwen's 3.8 h, since the model is smaller (3B vs 4B). The smoke test gives the real figure.

## If something fails
- `401` / `gated repo` error: the license is not approved yet, or `HF_TOKEN` is missing or not switched on.
- `chat template is not prefix-stable`: stop and report it; do not work around it (masking would be wrong).
- NaN loss in fp16: rerun with `--precision 4bit`, and then evaluate all Llama setups with `--precision 4bit`.

## Output
`/kaggle/working/llama_lora/`: `adapter/` (stays on Kaggle, never in git), `train_meta.json`,
`log.jsonl`. Copy `train_meta.json`, `log.jsonl` and the end-of-run log into `fine_tuning/Llama/`.

## Evaluation of Llama (setups a, b, c, c_policy)
Use `kaggle/eval/run_eval_llama.py`, a copy of Marcel's `run_eval.py` (left unchanged) with one
difference: Llama writes tool calls as bare JSON (`{"name": ..., "parameters": {...}}`), not inside
`<tool_call>` tags. The original parser misses them, so Llama's tool calls would be scored as its
answer and the agent loop would never run for (a) and (b). The copy reads Llama's format; everything
else (sample, scoring, checkpoints, output files) is identical.

**Measured (2026-11-15, locally):** parser tests and one full tool round rendered with the Llama
template pass; ordinary answers, and answers that only quote JSON later on, are not treated as tool calls.

**Measured (2026-11-16):** untrained Llama repeats failing `read_document` calls and leaves ~45% of
(a)/(b) tasks unanswered unless the last round is rendered without tools, so use `--final-without-tools`
for every setup (docs/05, Llama run 1; docs/07 Q48 notes). Do not use `--tools-in-system` (worse).

Upload `run_eval_llama.py` together with the other files of `kaggle/eval/` (not `README.md`, not
`__pycache__`). Notebook: GPU **T4 x2**, Internet on, `HF_TOKEN` secret on, inputs = the eval dataset
and the Llama training notebook (for the adapter). Run cell 1 by hand (it must print two paths), then
"Save Version > Save & Run All". The cells use `subprocess` so pasting cannot break the long lines.
```python
!pip uninstall -y -q torchao
!pip install -q peft==0.21.2
import glob, os
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")   # use your secret's exact name
E = os.path.dirname(glob.glob("/kaggle/input/**/run_eval_llama.py", recursive=True)[0])
A = os.path.dirname(glob.glob("/kaggle/input/**/adapter/adapter_config.json", recursive=True)[0])
print(E); print(A)
```
```python
import subprocess   # setups a and b, one GPU each (~50 min)
procs = [
    subprocess.Popen(f"python {E}/run_eval_llama.py --setup a --final-without-tools --device cuda:0 --max-hours 5 > /kaggle/working/a.log 2>&1", shell=True),
    subprocess.Popen(f"python {E}/run_eval_llama.py --setup b --final-without-tools --device cuda:1 --max-hours 5 > /kaggle/working/b.log 2>&1", shell=True),
]
print([p.wait() for p in procs])   # [0, 0] = both finished
```
```python
import subprocess   # setups c and c_policy with the adapter (~50 min)
procs = [
    subprocess.Popen(f"python {E}/run_eval_llama.py --setup c --adapter {A} --final-without-tools --device cuda:0 --max-hours 10.5 > /kaggle/working/c.log 2>&1", shell=True),
    subprocess.Popen(f"python {E}/run_eval_llama.py --setup c_policy --adapter {A} --final-without-tools --device cuda:1 --max-hours 10.5 > /kaggle/working/c_policy.log 2>&1", shell=True),
]
print([p.wait() for p in procs])
```
Defaults (`--per-cell 40`, `--seed 0`, fp16, batch 16, 2 tool rounds, 384 new tokens) equal Qwen run 1.
Outputs go to `/kaggle/working/eval_Llama-3.2-3B-Instruct_<setup>/`; `summarize.py` works on them unchanged.
