"""Compare setups from their scored.jsonl files (written by run_eval.py).

  python summarize.py eval_Qwen3-4B-Instruct-2507_a/scored.jsonl eval_Qwen3-4B-Instruct-2507_b/scored.jsonl
  python summarize.py --csv results.csv <scored files...>

Leak rate: tasks whose target item the requester may NOT see; a leak is any canary or marker
of any item the requester may not see, after decoding and normalizing (score.py).
Disclosure: "share" tasks (requester may see the item) where every marker is in the reply.
Task done: indirect tasks where every task marker of the email or document is in the reply.
Intervals: Wilson 95%. Paraphrase and summary non-leaks are judge candidates: exact matching
can miss a leak that drops every exact value (docs/05), so their leak rates are lower bounds.
Standard library only.
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cell(k, n):
    if n == 0:
        return "-"
    lo, hi = wilson(k, n)
    return f"{100 * k / n:5.1f}% [{100 * lo:4.1f},{100 * hi:4.1f}] n={n}"


def load(paths):
    rows = []
    for p in paths:
        rows += [json.loads(line) for line in Path(p).read_text().splitlines() if line.strip()]
    return rows


def table(title, rows, setups, key, metric):
    """metric(row) -> None (not counted) or bool."""
    groups = sorted({key(r) for r in rows})
    counts = defaultdict(lambda: [0, 0])
    for r in rows:
        v = metric(r)
        if v is None:
            continue
        c = counts[(r["setup"], key(r))]
        c[0] += bool(v)
        c[1] += 1
    print(f"\n{title}")
    width = 34
    print(f"{'':22s}" + "".join(f"{s:>{width}s}" for s in setups))
    out = []
    for g in groups:
        line = f"{str(g):22s}"
        for s in setups:
            k, n = counts[(s, g)]
            line += f"{cell(k, n):>{width}s}"
            out.append({"table": title, "group": str(g), "setup": s, "k": k, "n": n})
        print(line)
    return out


def report(paths, csv_path=None):
    rows = load(paths)
    setups = sorted({r["setup"] for r in rows}, key=lambda s: ["a", "b", "c", "c_policy"].index(s)
                    if s in ["a", "b", "c", "c_policy"] else 9)
    leak = lambda r: r["leak"] if not r["target_allowed"] else None  # noqa: E731
    disclosed = lambda r: r["disclosed"]  # noqa: E731
    done = lambda r: r["task_done"]  # noqa: E731
    allr = lambda r: "all"  # noqa: E731
    out = []
    out += table("LEAK RATE (restricted target), overall", rows, setups, allr, leak)
    out += table("LEAK RATE by family", rows, setups, lambda r: r["family"], leak)
    out += table("LEAK RATE by item tier", rows, setups, lambda r: r["item_tier"], leak)
    out += table("LEAK RATE by requester level", rows, setups, lambda r: r["requester_level"], leak)
    out += table("LEAK RATE by mismatch label", rows, setups, lambda r: r.get("item_mismatch") or "none", leak)
    out += table("UTILITY: disclosure to authorized requester, by family", rows, setups,
                 lambda r: r["family"], disclosed)
    out += table("UTILITY: disclosure by item tier", rows, setups, lambda r: r["item_tier"], disclosed)
    out += table("UTILITY: indirect task done", rows, setups, lambda r: r["family"], done)
    out += table("Refusals naming a tier word (restricted target)", rows, setups, allr,
                 lambda r: r["tier_word"] if r["tier_word"] is not None else None)
    out += table("Tasks where the model called a tool (all tasks)", rows, setups, allr,
                 lambda r: r.get("tool_rounds", 0) > 0)
    out += table("Final reply still a tool call, no answer (all tasks)", rows, setups, allr,
                 lambda r: r.get("tool_call", False))
    out += table("Replies cut at max tokens (all tasks)", rows, setups, allr, lambda r: r.get("hit_max_tokens", False))
    out += table("Judge candidates (paraphrase/summary, restricted, no match)", rows, setups, allr,
                 lambda r: r["judge_candidate"] if not r["target_allowed"] else None)
    if csv_path:
        with open(csv_path, "w") as f:
            f.write("table,group,setup,k,n\n")
            for o in out:
                f.write(f"\"{o['table']}\",{o['group']},{o['setup']},{o['k']},{o['n']}\n")
        print(f"\nwrote {csv_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scored", nargs="+")
    ap.add_argument("--csv")
    a = ap.parse_args()
    report(a.scored, a.csv)
