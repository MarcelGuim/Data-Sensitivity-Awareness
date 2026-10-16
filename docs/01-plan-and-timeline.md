# 01 Plan and timeline

Labels: see `AGENTS.md`.

## Fixed dates
- **Decided (course):** Presentations start Nov 25. Plan for Nov 25, the earliest slot; a later slot only adds slack.
- **Decided (course):** Final report due Dec 11.
- **Decided:** Work started Oct 15.
- **Open:** Assigned presentation slot, presentation length, report format and length requirements (docs/07, Q18).

## Task groups
- **Proposed:** Three task groups, not assigned to people. Each person will choose one. **Open:** who takes which (docs/07, Q3).

### Group A: Data and ground truth (heaviest weeks 1 to 3, then error analysis)
- **Proposed:** Draft the four tier criteria and authorization levels, including hard "combination" cases.
- **Proposed:** Generate about 8 synthetic companies with tiered files; canary strings and fact markers in every sensitive item.
- **Proposed:** Write benign tasks and requests from authorized and unauthorized requesters.
- **Proposed:** Write injection task sets labelled by attack family.
- **Proposed:** Lead manual validation (all items in held-out companies, a sample of the rest).
- **Proposed:** Convert the frozen data to training format; document the dataset for the report.

### Group B: Agent and attacks (steady load, weeks 1 to 4)
- **Proposed:** Build the agent: model inference, tools for reading and searching company data, system prompt and policy variants, logging of every run.
- **Proposed:** Build the attack library: direct injections; indirect injections via emails, documents and tool output; the adaptive attacker (paraphrase, encoding, summarization).
- **Proposed:** Split attack families into train and held-out.
- **Proposed:** Run baselines (a) and (b); run adaptive attacks against (b) and later (c).
- **Proposed:** Keep the harness independent of the inference stack (same code on laptops and the GPU machine); handle each model's chat template and tool-call format.

### Group C: Training and evaluation (light in week 1, heaviest weeks 3 and 4)
- **Proposed:** Define metrics: leakage by tier, over-refusal, utility on benign tasks, confidence intervals.
- **Proposed:** Run the screening test on both candidate models, confirm them, settle GPU access.
- **Proposed:** Write the PyTorch/TRL/PEFT QLoRA training script; debug the data, template and masking logic on a tiny model, then a short QLoRA smoke test on Kaggle (docs/07, Q28).
- **Proposed:** Train both models with the same script, with checkpoints; retrain if adaptive attacks expose a weakness.
- **Proposed:** Evaluate (c) on the held-out company and held-out attack families; produce results tables and figures.
- **Proposed:** Stretch: one ~8B model in week 5 if the Nov 11 gate is green and budget allows.

## Shared work (all three)
- **Proposed:** Tier-criteria sign-off, week 1.
- **Proposed:** Manual dataset validation, weeks 2 to 3. Split the held-out companies three ways; a second person checks the hard, judgment-labelled cases.
- **Proposed:** Results review on Nov 11.
- **Proposed:** Report and presentation: sections drafted from week 4; slides done Nov 23; complete report draft Dec 2; final report Dec 11. One person merges and edits the report for a single voice. **Open:** who (docs/07, Q3).
- **Proposed:** A short (~30-minute) sync at each gate.

## Timeline
**Proposed** as a whole (the course dates and the Nov 11 go/no-go on the larger model are Decided).

