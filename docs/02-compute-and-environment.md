# 02 Compute and environment

Labels: see `AGENTS.md`.

## Where compute runs
- **Decided (2026-10-16):** Training and all final evaluation of (a), (b), (c) run on Kaggle Notebooks (free T4), with one stack: PyTorch + transformers + bitsandbytes 4-bit. Rent a GPU only if Kaggle fails (quota, stability, or the ~8B stretch model).
- **Decided (2026-10-16):** Team laptops that can run the models (e.g. Marcel's MacBook Air M4, 24 GB) are for development, quick experiments and screening only. Their numbers never go into results tables.
- **Decided:** The HP laptop (GTX 1650 Ti, 4 GB) is not one of them.

## Hardware findings (historical, kept for the report)
### HP laptop (Ubuntu)
- **Measured:** NVIDIA GeForce GTX 1650 Ti Mobile (TU117), 4 GB VRAM, no tensor cores, no bf16; 14 GiB usable RAM (16 GB machine); proprietary NVIDIA driver not installed (nouveau/nvidiafb only), so `nvidia-smi` does not work.

### MacBook Air M4, 24 GB unified memory, fanless
- **Measured:** Runs, but overheats and throttles. Marcel stopped a benchmark run because the laptop was burning up.
- **Measured (MLX benchmark):** `mlx-community/Qwen2.5-3B-Instruct-4bit`, LoRA, batch 1, max seq 2048, gradient checkpointing, 100 iterations requested, dummy data ~1,500 tokens/example.

| Quantity | Value | Label |
|---|---|---|
| Trainable parameters | 0.216% (6.652M of 3085.939M) | Measured |
| Peak memory | 4.263 GB | Measured |
| Training throughput | ~184 tokens/s, first 10 iterations only | Measured (probably optimistic given throttling) |
| Validation forward pass | ~400 tokens/s (13.5k tokens in 33 s) | Measured |
| Loss values | meaningless (dummy data repeats one sentence) | Measured |

- **Estimate:** ~1.1 h per epoch for 500 examples, 2.3 h for 1,000, 4.5 h for 2,000 (at ~1,500 tokens each). This is why local training was ruled out.
- **Measured:** Marcel's Mac environment: venv `~/mlx-env` on system Python 3.9 (mlx-lm 0.29.1, mlx 0.29.3, transformers 4.57.6; Python 3.9 forced old versions). Qwen2.5-3B cached under `~/.cache/huggingface/hub` (~1.74 GB). A dummy `./data` folder and possibly `adapters/` exist where the benchmark ran.
- **Proposed:** `brew install python@3.12`, recreate the venv, reinstall, before building the real pipeline (docs/07, Q8).

## Training and inference stack
- **Decided:** Training: PyTorch + Hugging Face TRL + PEFT with QLoRA (bitsandbytes) on CUDA. MLX training scripts do not transfer; do not build the training pipeline in MLX.
- **Decided (2026-10-16):** Evaluation uses the same transformers + bitsandbytes 4-bit stack as training, on Kaggle, so (c) is tested at the quantization it was trained at and all setups share one stack.

## Kaggle constraints
- **Unverified (third-party sources):** ~30 GPU-hours/week per account (the quota may float; check account settings); sessions up to 12 h; T4 16 GB or 2× T4; background "Save & Run All" runs keep their outputs, interactive session files are lost.
- **Unverified:** Kaggle allows one account per person, so ~90 GPU-hours/week for the group.
- **Proposed:** Every training and evaluation script checkpoints and resumes; long jobs run as background runs.
- **Proposed:** Pin library versions in the notebook (Kaggle's image changes over time).
- **Proposed:** Hugging Face token (Llama is gated) stored in Kaggle Secrets, never in notebook code.
- **Unverified:** T4 has no bf16, so training is fp16; watch for NaN losses in the smoke test.
- **Proposed:** With 2× T4, evaluate the two models in parallel, one per GPU.
- **Estimate (not measured):** QLoRA on a T4 is perhaps 5–10× the Mac's 184 tokens/s, i.e. under an hour per epoch for 2,000 examples. Measure on the smoke test.
- **Estimate:** An ~8B model in 4-bit on 16 GB may only fit with short sequences; renting may be needed for the stretch.

## GPU options
- **Decided (2026-10-16):** Kaggle first (see above).
- **Decided (2026-10-16):** Colab free tier only for short tests: no published quota, no guaranteed GPU, idle disconnects (Unverified details).
- **Decided (2026-10-16):** A classmate of Marcel's still sends the GPU-access email to the professor; provided GPUs would be an extra option. **Open:** sender, professor's name (docs/07, Q2).
- **Decided (2026-10-16):** Fallback if Kaggle fails: rent a 16–24 GB card (RTX 4090, A5000, L4) on RunPod, Vast.ai or Lambda.

- **Unverified:** Rental prices change; the chat guessed well under a dollar an hour for these cards.
- **Unverified (older handoff only):** Qwen3-4B fits QLoRA on a 16 GB T4.
- **Estimate:** 10–20 GPU-hours per model for training including retries (20–40 for two), plus evaluation time on Kaggle (recompute once Q5 fixes sample sizes).
- **Open:** Budget cap and who pays (docs/07, Q21).

Rental checklist: `06-training-plan.md`.
