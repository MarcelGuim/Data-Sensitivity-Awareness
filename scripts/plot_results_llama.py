"""Llama figures: same script as plot_results.py, which now finds the model from the folder names.

  python3 scripts/plot_results_llama.py results/eval_llama_run1
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_results  # noqa: E402

if __name__ == "__main__":
    plot_results.main(sys.argv[1] if len(sys.argv) > 1 else "results/eval_llama_run1")
