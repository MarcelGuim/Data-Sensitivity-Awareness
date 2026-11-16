# LoRA training of Qwen3-4B-Instruct-2507 for setup (c), on Kaggle

## Files
| file | what |
|---|---|
| `train.py` | LoRA (fp16) or QLoRA (`--precision 4bit`) training; loss on the final assistant reply only; checkpoints every 25 steps |
| `train.jsonl` | 8,000 training conversations with target replies, built by `python3 scripts/prepare_kaggle.py` (not in git) |
| `build_info.json` | counts, seed, excluded companies, hash of the source tasks |

Training data: train split only (80 companies, 8 sectors, train wordings, train families). The
build script and `train.py` both stop if anything held out appears. Mix (Proposed): 40% share,
40% refuse over benign, direct, tampering, paraphrase, summary; 20% indirect email (do the task,
ignore the injection).

**Before the real run:** if a teammate's validation failed a company, rebuild without it:
`python3 scripts/prepare_kaggle.py --exclude company_a,company_b`, then upload a new dataset version.

## One-time setup
1. kaggle.com > Datasets > New Dataset > upload the files of this folder, e.g. `ece1776-train-qwen`.
2. New notebook > Add Input > that dataset. Settings: Accelerator **GPU T4**, Internet **on**.

## Notebook cells
```python
!pip uninstall -y -q torchao   # Kaggle's torchao 0.10 makes recent peft fail to start (ImportError); we do not use it
!pip install -q peft==0.21.2
import glob, os
T = os.path.dirname(glob.glob("/kaggle/input/**/train.py", recursive=True)[0])   # folder that holds train.py
print(T)
```
```python
# smoke test (interactive, ~10 min): checks memory, masking and NaN; prints the text that carries loss and s/step
!python {T}/train.py --max-steps 10 --save-steps 5 --out /kaggle/working/smoke
```
```python
# full run: "Save Version > Save & Run All" (background, max 12 h per session)
# --max-hours: saves a checkpoint and exits normally at that time, so Kaggle keeps the output
!python {T}/train.py --max-hours 6
```
Defaults (Proposed, docs/07 Q26): r 16, alpha 32, all linear layers, dropout 0.05, lr 2e-4,
cosine, 1 epoch, batch 2 x 8 accumulation = 16 per step, 500 steps, max length 2048.

## Output
`/kaggle/working/qwen_lora/`: `adapter/` (LoRA weights for setup c), `train_meta.json`
(versions, data hash, loss, hours), `log.jsonl` (loss per 5 steps), `checkpoints/`.
At the end it prints three training conversations with the target and the trained model's reply.
Do not commit the adapter or checkpoints (`.gitignore`); copy `train_meta.json` and `log.jsonl` into `results/`.

## Stopping safely (30 GPU hours per week per account)
- **Do not press Stop on a "Save & Run All" version or let the quota run out mid-run**: Kaggle saves
  `/kaggle/working` only when the version finishes, so the checkpoints would most likely be lost
  (Unverified; assume they are). Use `--max-hours` instead.
- Checkpoints are also saved every 25 steps, so if a session dies anyway in an interactive run where
  you downloaded `/kaggle/working/qwen_lora/checkpoints`, you lose at most 25 steps.
- No `adapter/` is written until all steps are done; a time-limited run leaves only checkpoints.

## Resume after a cut session
Add the cut version's output as an input and run
`!python {T}/train.py --resume-dir /kaggle/input/<notebook>/qwen_lora` with the same other arguments.

## If something fails
- Out of memory: `--batch-size 1 --grad-accum 16`; still OOM: `--precision 4bit` (QLoRA).
- NaN or inf loss (fp16 overflow): the script stops. Rerun with `--precision 4bit` or `--lr 1e-4`.
- If you switch to 4bit, evaluate (a), (b) and (c) all with `--precision 4bit` too.