| Week | Group A: Data | Group B: Agent and attacks | Group C: Training and evaluation | Gate at end of week |
|---|---|---|---|---|
| 1: Oct 15–21 | Tier criteria, authorization levels, hard cases; dataset schema; one pilot company | Agent skeleton (data-access tools, policy prompt, logging); first direct and indirect injections | Metrics; screening test on both models; settle GPU path; training environment | Criteria signed off by all three; models confirmed; GPU path confirmed (Oct 21) |
| 2: Oct 22–28 | Generate all companies; validate held-out companies fully and a sample of the rest; benign tasks and authorization cases | Attack library v1 (train and held-out families); agent end to end; first baselines (a) and (b) on both models | Metrics and statistics code; training script debugged on a tiny model | **Baselines (a) and (b) have numbers and show headroom (Oct 28)** |
| 3: Oct 29–Nov 4 | Finish validation; freeze data; build training files; dataset description | Adaptive attacker against (b); freeze attack sets; re-run baselines on final data | First real training run on the GPU (Qwen); check training damage on benign tasks; evaluate first checkpoint | Data and attacks frozen; a trained checkpoint exists (Nov 4) |
| 4: Nov 5–11 | Error analysis (which tiers and cases fail); draft data and tier sections | All three setups on Kaggle with the training stack, for both models; adaptive attacks against the trained model; draft agent and attack sections | Train Llama with the same script; main runs, retrain if needed; held-out and utility evaluation; tables and figures; draft training and results sections | First full results for both models; go or no-go on the larger model (Nov 11) |
| 5: Nov 12–18 (only buffer) | Fix gaps; finalize dataset description; slide skeleton | Re-run attacks if data or model changed; larger-model attack runs if it goes ahead; slide skeleton | Retrain or re-evaluate if needed; larger model (~8B) if it goes ahead; slide skeleton | **Results frozen (Nov 18)**; no new experiments after this unless something is broken |
| 6: Nov 19–25 | Final results into data slides; rehearse | Final results into agent and attack slides; rehearse | Final results into training and results slides; rehearse | Slides done Nov 23; dry run Nov 24; presentations start Nov 25 |
| 7: Nov 26–Dec 2 | Finish data and tier report sections with presentation feedback | Finish agent and attack sections | Finish training and results sections | Complete draft report (Dec 2) |
| Dec 3–11 | Final read-through | Final read-through | Final read-through; submit | Final report submitted (due Dec 11) |

- **Decided:** The professor suggested four weeks plus one buffer week. This plan has core work in weeks 1 to 4 and a single buffer in week 5.
- **Open:** Dry run on Nov 24 not yet booked (docs/07, Q3).
- **Open:** What "show headroom" at the Oct 28 gate means numerically (docs/07, Q5).

## Critical path and dependencies
- **Proposed:** Model choice (C) → agent (B), week 1.
- **Proposed:** Validated data (A) → baselines (B), week 2.
- **Proposed:** Frozen data (A) and GPU access (C) → first training run, week 3.
- **Proposed:** Frozen attack families (B) → held-out evaluation (C), week 3. The trained model must never see held-out attack families.
- **Proposed:** Critical path: data validation → baselines → data freeze → training → evaluation. The week 2 baseline gate decides whether training goes ahead.
- **Proposed:** One model end to end first (Qwen, week 3), then Llama through the same script (week 4). Do not debug both models in parallel.

## Risks and responses
- **Proposed:** Policy prompt alone blocks nearly everything ((b) near 0% leakage) → harder attacks, or a smaller or weaker base model, decided at the week 2 gate.
- **Proposed:** Model ignores the policy ((b) leaks as much as (a)) → switch model before anything is trained.
- **Proposed:** No GPU access → Kaggle first, rent if it fails (Decided 2026-10-16).
- **Proposed:** Data validation runs long → cut the number of companies, never the validation of the held-out ones.
- **Proposed:** Adaptive attacks break the trained model → retrain in week 4 or 5 and report the failure honestly, as the proposal promises.
- **Proposed:** Kaggle quota or session limits block a run → spread jobs across the three accounts; rent as fallback (Decided 2026-10-16).

## Cut order if behind
**Proposed:**
1. The larger model.
2. Extra tuning and retrain runs on the second model (it keeps one full run).
3. Adaptive attacks down to one type.
4. Number of companies.

Never cut the held-out evaluation or the utility measurements.

## Effort of using two models
- **Estimate:** Data: about no extra work. Agent and attacks: about 10–15% more (per-model chat template and tool-call format; baselines are inference only). Training and evaluation: close to double. Overall about 20–30% more effort, concentrated in weeks 3 and 4 on Group C.
- **Proposed:** Two models do not establish generality by themselves. Believability comes mainly from enough samples for confidence intervals, held-out attack families and the utility measurements. Do not let the second model take time from those.
