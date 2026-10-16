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
- **Decided:** Train an LLM agent to recognize how sensitive each piece of data is. Every item in a synthetic company's data carries one of four tiers: public, internal, confidential, highly confidential.
- **Decided:** Examples from the proposal: office map is public; client list is confidential; unreleased product schematics are highly confidential.
- **Decided:** The agent discloses data according to its tier and the requester's authorization, even when an injection instructs otherwise.
- **Decided:** Positioning: a different angle on instruction-hierarchy work ("The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"). Prioritize data by sensitivity rather than instructions by source. A last-resort layer that holds when other defences fail.

## Research question
- **Decided:** Does training a model to reason about data sensitivity reduce leakage under prompt injection beyond what a system-prompt policy achieves, and at what cost to utility?

## Method (from the proposal)
1. **Decided:** Write criteria for the four tiers, including hard cases where individually harmless facts reveal something sensitive when combined.
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
Record of the professor's comments as paraphrased in the planning chat. The two source files word the second point differently; the exact wording is **Open** (docs/07, Q16).
- Related to Data Loss Prevention (DLP) solutions, which usually do not consider an LLM indirect-prompt-injection (IPI) scenario.
- Fine-tuning needs a reasonably powered GPU.
- The evaluation should use a smaller model that may not have been trained to understand tags anyway (kickoff wording); "a small model may not already understand tags" (older handoff wording).
- Identify reasonable models that fit the available hardware.
- Suggested budgeting four weeks plus one buffer week (see `01-plan-and-timeline.md`).

How the feedback is addressed:
- **Decided (2026-10-16):** GPU: train and evaluate on Kaggle (free T4); rent only if it fails (`02-compute-and-environment.md`).
- **Decided:** Models: 3B/4B instruct models, with screening (`03-models.md`).
- **Open:** How the report will position the work against DLP (no plan written yet; docs/07, Q17).
