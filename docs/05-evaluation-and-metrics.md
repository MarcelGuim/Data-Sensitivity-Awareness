# 05 Evaluation and metrics

Labels: see `AGENTS.md`.

- **Proposed:** Metrics must be defined before the dataset, because they decide what the data must contain.

## Setups
- **Decided:** (a) untrained model, no protection.
- **Decided:** (b) untrained model with a system prompt stating the sensitivity policy.
- **Decided:** (c) model trained on sensitivity-labelled data, in the style of instruction-hierarchy training.
- **Open:** Whether (c) is evaluated with or without the policy system prompt (or both) (docs/07, Q24).
- **Decided (2026-10-16):** All final numbers for (a), (b), (c), both models, come from Kaggle with the training stack (transformers + bitsandbytes 4-bit). Laptop numbers are never reported. **Proposed:** week 2 baselines are headroom checks; final numbers in week 4 on frozen data.

## Metrics
- **Decided:** Leakage rate by tier.
- **Decided:** Utility on normal, non-sensitive tasks (cost of protection; detects training damage).
- **Proposed:** Over-refusal, including withholding data from an authorized requester.
- **Proposed:** Utility includes the authorized-disclosure cases.
- **Proposed:** Confidence intervals on reported rates.
- **Open:** How utility is scored (exact match, rubric, LLM judge) and whether any standard benchmark is used as a damage check (docs/07, Q25).

## Leakage detectors
- **Decided:** Canary matching (automatic, catches verbatim leaks).
- **Proposed:** A second detector: fact matching on planted distinctive facts, or an LLM judge spot-checked by hand. Needed because canaries miss paraphrased, summarized or encoded leaks.
- **Proposed:** Known issue from the screening script: matching names and numbers flags refusals that mention them ("I can't share the Northwind contract") as leaks. Read samples by eye.
- **Decided (2026-10-28, Marcel):** Leak detection in three steps: (1) decode the output (base64, hex, rot13, ...) before matching; (2) normalize (number words to digits, spacing, punctuation) before matching canaries and markers; (3) an LLM judge only on a subset, mainly paraphrase and summarization outputs that steps 1–2 mark as safe, with a hand-checked sample to report its error rate.
- **Proposed:** The judge comes from a different family than the generator (Claude) and the evaluated models (Qwen, Llama).
- **Open:** Which judge model, the judge prompt, the subset size and how many verdicts are hand-checked (docs/07, Q25).

## Statistics
- **Open:** Number of samples per evaluation cell, decoding settings (temperature), and which statistics and intervals to report. Never specified (docs/07, Q5).
- **Open:** Numeric threshold for "headroom" at the Oct 28 gate (docs/07, Q5).

## Held-out tests
- **Decided:** Held-out company and data domain not seen in training.
- **Decided (2026-10-28, Marcel):** Held-out attack families: indirect via document, encoding. 20 held-out companies from unseen sectors (see `04-dataset-design.md`).
- **Proposed:** Adaptive attacks against (b), then against (c).
- **Proposed:** Never cut the held-out evaluation or the utility measurements.

## Results artifacts
- **Proposed:** Tables and figures by Group C in week 4; error analysis by tier and case by Group A in week 4.
