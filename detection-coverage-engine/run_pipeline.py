#!/usr/bin/env python3
"""
run_pipeline.py
---------------
Self-scoring purple team pipeline:

  1. Emulate every technique in atomics/  -> synthetic telemetry (JSONL)
  2. Evaluate every rule in detections/   -> which techniques fired
  3. Record the run in SQLite             -> coverage history over time
  4. Flag decay                          -> anything that regressed since last run
  5. Export a Markdown report + an ATT&CK Navigator heatmap layer

Exit codes (for CI gating):
  0 = coverage >= --min-coverage AND (not --fail-on-decay OR no decay)
  1 = otherwise
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine.emulator import run_emulation
from engine.sigma_eval import load_rules, evaluate_rule
from engine.coverage import record_run, get_previous_run_results, detect_decay, write_markdown_report
from engine.navigator_export import write_navigator_layer

ROOT = Path(__file__).parent
ATOMICS_DIR = ROOT / "atomics"
DETECTIONS_DIR = ROOT / "detections"
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
DB_PATH = DATA_DIR / "coverage_history.db"


def main():
    parser = argparse.ArgumentParser(description="Self-scoring purple team detection coverage pipeline")
    parser.add_argument("--min-coverage", type=float, default=0.0,
                         help="Minimum coverage percent required to exit 0 (use in CI, e.g. 70)")
    parser.add_argument("--fail-on-decay", action="store_true",
                         help="Exit non-zero if any previously-detected technique regresses")
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "logs").mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    log_path = DATA_DIR / "logs" / "latest_run.jsonl"
    events, techniques = run_emulation(ATOMICS_DIR, log_path)

    rules = load_rules(DETECTIONS_DIR)

    results = []
    for tid, name, tactic in techniques:
        technique_events = [e for e in events if e["technique_id"] == tid]
        detected, rule_file = False, None
        for rule in rules:
            if evaluate_rule(rule, technique_events):
                detected, rule_file = True, rule.get("_file")
                break
        results.append({
            "technique_id": tid, "technique_name": name, "tactic": tactic,
            "detected": detected, "rule_file": rule_file,
        })

    total = len(results)
    detected_count = sum(1 for r in results if r["detected"])
    coverage_pct = 100.0 * detected_count / total if total else 0.0

    run_id, ts = record_run(DB_PATH, results)
    previous_map = get_previous_run_results(DB_PATH, run_id)
    decayed = detect_decay(results, previous_map)

    write_markdown_report(REPORTS_DIR / "coverage_report.md", run_id, ts, results, decayed, coverage_pct)
    write_navigator_layer(REPORTS_DIR / "navigator_layer.json", results)

    print(f"\nDetection Coverage Pipeline — Run #{run_id} @ {ts}")
    print("=" * 64)
    for r in sorted(results, key=lambda x: x["technique_id"]):
        mark = "PASS" if r["detected"] else "GAP "
        print(f"  [{mark}] {r['technique_id']:<12} {r['technique_name']:<32} ({r['tactic']})")
    print("=" * 64)
    print(f"Overall coverage: {coverage_pct:.1f}%  ({detected_count}/{total} techniques)")
    if decayed:
        print(f"\n[WARNING] COVERAGE REGRESSION on: {', '.join(decayed)}")
    print(f"\nReports written to: {REPORTS_DIR}/")

    exit_code = 0
    if coverage_pct < args.min_coverage:
        print(f"\nFAILED: coverage {coverage_pct:.1f}% is below required minimum {args.min_coverage}%")
        exit_code = 1
    if args.fail_on_decay and decayed:
        print("\nFAILED: coverage regression detected")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
