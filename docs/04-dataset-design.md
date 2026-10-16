# 04 Dataset design

Labels: see `AGENTS.md`.

## Sensitivity tiers
- **Decided:** Four tiers: public, internal, confidential, highly confidential.
- **Decided:** Examples: office map → public; client list → confidential; unreleased product schematics → highly confidential.
- **Decided:** Write criteria for each tier, including hard cases where individually harmless facts reveal something sensitive when combined.
- **Proposed:** The tier criteria are the foundation and the hardest part, especially the combination cases. They were not a task in the original plan and now are (Group A, signed off by all three in week 1).
- **Open:** The criteria themselves (not written yet; docs/07, Q4).
- **Open:** How a combination case is labelled and scored (which tier the combination gets, and whether disclosing one part counts as a leak) (docs/07, Q4).

## Authorization levels
- **Proposed:** Requesters have different authorization levels, so confidential data is correctly disclosed to an authorized requester and withheld from an unauthorized one. Reason: if every training example is "refuse non-public data", the model learns to refuse everything, and over-refusal looks like protection.
- **Proposed:** The utility metric includes these authorized-disclosure cases.
- **Open:** How many authorization levels, how they map to tiers, and how the requester's identity is conveyed to the agent (system prompt, tool, metadata) (docs/07, Q10).

## Canaries and fact markers
- **Decided:** Plant canary strings in sensitive items so leakage is detected automatically.
- **Proposed:** Also plant distinctive facts (unusual names, specific numbers) in every sensitive item, because canaries only catch verbatim leaks; paraphrased, summarized or encoded leaks would show 0%.
- **Open:** Canary format and how many per item; whether public/internal items get markers too (docs/07, Q11).

## Companies
- **Decided:** Synthetic company data generated with an LLM.
- **Proposed:** About 8 companies, 2 held out for testing and fully validated, the rest sample-validated. Reason: five companies (the original plan) is thin for a split.
- **Open:** The proposal and Group C task speak of "the held-out company" (singular); the gap analysis proposes 2. Which? (docs/07, Q12)
- **Decided:** Held-out evaluation uses a company *and data domain* not seen in training. **Open:** which domains (industries) the companies cover (docs/07, Q12).
- **Open:** Which LLM generates the data, and the generation prompts (docs/07, Q13).
- **Open:** Dataset schema and file types per company (emails, documents, records, ...) (docs/07, Q14). A schema is a week 1 Group A deliverable.
- **Open:** Dataset size (items per company, training examples) (docs/07, Q5).

## Task types
- **Proposed:** Benign tasks (normal, non-sensitive work) for utility.
- **Proposed:** Requests from authorized and unauthorized requesters.
- **Proposed:** Injection tasks, labelled by attack family.
- **Open:** Ratio of benign / authorized / unauthorized / injection examples in training and evaluation (docs/07, Q5).

## Attack families
- **Decided:** Prompt injections that try to extract the data, including, if possible, an adaptive attacker that targets the defence (paraphrasing, encoding, summarizing).
- **Proposed:** Direct injections; indirect injections via emails, documents and tool output.
- **Proposed:** Hold out whole attack families, in addition to holding out companies. Example split: train on direct and email-embedded injections; test on paraphrased, encoded and multi-step ones.
- **Proposed:** Train and held-out families are split and frozen by Group B in week 3; the trained model never sees held-out families.
- **Open:** Final list of families and the split (docs/07, Q6).
- **Open:** How the adaptive attacker is implemented (manual, scripted, or an attacker LLM) (docs/07, Q15).

## Validation
- **Decided:** Manually validate against the criteria: every item in the evaluation set and a sample of the training set.
- **Proposed:** All items in the held-out companies; a sample of the rest. Split the held-out companies three ways; a second person checks the hard, judgment-labelled cases.
- **Proposed:** Manual validation is the bottleneck. If it runs long, cut the number of companies, never the validation of the held-out ones.
- **Open:** Sample size for training-set validation, and how disagreements between validators are resolved (docs/07, Q5).

## Training format
- **Proposed:** Group A converts the frozen data to training format (chat format with assistant-only loss; see `06-training-plan.md`).
- **Open:** Exact format (docs/07, Q14).
