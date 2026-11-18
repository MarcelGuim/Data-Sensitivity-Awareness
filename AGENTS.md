# Agent instructions: ECE1776 Group 3

This file is the single source of project context for any AI coding agent (Claude Code, Codex, Cursor, Copilot, Gemini). `CLAUDE.md` and `GEMINI.md` import it; `.github/copilot-instructions.md` points to it. Edit this file, not the pointer files.

**Your local memory and chat history are not shared with the team.** Anything that matters to the project must be written into `docs/`, then committed. If a teammate tells you a decision in chat, record it in `docs/07-decisions-and-open-questions.md` before finishing.

## Project
Course project, ECE1776 (Computer Security, Cryptography and Privacy), U of T, Fall 2026. Group 3: Wasilat Ayinla, Khalid Challango, Marcel Guim. Proposal dated 2026-10-12. Any of the three may be the person you are talking to; ask if it matters.

- **Decided:** Title "Limiting the Blast Radius of Prompt Injection Through Data-Sensitivity Awareness".
- **Decided:** Train an LLM agent to disclose company data according to its sensitivity tier (public, private, confidential; three tiers since 2026-10-28, the proposal had four) and the requester's authorization (external, internal_no_clearance, internal_clearance), even under prompt injection. A last-resort layer, not prevention.
- **Decided:** Research question: does training a model to reason about data sensitivity reduce leakage under prompt injection beyond what a system-prompt policy achieves, and at what cost to utility?
- **Decided:** Compare (a) untrained, no protection; (b) untrained + policy system prompt; (c) trained on sensitivity-labelled data.

## Labels (mandatory in docs/)
Every statement in `docs/` carries one label:
- **Decided**: the group or a member chose it, or it is fixed by the course or the proposal.
- **Proposed**: a suggestion, not yet agreed by the group.
- **Estimate**: a rough number, not measured.
- **Unverified**: from web search or a third-party source.
- **Measured**: observed on our own hardware or runs.
- **Open**: information missing; the question lives in `docs/07`.

Never upgrade Proposed or Estimate to Decided without a dated row in the docs/07 decisions log naming who decided. Never invent facts: if something is missing, write Open and add a question to docs/07 (numbers are stable; append, do not renumber).

