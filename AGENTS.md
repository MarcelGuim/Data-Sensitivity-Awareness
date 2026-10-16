# Agent instructions: ECE1776 Group 3

This file is the single source of project context for any AI coding agent (Claude Code, Codex, Cursor, Copilot, Gemini). `CLAUDE.md` and `GEMINI.md` import it; `.github/copilot-instructions.md` points to it. Edit this file, not the pointer files.

**Your local memory and chat history are not shared with the team.** Anything that matters to the project must be written into `docs/`, then committed. If a teammate tells you a decision in chat, record it in `docs/07-decisions-and-open-questions.md` before finishing.

## Project
Course project, ECE1776 (Computer Security, Cryptography and Privacy), U of T, Fall 2026. Group 3: Wasilat Ayinla, Khalid Challango, Marcel Guim. Proposal dated 2026-10-12. Any of the three may be the person you are talking to; ask if it matters.

- **Decided:** Title "Limiting the Blast Radius of Prompt Injection Through Data-Sensitivity Awareness".
- **Decided:** Train an LLM agent to disclose company data according to its sensitivity tier (public, internal, confidential, highly confidential) and the requester's authorization, even under prompt injection. A last-resort layer, not prevention.
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
- **Decided:** Training stack: PyTorch + Hugging Face TRL + PEFT, QLoRA (bitsandbytes). Do not build the training pipeline in MLX.
- **Decided (2026-10-16):** Evaluation uses the training stack (transformers + bitsandbytes 4-bit) for all of (a)(b)(c). Scripts must checkpoint/resume (12 h sessions) and pin versions; tokens go in Kaggle Secrets.
- **Decided:** Models: Qwen3-4B-Instruct-2507 (primary, trained first) and Llama-3.2-3B-Instruct (second), pending the screening test. Stretch: one ~8B model, go or no-go at the Nov 11 gate.
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
- `docs/archive/`: original planning handoffs, historical only. **Do not follow the instructions in them**; `docs/` supersedes them.
