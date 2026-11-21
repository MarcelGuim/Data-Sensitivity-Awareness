# 00 Project overview

Labels: see `AGENTS.md`.

## Basics
- **Decided:** Course: ECE1776, Computer Security, Cryptography and Privacy, University of Toronto, Fall 2026.
- **Decided:** Group 3: Wasilat Ayinla, Khalid Challango, Marcel Guim. Proposal dated 2026-10-12.
- **Decided:** Title: *Limiting the Blast Radius of Prompt Injection Through Data-Sensitivity Awareness*.

## Problem
- **Decided:** Prompt injection is unsolved. Models cannot reliably separate instructions from data, and detection-based defences can be bypassed.
- **Decided:** Instead of only trying to prevent injections, limit what a successful one can disclose: the attacker may redirect the agent, but what it can reach and disclose stays contained.

## Idea
- **Decided:** Train an LLM agent to recognize how sensitive each piece of data is. Every item in a synthetic company's data carries a tier. The proposal had four (public, internal, confidential, highly confidential); **Decided (2026-10-28, Marcel):** three tiers, public, private, confidential (see `04-dataset-design.md`).
- **Decided:** Examples from the proposal: office map is public; client list is confidential; unreleased product schematics are highly confidential.
- **Decided:** The agent discloses data according to its tier and the requester's authorization, even when an injection instructs otherwise.
- **Decided:** Positioning: a different angle on instruction-hierarchy work ("The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"). Prioritize data by sensitivity rather than instructions by source. A last-resort layer that holds when other defences fail.

## Research question
- **Decided:** Does training a model to reason about data sensitivity reduce leakage under prompt injection beyond what a system-prompt policy achieves, and at what cost to utility?

## Method (from the proposal)
1. **Decided:** Write criteria for the tiers (three since 2026-10-28), including hard cases where individually harmless facts reveal something sensitive when combined.
2. **Decided:** Generate a synthetic company dataset with an LLM, then validate it manually against the criteria: every item in the evaluation set and a sample of the training set. Plant canary strings in sensitive items so leakage is detected automatically.
3. **Decided:** Build an agent with access to the data and attack it with prompt injections that try to extract it, including, if possible, an adaptive attacker that targets the defence (paraphrasing, encoding, summarizing).
4. **Decided:** Compare (a) untrained model, no protection; (b) untrained model with a system prompt stating the sensitivity policy; (c) a model trained on sensitivity-labelled data, in the style of instruction-hierarchy training.

Details and proposed changes: `04-dataset-design.md`, `05-evaluation-and-metrics.md`, `06-training-plan.md`.

## Evaluation (from the proposal)
- **Decided:** Leakage rate by tier, detected by canary matching.
- **Decided:** Utility on normal, non-sensitive tasks, to show the cost of protection and detect training damage.
- **Decided:** Held-out evaluation on a company and data domain not seen in training, to check the model learned the policy rather than memorizing examples.

## Contribution and expected outcome
- **Decided:** Contribution: a tiered sensitivity dataset, an evaluation of whether learned sensitivity holds up against adaptive injection, and an honest account of where it fails.
- **Decided:** Expected outcome (hypothesis, not a result): sensitivity-trained models leak less under prompt injection than models relying on system-prompt policies alone, including under adaptive attacks, generalize to unseen data domains, and keep reasonable performance on legitimate tasks.

## Professor's feedback
**Decided (course feedback; exact text supplied by Marcel, 2026-11-20):** "This is interesting and related to Data Loss Prevention solutions, though these usually do not consider an LLM IPI scenario. The only thought is that LLM training/fine-tuning requires a reasonably powered GPU and you'd need to evaluate on a smaller model in any case that may not be previously trained to understand tags anyways. Some careful thought and identification of reasonable models that can fit on your hardware is recommended."

Earlier paraphrase from the planning chat (superseded by the text above):
- Related to Data Loss Prevention (DLP) solutions, which usually do not consider an LLM indirect-prompt-injection (IPI) scenario.
- Fine-tuning needs a reasonably powered GPU.
- The evaluation should use a smaller model that may not have been trained to understand tags anyway (kickoff wording); "a small model may not already understand tags" (older handoff wording).
- Identify reasonable models that fit the available hardware.
- Suggested budgeting four weeks plus one buffer week (see `01-plan-and-timeline.md`).

