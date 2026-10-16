"""Score reviewers against the hidden answer key.

Reviewer decisions: JSONL, one decision per line
    {"id": "...", "reviewer": "teacher_01", "decision": "approve" | "flag"}

Reports, per reviewer:
    catch rate        share of planted errors the reviewer flagged (with 95% Wilson interval)
    false-flag rate   share of correct gradings the reviewer flagged
    catch rate by error type

Usage:
    python -m oversight_eval.score out/answer_key.jsonl decisions.jsonl
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a proportion k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def score(key_rows, decisions):
    key = {k["id"]: k for k in key_rows}
    per = defaultdict(lambda: {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "by_type": defaultdict(lambda: [0, 0])})
    for d in decisions:
        k = key.get(d["id"])
        if k is None:
            continue
        s = per[d["reviewer"]]
        flagged = d["decision"] == "flag"
        if k["planted"]:
            s["tp" if flagged else "fn"] += 1
            t = s["by_type"][k["error_type"]]
            t[0] += int(flagged)
            t[1] += 1
        else:
            s["fp" if flagged else "tn"] += 1
    report = {}
    for r, s in per.items():
        n_err, n_ok = s["tp"] + s["fn"], s["fp"] + s["tn"]
        report[r] = {
            "catch_rate": s["tp"] / n_err if n_err else float("nan"),
            "catch_rate_ci95": wilson(s["tp"], n_err),
            "false_flag_rate": s["fp"] / n_ok if n_ok else float("nan"),
            "approval_rate": (s["fn"] + s["tn"]) / (n_err + n_ok) if (n_err + n_ok) else float("nan"),
            "n_planted": n_err, "n_correct": n_ok,
            "catch_rate_by_type": {t: v[0] / v[1] for t, v in s["by_type"].items()},
        }
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("answer_key")
    ap.add_argument("decisions")
    a = ap.parse_args()
    load = lambda p: [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]
    report = score(load(a.answer_key), load(a.decisions))
    for r, m in sorted(report.items()):
        lo, hi = m["catch_rate_ci95"]
        print(f"{r}: approval {m['approval_rate']:.1%} | catch {m['catch_rate']:.1%} "
              f"[{lo:.1%}, {hi:.1%}] on {m['n_planted']} planted | false flags {m['false_flag_rate']:.1%}")
        for t, v in sorted(m["catch_rate_by_type"].items()):
            print(f"    {t}: {v:.1%}")


if __name__ == "__main__":
    main()
