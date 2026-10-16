# Results

Labels: see `AGENTS.md`. Screening runs only; these are **not** reportable results (docs/03, docs/05). Analysis is in `docs/03-models.md`; summary in `docs/08-findings-summary.md`.

All runs: Kaggle T4, `scripts/screen_models.py`, transformers + bitsandbytes 4-bit, run by Marcel on 2026-10-16. Each `outputs.jsonl` holds one JSON record per generation (model, condition, prompt, sample index, response text, detector fields).

| folder | model | script version | conditions | prompts | N per cell | records |
|---|---|---|---|---|---|---|
| `screening/v1_qwen/` | Qwen3-4B-Instruct-2507 | v1 | no_policy, policy_external, policy_employee | 4 | 5 | 60 |
| `screening/v2_qwen/` | Qwen3-4B-Instruct-2507 | v2 | same 3 | 12 | 20 | 720 |
| `screening/v2_llama/` | Llama-3.2-3B-Instruct | v2 | same 3 | 12 | 20 | 720 |
| `screening/v2_llama_rerun/` | Llama-3.2-3B-Instruct | v2 defaults | same 3 | 12 | 20 | 720 |
| `screening/v_prompt_optimization/` | Llama-3.2-3B-Instruct | v3 | policy_external, policy_employee, opt_external, opt_employee | 18 (12 + 6 held-out) | 20 | 1,440 |

- `v2_llama_rerun` was meant to be the prompt-optimization run, but the notebook ran without the new settings. Its text is identical to `v2_llama`, which shows the runs are reproducible.
- Pending: Qwen prompt-optimization run (save as `screening/v_prompt_optimization_qwen/`).