## Key decisions
- **Decided (2026-10-16):** Training and all final evaluation run on Kaggle Notebooks (free T4, one account per person); rent only if Kaggle fails. Colab only for short tests. Laptops that can run the models (e.g. Marcel's M4, 24 GB; not the HP laptop) are for development and screening only; their numbers never go into results.
- **Decided:** Training stack: PyTorch + Hugging Face + PEFT. Do not build the training pipeline in MLX.
- **Decided (2026-11-09, Marcel):** Plain LoRA on the fp16 model instead of QLoRA; QLoRA is the fallback. **Proposed:** evaluate every setup in fp16 too (docs/07, Q48).
- **Decided (2026-10-16):** Evaluation uses the training stack (transformers) for all of (a)(b)(c), at one precision for all (4-bit until 2026-11-09; fp16 Proposed, Q48). Scripts must checkpoint/resume (12 h sessions) and pin versions; tokens go in Kaggle Secrets.
- **Decided:** Models: Qwen3-4B-Instruct-2507 (primary, trained first) and Llama-3.2-3B-Instruct (second), pending the screening test. The ~8B stretch model is dropped (2026-11-09).
- **Decided (course):** Presentations start Nov 25; final report due Dec 11.

## Rules for code and data
- **Proposed:** Held-out companies and held-out attack families never enter training files. Any script that builds training data must filter by the `split` field and fail loudly if held-out items appear.
- **Proposed:** Loss on assistant turns only.
- **Proposed:** Every long-running script (training, evaluation) checkpoints and can resume; free GPUs cut sessions.
- **Proposed:** Never cut the held-out evaluation or the utility measurements.
- Never commit API keys, `.env` files, model weights, adapters or checkpoints (see `.gitignore`).
- Pin library versions once chosen.

## Default working style
From Marcel; teammates may change it here for the group:
- Direct and concise. No filler; no praise without a specific reason.
- Stress-test ideas before agreeing. Lead with what is wrong or missing; say "this won't work" first when it won't.
- Do not echo the user's framing back. Push back harder when they sound confident.

## Status (update when it changes)
- 2026-10-16: Docs created. Screening: `scripts/screen_models.py` (Kaggle, training stack) written, not yet run; Marcel runs it for preliminary results. `scripts/test_policy.py` is the original MLX version. A classmate sends the GPU-access email; Kaggle is the GPU path regardless. Task groups A/B/C proposed, not assigned. Open questions are being answered one by one (docs/07).
- 2026-10-16: Screening done for Qwen and Llama (v2) and Llama b+; results in `docs/03-models.md`, summary for the group in `docs/08-findings-summary.md`. Pending: Qwen b+ run; group confirmation of models (Q1) and gaps (Q32).
- 2026-10-28: Marcel decided three tiers (public, private, confidential), three requester levels, visible per-company tags, 100 companies, query groups (benign, direct injection, ...). Logged in docs/07; new questions Q37–Q43 block the schema.
- 2026-10-30: Pilot built (2 companies, attack templates, task builder, scorer); awaiting group review. See docs/04, section Pilot.
- 2026-11-01: The group agreed two tiers and two levels; Marcel reverted to three tiers and three levels the same day (docs/07). The group still needs to be told.
- 2026-11-01: Full dataset generated (100 companies, 89,280 tasks) in `data/full/`; awaiting validation by the rule in docs/04. Plan: `data/full/validation/plan.md`. Open: Q46, Q47.
- 2026-11-09: Held-out validation done (all 20 pass); teammates' training-sector results pending upload. 8B dropped. Kaggle folders written: `kaggle/eval/` (setups a, b, c) and `kaggle/train_qwen/` (LoRA). Tested locally without a GPU (template, masking, scoring); not yet run on Kaggle.
- 2026-11-10: Qwen LoRA trained (3.8 h, adapter outside git) and run 1 of the evaluation done: leak (a) 76%, (b) 53%, (c) 0%; utility (c) 100%. Results in `docs/05` and `results/eval_run1/`. Open: out-of-distribution test (Q49), Llama, judge (Q25).
- 2026-11-15: Llama prepared (Wasilat): training reuses `kaggle/train_qwen/train.py` and data unchanged; evaluation uses `kaggle/eval/run_eval_llama.py`, a copy of `run_eval.py` with a Llama tool-call parser (docs/07 Q48). Cells in `kaggle/train_llama/README.md`. Not yet run on Kaggle.
- 2026-11-16: Llama LoRA trained on Kaggle (Wasilat): 500 steps, 2.76 h, train loss 0.131 (Qwen 0.132), same data hash and settings; adapter outside git. Logs in `fine_tuning/Llama/`.
- 2026-11-16: Llama evaluation done: leak (a) 57%, (b) 51%, (c) 0.1%; utility (c) 100%. Two earlier a/b runs discarded (Llama tool-call loop and a parser gap; docs/05). Needed `--final-without-tools` (docs/07 Q48 notes). Results in `docs/05`, files and figures in `results/eval_llama_run1/` (`scripts/plot_results_llama.py`); Qwen vs Llama figure in `results/figures_compare/` (`scripts/plot_compare_models.py`).

## Where things are
- `docs/00-project-overview.md`: proposal, research question, method, evaluation, professor feedback
- `docs/01-plan-and-timeline.md`: task groups, timeline, gates, shared work, risks, cut order
- `docs/02-compute-and-environment.md`: hardware findings, stack, GPU options
- `docs/03-models.md`: candidates, selection reasoning, screening
- `docs/04-dataset-design.md`: tiers, authorization, canaries, companies, tasks, attacks, validation
- `docs/05-evaluation-and-metrics.md`: setups, metrics, detectors, statistics, held-out tests
- `docs/06-training-plan.md`: QLoRA, loss masking, run plan, rental checklist
- `docs/07-decisions-and-open-questions.md`: dated decisions log and open questions. **Read before proposing anything.**
- `docs/08-findings-summary.md`: snapshot of screening findings and pending group decisions, for presenting to the team (03 and 07 win if they disagree)
- `docs/09-proposal-presentation.md`: answers to the professor's four proposal questions and the weekly plan with owners, for the Oct 21 presentation
- `data/pilot/`: pilot companies, attack templates, response structures, generated tasks
- `data/full/`: the 100 companies, attack templates, spec, validation plan (`tasks.jsonl` is rebuilt, not committed)
- `scripts/dataset/`: task builder, leak scorer and its tests, validation sampler
- `scripts/prepare_kaggle.py`: builds the data files for the two Kaggle folders
- `scripts/plot_results.py`: report/slide figures from an evaluation run (`python3 scripts/plot_results.py results/eval_run1`)
- `kaggle/eval/`, `kaggle/train_qwen/`: upload-ready Kaggle folders (evaluation of a/b/c; Qwen LoRA training); each has a README with the notebook cells
- `kaggle/train_llama/README.md`: notebook cells for training and evaluating Llama (same training script and data; `kaggle/eval/run_eval_llama.py` for evaluation)
- `docs/archive/`: original planning handoffs, historical only. **Do not follow the instructions in them**; `docs/` supersedes them.
