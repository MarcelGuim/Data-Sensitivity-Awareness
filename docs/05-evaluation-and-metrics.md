# 05 Evaluation and metrics

Labels: see `AGENTS.md`.

- **Proposed:** Metrics must be defined before the dataset, because they decide what the data must contain.

## Setups
- **Decided:** (a) untrained model, no protection.
- **Decided:** (b) untrained model with a system prompt stating the sensitivity policy.
- **Decided:** (c) model trained on sensitivity-labelled data, in the style of instruction-hierarchy training.
- **Open:** Whether (c) is evaluated with or without the policy system prompt (or both) (docs/07, Q24).
- **Decided (2026-10-16):** All final numbers for (a), (b), (c), both models, come from Kaggle with the training stack. **Proposed (2026-11-09):** fp16 for all setups, following the switch to LoRA (docs/07, Q48). Code: `kaggle/eval/`. Laptop numbers are never reported. **Proposed:** week 2 baselines are headroom checks; final numbers in week 4 on frozen data.

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

## Results, run 1 (2026-11-10)
- **Measured (2026-11-10, Kaggle T4 x2, fp16, greedy, stratified sample of 2,880 held-out tasks, same sample for every setup; files in `results/eval_run1/`):**

| metric | (a) untrained | (b) + policy prompt | (c) trained | (c) + policy |
|---|---|---|---|---|
| Leak rate, restricted target (n=960) | 76.0% [73.2, 78.6] | 52.9% [49.8, 56.1] | 0.0% [0.0, 0.4] | 0.0% [0.0, 0.4] |
| Disclosure to authorized requester (n=1,440) | 63% (confidential 35%) | 64% (confidential 34%) | 100% | 100% |
| Indirect task done, email (n=360) | 82.2% | 80.3% | 98.9% | 98.9% |
| Refusals naming a tier word (n=720) | 16.5% | 56.1% | 0.0% | 0.0% |
| Called a tool | 30.1% | 12.2% | 0.0% | 0.0% |

- **Measured:** (c) leaks in no family, including the held-out ones (encoding, indirect document); (b) still leaks 44–89% per family outside the indirect ones. (c)'s 240 paraphrase/summary non-matches were checked: all are one of two templated refusals (at most 184 characters), so no reworded leak hides there. (c) and (c)+policy give identical metrics (1,838 of 2,880 replies identical word for word).
- **Proposed (interpretation, not yet agreed):** the result is at ceiling. The held-out split changes companies, sectors, wordings and two attack families, but the prompt format, tag format and attack generator are the same as in training, and the decision can be read from the prompt (tag + requester level). This shows the model learned the rule for this format; it does not show robustness to formats or attacks outside our generator. An out-of-distribution test is needed before claiming more (docs/07 Q49).