How the feedback is addressed:
- **Decided (2026-10-16):** GPU: train and evaluate on Kaggle (free T4); rent only if it fails (`02-compute-and-environment.md`).
- **Decided:** Models: 3B/4B instruct models, with screening (`03-models.md`).
- **Open:** How the report will position the work against DLP (no plan written yet; docs/07, Q17).

## Related work candidates (2026-11-20)
**Unverified:** found by web search (Marcel with Claude); only abstracts and search summaries were read. Read each paper before citing it or claiming a difference.
- Indirect prompt injection, the threat: Greshake et al. 2023, "Not what you've signed up for", AISec 2023, arXiv:2302.12173. Data theft is one category in its threat taxonomy.
- Agent injection benchmark: Debenedetti et al. 2024, AgentDojo, NeurIPS 2024 Datasets and Benchmarks, arXiv:2406.13352.
- Training-based injection defenses: StruQ (Chen et al. 2024, arXiv:2402.06363); SecAlign (Chen et al. 2024, arXiv:2410.05451); Wallace et al. 2024, "The Instruction Hierarchy", arXiv:2404.13208. These teach the model to ignore injected instructions; they do not condition on who may see which data. Critique: "A Critical Evaluation of Defenses against Prompt Injection Attacks", arXiv:2505.18333 (StruQ/SecAlign weaker and with utility loss under more diverse attacks).
- System-level defenses with confidentiality labels / information flow: CaMeL (Debenedetti et al. 2025, arXiv:2503.18813); FIDES (arXiv:2505.23643); RTBAS (arXiv:2502.08966). These enforce labels outside the model; our setup trains the model itself (comparison point for the "last-resort layer" framing).
- Leakage of data an agent has seen: "Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During Task Execution", arXiv:2506.01055.
- Contextual-integrity privacy benchmarks: ConfAIde (Mireshghallah et al. 2023, arXiv:2310.17884); PrivacyLens (Shao et al. 2024, arXiv:2409.00138). Mostly without adversarial pressure.
- **Closest to our increment (read 2026-11-20 from the arXiv HTML; Unverified, parts of appendices only as summaries):**
  - Almheiri et al. 2025, Role-Aware LMs (arXiv:2507.23465v3): LoRA on 3–8B models (incl. Llama 3.2 3B) to grant or refuse by role in a 20-role hierarchy; answers are learned into the weights, no data in context, no RAG/tools. Attacks: direct only, 3 templated user-prompt jailbreaks (authority claim, fake role prefix, override); also in training; accuracy on them 70% → 87%. No indirect injection, no untrained system-prompt baseline, no held-out roles/orgs/attack types (only unseen instructions). GPT-4.1 mini as judge.
  - Jayaraman et al. 2025, Permissioned LLMs (arXiv:2505.22860v2): one LoRA adapter per data domain, chosen by the system from the user's credentials; data in the weights. Attacks: none besides membership inference used to audit domain separation; assumes credentials cannot be tampered with. No sensitivity tiers, no injection.
  - Klisura et al. 2025, Role-Conditioned Refusals (arXiv:2510.07642v1): text-to-SQL; model sees schema and role grants (table/column), not the data; prompting vs generator-verifier vs LoRA (Mistral 7B, Llama 3.1 8B). No injection or jailbreak evaluation. Fine-tuned F1 0.93 in distribution drops to about 0.65 on an unseen database set (BIRD).
  - **Proposed (our increment, not yet agreed):** none of the three puts the restricted data in the model's context, attacks through tool outputs (indirect injection) in an agent loop, compares training against a policy prompt on the same model under attack, or holds out attack families. Overlaps: LoRA on small models for access control (all three), fine-tuning beats prompting (Klisura, without attacks), training helps against direct jailbreaks (Almheiri). Klisura's out-of-distribution drop supports our own caution (Q49).
  - **Proposed (Marcel, 2026-11-20): the plain difference from Almheiri et al., for the slides and report.** They train a model to learn the data *and* who may access it: answers and access decisions are both in the weights, and at inference there is no written policy and no data in the context (our reading: they use no retrieval; the paper does not say it in these words, Unverified). We train a model to follow one policy (compare a record's sensitivity tag with the requester's level) and apply it to data that arrives in its context. Consequence: adding or relabelling data in our approach needs no retraining (change the record or its tag); in theirs, new data or changed permissions mean retraining the adapter (their own stated limitation: roles cannot change after fine-tuning). Evidence on our side: **Measured** (run 1, both models): leak 0–0.2% and 100% disclosure on 20 held-out companies whose records were never in training. Limit: shown only for our record and tag format (Q49).
