# 06 Training plan

Labels: see `AGENTS.md`.

## Stack
- **Decided:** PyTorch + Hugging Face TRL + PEFT, QLoRA (bitsandbytes), CUDA.
- **Decided (2026-10-16):** Runs on Kaggle Notebooks (free T4); rent only if Kaggle fails. Evaluation uses the same stack on Kaggle, so no adapter export is needed. Constraints: `02-compute-and-environment.md`.
- **Open:** Library versions, LoRA rank/alpha/target modules, learning rate, epochs, sequence length, batch size, runs and seeds (docs/07, Q26).

## Loss masking
- **Proposed:** Mask the loss to assistant turns only; otherwise the model trains on system prompts and canaries. (The older handoff lists this as a decision; the kickoff lists it as proposed. **Open**, docs/07, Q27.)
- **Proposed:** Check that TRL/PEFT support each model's chat template.
- **Proposed:** No thinking-mode models in the first experiments, because reasoning tags interfere with loss masking.

## Debugging path
- **Proposed:** Debug the data format, chat template and loss masking on a tiny model (for example Qwen2.5-0.5B-Instruct), on a laptop with plain LoRA or directly on Kaggle. Then a short QLoRA smoke test on Kaggle: check for fp16 NaN losses, time tokens/s, test checkpoint and resume (docs/07, Q28).

## Run plan
- **Proposed:** Week 2: script debugged on a tiny model.
- **Proposed:** Week 3: first real training run (Qwen3-4B); check training damage on benign tasks; evaluate the first checkpoint. Gate Nov 4: a trained checkpoint exists.
- **Proposed:** Week 4: train Llama-3.2-3B with the same script; main runs; retrain if adaptive attacks expose a weakness.
- **Proposed:** Week 5: retrain or re-evaluate if needed; larger model (~8B) if the Nov 11 gate is green and budget allows. **Decided:** go or no-go on Nov 11.
- **Proposed:** One model end to end first; do not debug both in parallel.
- **Proposed:** Results frozen Nov 18.
- **Estimate:** 10–20 GPU-hours per model for training including retries; 20–40 for two models.

## Run checklist (Kaggle, and any rental)
**Proposed:**
1. Freeze the model and framework first.
2. Debug the training script on a tiny model, then a short QLoRA smoke test on Kaggle.
3. Mask the loss to assistant turns only.
4. Have the dataset validated and uploaded.
5. Check remaining Kaggle quota; set a budget only if renting (docs/07, Q21).
6. Checkpoint every few hundred steps (needed anyway for Kaggle session limits).
7. Run long jobs as background runs; for rentals, shut the instance down the moment a run finishes.
