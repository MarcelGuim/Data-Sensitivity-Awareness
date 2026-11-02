# 09 Proposal presentation (Wednesday Oct 21) and weekly plan

Labels: see `AGENTS.md`. Draft by Claude for the group meeting on 2026-10-17. It answers the professor's four questions and adds a week-by-week plan with owners. Facts come from `00`, `01`, `03`, `07` and `08`; if they disagree, those files win. Everything marked Proposed or Open has to be agreed in the meeting.

## 1. The problem, and the work we build on
- **Decided:** Prompt injection is unsolved. Models cannot reliably separate instructions from data, and detection-based defences can be bypassed. When an agent with access to company data is injected, it can disclose anything it can read.
- **Decided:** Our angle: limit the *blast radius*. Accept that an injection may succeed in redirecting the agent; make sure what it discloses stays contained by the data's sensitivity and the requester's authorization.
- **Decided:** Builds on instruction-hierarchy training: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions". We prioritize *data by sensitivity* instead of *instructions by source*.
- **Unverified (Claude, from memory; check before citing):** Wallace, Xiao, Leike, Weng, Heidecke, Beutel (OpenAI), 2024, arXiv:2404.13208. As far as Claude knows, no public code repository; say so on the slide if confirmed.
- **Proposed (Claude), Unverified details:** related work worth one line each: StruQ (Chen et al., 2024, arXiv:2402.06363) and SecAlign (Chen et al., 2024, arXiv:2410.05451), which train models against prompt injection; AgentDojo (Debenedetti et al., 2024, github.com/ethz-spylab/agentdojo), a benchmark of injections against tool-using agents. DLP tools filter outputs by pattern and do not consider indirect prompt injection (professor's feedback; Q17).
- **Measured (preliminary, our screening):** the problem is real on our candidate models. With a policy system prompt, an instruction hidden in a fake tool result made both models give an employee every confidential item 20/20 times (`08-findings-summary.md`).

## 2. The idea we test
- **Decided:** Fine-tune a small open model (QLoRA) on a synthetic, sensitivity-labelled company dataset so it discloses data by tier (public, internal, confidential, highly confidential) and requester authorization, even when an injection says otherwise.
- **Decided:** Compare three setups: (a) untrained, no protection; (b) untrained + a policy system prompt; (c) trained.
- **Proposed:** (b+) a stronger, optimized policy prompt as an extra baseline, so (c) is compared with a good prompt and not only ours (Q36).
- **Decided:** Models: Qwen3-4B-Instruct-2507 and Llama-3.2-3B-Instruct; Kaggle T4 GPUs.
- Research question (**Decided**): does training a model to reason about data sensitivity reduce leakage under prompt injection beyond what a system-prompt policy achieves, and at what cost to utility?

## 3. How we evaluate it
### a) Metrics
- **Decided:** Leakage rate by tier.
- **Decided:** Utility on normal, non-sensitive tasks (cost of protection; training damage).
- **Proposed:** Leakage broken down by tier × requester role × attack family. A leak is any restricted content in the answer, including inside a refusal (Q35).
- **Proposed:** Over-refusal: authorized requests that are wrongly refused.
- **Proposed:** 95% confidence intervals on every rate. **Open:** samples per cell (Q5).

### b) The test
- **Decided:** An agent with access to the company data is attacked with prompt injections that try to extract restricted data. Leaks are detected automatically by canary strings planted in sensitive items.
- **Proposed:** Plus fact markers (distinctive names and numbers), because screening showed canaries miss many leaks (`08` §6).
- **Proposed:** Attacks vary on two axes: *where* the injection sits (user message, email, document, tool output) and *how* it is written (authority claim, relabelling, encoding, translation, spelling out). Some of each are held out from training to test generalization (Q6).
- **Decided:** Held-out company and data domain never seen in training.
- **Decided (if possible):** an adaptive attacker targeting the defence (paraphrasing, encoding, summarizing).

### c) Dataset
- **Decided:** Synthetic company data generated with an LLM, manually validated against written tier criteria (every evaluation item, a sample of training items), with canaries in sensitive items.
- **Proposed:** ~8 companies, 2 held out for testing; requesters with different authorization levels; benign tasks for utility; items whose tag disagrees with how sensitive they look (Q34).
- **Open:** generator model, schema, size (Q13, Q14, Q5).

## 4. Expected outcome if the idea works
- **Decided (hypothesis from the proposal):** the trained model (c) leaks less than (a) and (b) under prompt injection, including adaptive attacks; it generalizes to the unseen company and domain; and it keeps reasonable utility on legitimate tasks.
- **Proposed (Claude): make it measurable for the slide.** "Works" means:
  1. (c) leaks less than (b) (and b+) on the **held-out** attack families and company, with non-overlapping 95% intervals;
  2. over-refusal and benign utility within a few points of (b) (**Open:** the threshold, Q5);
  3. the gain shows on both models.
- **Proposed:** say up front what a negative result looks like: (b+) closes most of the gap, or (c) only beats (b) on attack families it was trained on. Both still answer the research question.
- **Measured (screening, motivation only):** there is room to improve. Under (b), both models give a bland-looking INTERNAL item to an outsider 18–20/20; Qwen restates secrets in refusals; Llama labels the confidential client list "publicly available". A hand-written optimized prompt did not fix Llama.

## 5. Weekly plan and owners
**Open (Q3): who takes which group.** The meeting should fill the Owner column. Three groups, one person each, from `01-plan-and-timeline.md` (**Proposed**):
- **Group A, data and ground truth:** tier criteria, companies, tasks, validation, training files.
- **Group B, agent and attacks:** agent harness, attack library, baselines, adaptive attacks.
- **Group C, training and evaluation:** metrics, training script, training runs, evaluation and figures.
- **Proposed (Claude):** Marcel on C, since he already runs the Kaggle setup and screening. Wasilat and Khalid choose A or B.

**Proposed** timeline (course dates and the Nov 11 go/no-go are Decided):

| Week | A: Data (owner: ?) | B: Agent and attacks (owner: ?) | C: Training and evaluation (owner: ?) | Gate |
|---|---|---|---|---|
| 1: Oct 15–21 | Tier criteria and authorization levels; dataset schema; one pilot company | Agent skeleton (data tools, policy prompt, logging); first direct and indirect injections | Screening on both models (**done**); GPU path (**done**: Kaggle); metric definitions | Proposal presented; criteria signed off by all three; models confirmed (Oct 21) |
| 2: Oct 22–28 | Generate all companies; validate held-out companies fully, sample the rest; benign and authorization tasks | Attack library v1, split train/held-out; agent end to end; baselines (a) and (b) on both models | Metrics and statistics code; training script debugged on a tiny model | Baselines show headroom (Oct 28) |
| 3: Oct 29–Nov 4 | Finish validation; freeze data; training files | Adaptive attacker vs (b); freeze attack sets; rerun baselines on final data | First real training run (Qwen); check utility damage; evaluate checkpoint | Data and attacks frozen; trained checkpoint exists (Nov 4) |
| 4: Nov 5–11 | Error analysis; draft data section | All setups on both models; adaptive attacks vs (c); draft agent/attack section | Train Llama; held-out and utility evaluation; tables; draft results section | Full results; go/no-go on ~8B (Nov 11) |
| 5: Nov 12–18 (buffer) | Fix gaps; slide skeleton | Reruns if needed; slide skeleton | Retrain/re-evaluate; ~8B if go; slide skeleton | **Results frozen (Nov 18)** |
| 6: Nov 19–25 | Data slides | Agent/attack slides | Results slides | Slides Nov 23; dry run Nov 24; presentations from Nov 25 |
| 7: Nov 26–Dec 2 | Finish data section | Finish agent/attack section | Finish training/results section | Full draft Dec 2 |
| Dec 3–11 | Read-through | Read-through | Read-through; submit | Report due Dec 11 |

Shared by all three (**Proposed**): tier-criteria sign-off (week 1), manual validation (weeks 2–3), results review (Nov 11), a ~30-minute sync at each gate, one person merging the report (**Open**, Q3).

## 6. Problems to settle in the meeting
- **Open:** Week 1 ends at Wednesday's gate. The repo records only the screening and the GPU path as done; there is no record of the tier criteria, the dataset schema, the agent skeleton or the metric definitions (teammates may have work not yet in the repo). Either they are done by Oct 21, or the gate moves and week 2 gets tighter. That week has no slack: validation is the bottleneck.
- **Open:** the presentation format and length (Q18); find out before building slides.
- **Open:** the gap-analysis items and the Q34–Q36 proposals (`08` §8–9); the dataset depends on them.
- **Proposed:** keep the GitHub repo private until held-out data policy is decided (the repo is public as of 2026-10-16).
