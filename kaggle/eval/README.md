# Evaluation of setups (a), (b), (c) on Kaggle

Held-out evaluation (docs/05): 20 held-out companies (finance, healthcare), all 8 families
including the held-out ones (indirect via document, encoding). By default a stratified sample of
40 tasks per (family, tier, requester level) cell: 2,880 of the 12,960 tasks, the same sample for
every setup (`--per-cell 0` runs all). Greedy decoding, scored with `score.py` (decode, normalize,
match canaries and markers).

Agent loop: if the model calls `read_email` or `read_document`, it gets a result and answers again
(up to 2 tool results). Its own email or document returns that content; anything else returns
"not found". Without this, the untrained model's tool calls (36% of replies in the first smoke
test) ended the conversation and were scored as neither leak nor disclosure, which would favour
the trained model. Only the text the requester would see is scored.

**Measured (2026-11-09, T4, smoke test without the tool loop):** 0.21 tasks/s, so all 12,960 tasks
would take about 17 h per setup. With the sample: about 4–5 h per setup (Estimate; the tool loop adds
a second round for some tasks).

## Files
| file | what |
|---|---|
| `run_eval.py` | generates and scores one setup; checkpoints after every batch |
| `summarize.py` | compares setups: leak rate by family, tier, level, mismatch; utility; Wilson 95% intervals |
| `score.py` | copy of `scripts/dataset/score.py` (do not edit here) |
| `eval_tasks.jsonl`, `items.json` | built by `python3 scripts/prepare_kaggle.py` (not in git; rebuild after any data change) |

## One-time setup
1. Locally: `python3 scripts/dataset/build_tasks.py --data data/full && python3 scripts/prepare_kaggle.py`.
2. kaggle.com > Datasets > New Dataset > upload the files of this folder. Name it e.g. `ece1776-eval`.
   After any change to code or data, upload a new version of the same dataset.
3. New notebook > Add Input > your dataset. Settings: Accelerator **GPU T4**, Internet **on**.

## Notebook cells
```python
# 1. find the folder (the mount path differs between Kaggle versions)
import glob, os
E = os.path.dirname(glob.glob("/kaggle/input/**/run_eval.py", recursive=True)[0])   # folder that holds run_eval.py
print(E)
```
```python
# 2. smoke test (interactive session, ~6 min): prints tasks/s and ETA
!python {E}/run_eval.py --setup a --limit 64 --out /kaggle/working/smoke_eval2
```
```python
# 3. one setup per version: "Save Version > Save & Run All" (background, max 12 h per session)
#    --max-hours: the script stops itself, scores what it has and exits normally, so Kaggle keeps the output.
!python {E}/run_eval.py --setup a --max-hours 5.5
!python {E}/run_eval.py --setup b --max-hours 5.5
!python {E}/summarize.py /kaggle/working/eval_*/scored.jsonl --csv /kaggle/working/results_ab.csv
```
With two T4s, run (a) and (b) in the same version, one per GPU (about 4–5 h instead of 9–10 h; Estimate):
```python
!python {E}/run_eval.py --setup a --device cuda:0 --max-hours 10.5 > /kaggle/working/a.log 2>&1 & python {E}/run_eval.py --setup b --device cuda:1 --max-hours 10.5 > /kaggle/working/b.log 2>&1 & wait
!tail -n 60 /kaggle/working/a.log /kaggle/working/b.log
```
Use the same `--per-cell` and `--seed` for every setup you compare (the defaults, 40 and 0).
Replies from the first harness (no tool loop) are ignored on resume.

## Setup (c), after training
Add the training notebook's output as an input (Add Input > Notebook Output), then:
```python
A = "/kaggle/input/<training-notebook>/qwen_lora/adapter"   # find it with !find /kaggle/input -name adapter_config.json
!pip uninstall -y -q torchao   # Kaggle's torchao 0.10 makes recent peft fail to start (ImportError); we do not use it
!pip install -q peft==0.21.2
!python {E}/run_eval.py --setup c --adapter {A} --max-hours 10
```
Then a new version with `--setup c_policy`, or both in one version, one per T4 (logs go to files, not the cell):
```python
!python {E}/run_eval.py --setup c --adapter {A} --device cuda:0 --max-hours 10 > /kaggle/working/c.log 2>&1 & python {E}/run_eval.py --setup c_policy --adapter {A} --device cuda:1 --max-hours 10 > /kaggle/working/c_policy.log 2>&1 & wait
!tail -n 40 /kaggle/working/c.log /kaggle/working/c_policy.log
```
`c` = trained model, task prompt only; `c_policy` = trained model plus the (b) policy text (docs/07 Q24).

## Comparing (a), (b), (c), c_policy
Download each version's `eval_*` folder (Output tab) into `results/` in the repo, then locally
(standard library only, no GPU):
```
python3 kaggle/eval/summarize.py results/eval_*/scored.jsonl --csv results/results_abc.csv
```
One column per setup, Wilson 95% intervals. Read leak rate and disclosure together: lower leakage
with lower disclosure is over-refusal, not protection.

## Stopping safely (30 GPU hours per week per account)
- **Do not press Stop on a "Save & Run All" version or let the quota run out mid-run**: Kaggle saves
  `/kaggle/working` only when the version finishes, so a cancelled or killed version most likely loses
  everything it wrote (Unverified; assume it does). Use `--max-hours` instead, set to the hours you can
  spare minus ~0.5 h for model download and scoring.
- In an interactive session, files in `/kaggle/working` disappear when the session ends; download them first.
- What the code itself guarantees: replies are written after every batch of 16, so a resume repeats at most one batch.

## Resume after a cut session
Outputs live in `/kaggle/working/eval_<model>_<setup>/` and are saved with the notebook version.
In the next version, add that version's output as an input and pass
`--resume-dir /kaggle/input/<notebook>/eval_Qwen3-4B-Instruct-2507_a`. Finished tasks are skipped.

## Rules
- All setups that are compared use the same `--precision` (default fp16) and the same sample.
- The policy text for (b) is `POLICY` in `run_eval.py`. Do not change it after the first (b) numbers.
- Paraphrase and summary leak rates are lower bounds: exact matching misses a leak that drops every exact value (judge pending, docs/07 Q25).
- Bring the `eval_*` folders back into `results/` in the repo (replies and scored files, no weights).
