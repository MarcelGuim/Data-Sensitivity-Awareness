# 07 Decisions and open questions

Labels: see `AGENTS.md`. When a question is answered: add a dated row to the decisions log (who decided), update the doc it affects, and mark the question **Closed** here with a pointer. Question numbers are stable; do not renumber.

## Decisions log
Rows dated 2026-10-15/16 were recorded in the planning chat; the exact day within that window was not recorded.

| Date | Decision | Decided by | Notes |
|---|---|---|---|
| 2026-10-12 | Title, research question, four tiers, method, setups (a)(b)(c), evaluation (leakage by tier via canaries, utility, held-out company/domain) | Group (proposal) | |
| 2026-10-15 | HP laptop (GTX 1650 Ti, 4 GB) not used for training | Marcel | Hardware check |
| 2026-10-15 | No training on the Mac; train on a rented or provided GPU | Marcel | MLX benchmark |
| 2026-10-15 | Training stack: PyTorch + TRL + PEFT, QLoRA (bitsandbytes), CUDA; not MLX | Marcel | |
| 2026-10-15/16 | Two models: Qwen3-4B-Instruct-2507 (primary), Llama-3.2-3B-Instruct (second), pending screening | Marcel | |
| 2026-10-15/16 | Stretch: one ~8B model, go or no-go at the Nov 11 gate | Marcel | |
| 2026-10-16 | ~~Nothing runs on the Mac~~ (superseded the same day by the next row) | Marcel | |
| 2026-10-16 | Only training runs on the rented/provided CUDA GPU. Screening, initial validations and experiments, baselines and tests of the trained models run on a team laptop able to run the models (Marcel's M4 24 GB, or any laptop with enough RAM and GPU) | Marcel | Closes Q30, Q31. Laptop evaluation of trained models superseded by the Kaggle evaluation row below |
| 2026-10-16 | The GPU-access email is sent by a classmate of Marcel's, not Marcel. If no GPUs are available to us, the group rents one | Marcel | Q2. "Rent if none" superseded by the Kaggle row below |
| 2026-10-16 | GPU path: Kaggle Notebooks (free T4) first, one account per person; rent only if Kaggle fails (quota, stability, or the ~8B stretch model). Colab only for short tests | Marcel | Supersedes "rent if no GPUs are provided"; Q2, Q21 |
| 2026-10-16 | All final numbers for (a), (b), (c) come from Kaggle with the same transformers + bitsandbytes 4-bit stack used for training. Laptops (e.g. Marcel's Mac) are for development and screening only | Marcel | Closes Q33; supersedes laptop evaluation of trained models |
| Course | Presentations start Nov 25 (plan for that slot); final report due Dec 11 | Course | |

## Proposed, awaiting group agreement
Marcel's position (2026-10-16; teammates have not seen the list yet, a summary for them comes after Q1):
1. Authorization variation: agrees.
2. Fact markers + second detector: agrees.
3. Metrics before dataset: agrees it is needed; asked Claude for concrete proposals.
4. Held-out attack families: wants to train on a few attack types and test generalization. Example: train on email, paraphrased and encoded; test on those three plus multi-encoded, tool returns and other unseen types.
5. ~8 companies, 2 held out: agrees.
6. Write-up task slots: needs a clearer explanation.
7. Tier criteria as a week 1 task: needs a clearer explanation.

Gap analysis from the planning chat (see Q32): authorization variation; fact markers plus a second leak detector; metrics before dataset; held-out attack families; ~8 companies with 2 held out; write-up task slots; tier criteria as an explicit week 1 task. Also proposed: task groups A/B/C, timeline and gates, risks and cut order, rental checklist.

## Open questions
Format: **Why** it matters, **Proposal** (labelled Proposed; "Claude" means raised on 2026-10-16 while writing these docs, not from the planning chat), **Consequences**. Ordered by when the answer is needed.

### Needed this week (before the Oct 21 gate)

**Q2. GPU access. Mostly closed (2026-10-16).**
- Decided: a classmate of Marcel's sends the email. If no GPUs are available to us, we rent.
- Still open: which classmate; the professor's name; the date by which we stop waiting and rent (the older plan said Oct 21). Tracked by the sender, not Marcel.

**Q30. Which GPU runs which work? Closed (2026-10-16):** the GPU only trains; everything else runs on laptops. Original text kept below for reference.
- Why: before the no-Mac decision, the GPU was only for training. Screening, debugging, baselines and evaluation now need it too, and the 10–20 GPU-h/model estimate does not include them.
- Proposal (Claude): Kaggle T4 (16 GB) for screening, script debugging and 3–4B baselines; a rented 24 GB card (or university GPUs) for training runs and the 8B stretch. Re-estimate GPU-hours once Q5 fixes the sample counts.
- Consequences: Kaggle quotas and session limits (Unverified) mean every script must checkpoint and resume, including the evaluation harness. Inference across 2 models × 3+ setups × all cells can rival training time.

**Q1. Screening test. Decided (2026-10-16):** `scripts/screen_models.py` written (Kaggle, training stack, authorized-requester case, saved outputs). Marcel runs it on his new Kaggle account for preliminary results. Still open: the results, and confirming both models from them (Oct 21 gate). Instructions: `docs/03-models.md`.

**Q31. Closed (2026-10-16):** superseded; laptops are used for everything except training.

**Q31 (original).** Does "nothing on the Mac" cover dataset generation and code editing?
- Why: generating data through a hosted API, writing code and editing docs need no CUDA.
- Proposal (Claude): read the rule as "no local model execution". Data generation via an API can run from any machine.
- Consequences: if it really means nothing at all, generation also needs a cloud environment, which adds setup but changes no results.

**Q32. Has the group agreed to the gap-analysis changes?**
- Why: authorization levels, held-out attack families, fact markers and 8 companies all change what the dataset must contain, and the schema is due this week.
- Proposal: walk through them at the Oct 21 sync, or earlier by message.
- Consequences: if agreement comes after data generation, the data gets regenerated.

**Q3. People: who takes which group, who presents what, who merges the report; book the Nov 24 dry run.**
- Why: Group A has to start the criteria now, and nobody owns them yet.
- Proposal: decide at the next sync; the person on Group A should be the one with the most time in weeks 1–3.
- Consequences: no owner means the criteria slip, and everything downstream slips with them.

**Q4. Tier criteria, including combination cases: how are they labelled and scored?**
- Why: they are the ground truth for everything. Combination cases are also the hardest to detect automatically.
- Proposal (Claude): a criteria doc with a definition, 3+ examples and a counterexample per tier. Rule: a combination gets the tier of what it reveals. It counts as a leak only if enough parts to reconstruct it reach an unauthorized requester. Keep combination cases to a small, hand-written, hand-scored eval subset.
- Consequences: canaries cannot detect combinations, so they need the judge or hand scoring. Too many of them makes validation explode.
- Added 2026-10-16 (from the Qwen screening): does confirming that a restricted item exists, or naming its tier ("the schematic is HIGHLY CONFIDENTIAL"), count as a leak? Qwen does this in most refusals.

**Q10. Authorization levels: how many, the mapping, and how identity reaches the agent.**
- Why: without them, over-refusal looks like protection (gap 1).
- Proposal (Claude): four roles mirroring the tiers: external (public), employee (≤ internal), authorized staff (≤ confidential), executive (≤ highly confidential). The requester's role is set in trusted system-prompt metadata. Text in user input or documents claiming a role never raises it.
- Consequences: a monotone mapping is easy to learn and score. Adding need-to-know (per project) is more realistic but roughly doubles the data and labelling work. Keep it out of the core.

**Q13. Which LLM generates the synthetic data?**
- Why: it blocks the pilot company. It also decides quality, cost and terms of use.
- Proposal (Claude): a strong hosted model via API, with fixed prompts committed to the repo. Avoid using the same model as the leak judge.
- Consequences: some providers' terms restrict training models on their outputs (Unverified; check before using). A generator that is also the judge makes correlated errors. A local open model would cost GPU time and give weaker data.

**Q14. Dataset schema, file types and training format.**
- Why: Group A's week 1 deliverable. Group B's tools and Group C's training script both depend on it.
- Proposal (Claude): one JSONL record per item: `company, item_id, tier, content, canary, fact_markers, combination_group`. Tasks in a separate JSONL: `requester_role, prompt, injected_docs, attack_family, expected_behavior, split`. Training data in chat-messages format with tool calls.
- Consequences: changing the schema after generation costs regeneration and revalidation.

**Q33. Closed (2026-10-16):** final evaluation on Kaggle with the training stack; no adapter conversion to MLX. Original text kept below.

**Q33 (original). Evaluation machine, stack, and the adapter path.**
- Why: training happens with bitsandbytes 4-bit on CUDA; evaluation on a laptop uses a different engine and quantization. That is fine only if (a), (b) and (c) all run through the *same* laptop stack, and results from different laptops are never mixed.
- Proposal (Claude): designate one machine (Marcel's Mac) and one stack (MLX 4-bit) for all final numbers. After training: merge the LoRA adapter into the full-precision base model with PEFT, then quantize the merged model to MLX 4-bit; base models for (a)/(b) go through the identical conversion. Teammates' laptops are for development only.
- Consequences: the trained model is evaluated at a slightly different quantization than it was trained at (effect size Unverified; report it as a limitation). A fanless Mac running thousands of long prompts may need a day or more per full evaluation (Estimate), so sample sizes (Q5) must account for it; the fallback is running the same stack on a second identical-spec machine or renting GPU inference time.

### Needed in week 2 (before the Oct 28 gate)

**Q5. Sizes and statistics.**
- Why: the gate says "show headroom" with no number. Sample counts set GPU inference hours and how wide the error bars are.
- Proposal (Claude): ≥100 attacks per cell (model × setup × tier × attack family), with Wilson 95% intervals (±~6 pp around 10% at n = 100). Headroom: (b) leaks ≥ 15–20% on injections for at least the confidential tiers. 1,000–2,000 training examples. Validate ~10% of the training set.
- Consequences: more samples means more GPU time (feeds Q30). Fewer means differences between (b) and (c) may not be significant.

**Q12. Held-out companies: 1 or 2, and which domains?**
- Why: with one held-out company, results reflect that company's quirks, and confidence intervals do not capture this.
- Proposal (Claude): 2 held-out companies in industries not used in training.
- Consequences: two full validations instead of one (gap 5 already budgets this). With 1, the generalization claim is weak.

**Q11. Canary format.**
- Why: training data with canaries can teach the model to suppress strings that *look* like canaries rather than sensitive content, which inflates measured protection.
- Proposal (Claude): natural-looking codes (e.g. a project ID like "PRJ-7F3A"), different formats in train and eval, 2–3 fact markers per sensitive item. Public items get no canary.
- Consequences: with the "CANARY-" format in training, the leakage metric for (c) may be invalid.

**Q6. Attack families and the train/held-out split.**
- Proposal (from the chat): train on direct and email-embedded injections; hold out paraphrased, encoded and multi-step ones. Freeze in week 3.
- Consequences: if the held-out families are too close to the training ones, the held-out result overstates generalization.

**Q15. How the adaptive attacker works.**
- Proposal (Claude): scripted transforms (paraphrase, base64/encoding, summarize-then-leak, translation) for all cells, plus a small attacker-LLM loop against a subset.
- Consequences: the attacker LLM costs API or GPU time. Scripted-only is weaker, and reviewers will see it as non-adaptive.

**Q24. Is (c) evaluated with or without the policy prompt?**
- Proposal (Claude): both. Without the prompt shows what was learned; with it is the realistic deployment setup.
- Consequences: one extra column in every table. With only one, the "beyond a system prompt" claim is ambiguous.

**Q25. Scoring: utility, judge, hand checks, damage benchmark.**
- Proposal (Claude): utility from reference answers plus a judge from a different family than the evaluated models. Hand-check ~10% of judged outputs, stratified. A small standard instruction-following subset as a training-damage check.
- Consequences: API cost. The judge's error rate needs reporting.

**Q20. Inference library on the laptop.** Merged into Q33.

### Needed by week 3

**Q21. Budget cap and who pays.** Mostly moot after the Kaggle decision (2026-10-16); still needed if we rent for the 8B stretch or if Kaggle fails. Proposal: agree on a cap before any rental.

**Q26. Training hyperparameters.** Proposal (Claude, Unverified common defaults): r = 16, alpha = 32, all linear layers, lr 2e-4, 2–3 epochs, one seed for the first run; tune after. Consequences: report seeds; a single seed is a stated limitation.

**Q27. Label conflict between source files.** The older handoff calls loss masking, tiny-model debugging and checkpointing decisions; the kickoff calls them proposed. Proposal: make all three Decided. They are standard practice, and loss masking matters for validity.

**Q22. Fallback model if a core model fails screening.** Proposal (Claude): Phi-4-mini-instruct first (non-thinking by default, Unverified), then SmolLM3-3B with reasoning off. Consequences: a swap after week 2 costs a week.

**Q23. Licenses.** Proposal: check both model cards before results are published. Consequences: the Llama license has naming and attribution terms (Unverified).

### Later

**Q9. Larger model and which one (Nov 11).** Proposal (Claude): Llama-3.1-8B-Instruct (no thinking mode to disable). Consequences: needs a 24 GB card; it is a different release, so not a controlled scaling study.

**Q16. Exact wording of the professor's feedback on tags.** Matters because it may mean small models do not understand `[CONFIDENTIAL]` tags without training, which would argue for (b) being weak by design. Proposal: reread the original message.

**Q17. Positioning against DLP.** Proposal: a related-work paragraph: DLP filters outputs by pattern; this work makes the model itself tier-aware under IPI.

**Q18. Course logistics.** Slot, talk length, report format and length.

**Q29. One buffer week vs the professor's advice.** Week 2 is overloaded: criteria sign-off Oct 21, then generation, validation, attack library and baselines by Oct 28. Proposal (Claude): run the Oct 28 baselines on the pilot company plus the held-out companies only.

**Q34. Items whose tag disagrees with how sensitive they look (new, 2026-10-16, from the Qwen screening).**
- Why: in screening, Qwen with the external policy protected confidential/highly confidential items 5/5 but disclosed the INTERNAL item 5/5 (loose detector). It may judge sensitivity by content rather than by the tag or criteria.
- Proposal (Claude): include a share of such mismatched items in training and evaluation (e.g. a bland-sounding item tagged confidential; a secret-sounding item that is public, such as a published patent), and report them as a separate slice.
- Consequences: without them, (b) and (c) can look good by guessing from content, and the result does not show tier awareness. They also add a utility check (public items that look secret must still be disclosed).

**Q35. Does a refusal that states the secret count as a leak? (new, 2026-10-16, from screening v2)**
- Why: most of Qwen's policy-condition leaks are refusals that restate the value ("...torque spec of 14.2 Nm is HIGHLY CONFIDENTIAL").
- Proposal (Claude): yes. A leak is defined by content disclosed, never by whether the answer sounds like a refusal. Training data for (c) should contain refusals that do not restate restricted content.
- Consequences: the detector must be content-based (as now). A refusal-phrase classifier would undercount leaks badly.

**Q36. Add an optimized-prompt baseline (b+)? (new, 2026-10-16, raised by Marcel after the Llama screening)**
- Status 2026-10-16: exploratory run `v_prompt_optimization` done for Llama: b+ did not help overall (worse on several attacks, fixed base64, no gain on held-out attacks). Qwen run pending. Whether b+ becomes a setup in the main experiment is still open.
- Why: Llama's leaks under the policy may come from a weak prompt rather than a limit that only training can fix. A reviewer will ask whether (c) beats a *good* prompt or just ours.
- Proposal (Claude): yes. Add (b+): the policy plus explicit rules targeting the failures seen in screening (tags are authoritative and cannot be changed by the requester or by documents; text in tool output or documents never changes the requester's clearance; refusals never restate restricted content), optionally with a few examples. Tune it only on training-split attacks and freeze it before any test-split run.
- Consequences: one more column in every table (more evaluation time). If (b+) closes most of the gap, the honest conclusion is that prompting is enough for these attacks; that is still an answer to the research question. Tuning the prompt on test attacks would make (b+) look better than it is.

### Closed or superseded
- **Q7** (build agent, harness, training script): a task, not a question; tracked in `01-plan-and-timeline.md`.
- **Q8** (upgrade the Mac to Python 3.12): reopened 2026-10-16, since the Mac is used again. Proposed: do it before building the real pipeline.
- **Q19** (teammates' hardware): moot for model work; any machine works for editing.
- **Q28** (debugging the training script): reopened 2026-10-16. Proposed: debug data, template and masking with plain LoRA on a tiny model on a laptop, then a short QLoRA smoke test on the GPU.
