"""SIMULATION ONLY: generate reviewer decisions from assumed catch and false-flag rates.

This exists to test the pipeline and to show why approval rate alone is uninformative.
It produces no empirical results about real reviewers.

Usage:
    python -m oversight_eval.simulate out/answer_key.jsonl decisions.jsonl --catch 0.4 --false-flag 0.05
"""
import argparse
import json
import random
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("answer_key")
    ap.add_argument("out")
    ap.add_argument("--catch", type=float, default=0.4)
    ap.add_argument("--false-flag", type=float, default=0.05)
    ap.add_argument("--reviewer", default="simulated_reviewer")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    key = [json.loads(l) for l in Path(a.answer_key).read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = []
    for k in key:
        p = a.catch if k["planted"] else a.false_flag
        rows.append({"id": k["id"], "reviewer": a.reviewer, "decision": "flag" if rng.random() < p else "approve"})
    Path(a.out).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"wrote {len(rows)} simulated decisions -> {a.out}")


if __name__ == "__main__":
    main()
