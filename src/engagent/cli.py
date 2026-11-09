from __future__ import annotations
import argparse, sys
from .agent import RunStatus, run_design


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="engagent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a design request")
    r.add_argument("request")
    r.add_argument("--out", default="runs/latest")
    r.add_argument("--allow-defaults", action="store_true",
                   help="fill non-critical gaps with FLAGGED assumptions (never payload/offset)")
    r.add_argument("--samples", type=int, default=1500)
    r.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    res = run_design(a.request, allow_defaults=a.allow_defaults, n_samples=a.samples, seed=a.seed, out_dir=a.out)
    if res.status == RunStatus.NEEDS_INPUT:
        print("Cannot proceed. Missing information:")
        for q in res.questions:
            print(" -", q)
        print("Tip: --allow-defaults fills non-critical gaps (flagged as assumptions).")
        return 2
    print(f"status: {res.status.value}\nbest: {res.best_id}\nreport: {res.out_dir}/report.md")
    for k, v in res.metrics.items():
        print(f"  {k}: {v}")
    return 0 if res.status == RunStatus.FEASIBLE_FOUND else 1


if __name__ == "__main__":
    sys.exit(main())
