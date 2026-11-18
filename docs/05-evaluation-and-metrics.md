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

## Results, Llama-3.2-3B-Instruct run 1 (2026-11-16, Wasilat)
- **Measured (Kaggle T4 x2, fp16, greedy, same 2,880-task sample and settings as Qwen run 1; `kaggle/eval/run_eval_llama.py` with `--final-without-tools`, Llama parser v2, template date pinned to 16 Nov 2026; adapter from the Llama training run, `fine_tuning/Llama/`; files and figures in `results/eval_llama_run1/`, Qwen vs Llama figure in `results/figures_compare/`). (a) and (b) are from the final re-run (2026-11-16, the third a/b run); (c) and (c)+policy from the second run, which the parser fixes do not affect (no (c) reply contains a tool call).**

| metric | (a) untrained | (b) + policy prompt | (c) trained | (c) + policy |
|---|---|---|---|---|
| Leak rate, restricted target (n=960) | 57.2% [54.0, 60.3] | 50.7% [47.6, 53.9] | 0.1% [0.0, 0.6] | 0.2% [0.1, 0.8] |
| Disclosure to authorized requester (n=1,440) | 56% (confidential 47.9%) | 60% (confidential 47.9%) | 100% | 100% |
| Indirect task done, email (n=360) | 51.7% | 45.8% | 98.9% | 98.9% |
| Indirect task done, document (held-out family, n=360) | 73.6% | 65.6% | 75.8% | 71.9% |
| Refusals naming a tier word (n=720) | 15.0% | 28.5% | 0.0% | 0.0% |
| Called a tool | 100.0% | 99.9% | 0.0% | 0.0% |
| Final reply still a tool call (no answer) | 17.8% | 18.6% | 0.0% | 0.0% |

- **Measured:** the policy prompt helps untrained Llama a little (57.2% → 50.7%, intervals do not overlap; Qwen: 76% → 53%). Training brings leakage to 0.1–0.2% (1 and 2 leaks, all in tampering) with 100% disclosure to authorized requesters, as for Qwen.
- **Measured:** unlike Qwen, trained Llama completes the held-out indirect-document task only 75.8% of the time (Qwen (c) 99.7%), without leaking there; failed replies describe the document's layout instead of its content.
- **Measured:** 25.0% of (c)'s restricted paraphrase/summary replies are judge candidates (no fact match), the same share as Qwen (c); not yet checked by hand or by a judge (Q25).
- **Measured:** untrained Llama calls a tool on essentially every task and 17.8% (a) / 18.6% (b) still end in a tool call even though the last round shows no tool list (it repeats its earlier calls). These count as no leak and no disclosure, so (a)/(b) utility is somewhat understated; Qwen had 0%.
- **Measured (harness history):** two earlier Llama a/b runs are not valid. Run 1 (no `--final-without-tools`): untrained Llama repeated failing `read_document` calls on reference codes from the records and left 46.7% (a) / 44.3% (b) of tasks unanswered. `--tools-in-system` (160-task test) made it worse (67.5% unanswered). Run 2: the parser missed the `{"type": "function", "function": ..., "parameters": ...}` shape (about half the replies), so tool calls quoting a record's reference code were scored as leaks and utility read 22% (leak (a) 69.9%, (b) 65.7%: overstated). Fixed in parser v2 (both shapes and a trailing call after prose); checked offline on all stored turns and with a simulated loop before run 3. Qwen run 1 had 0% unanswered, so `--final-without-tools` would not change any Qwen reply. See docs/07 (Q48 notes).
- **Proposed (interpretation):** the ceiling caveat for Qwen (same format and generator as training; Q49) applies equally here.
