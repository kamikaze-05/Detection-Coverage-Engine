"""
coverage.py
-----------
Persists every pipeline run to SQLite so coverage can be tracked over time,
and flags "decay": a technique that used to be detected but no longer is
(e.g. because a rule broke, a log field got renamed upstream, or a
telemetry source stopped reporting). This is the core "self-scoring"
behavior that separates this from a one-off detection lab.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
    run_id INTEGER,
    technique_id TEXT,
    technique_name TEXT,
    tactic TEXT,
    detected INTEGER,
    rule_file TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
"""


def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn


def record_run(db_path, results):
    conn = get_conn(db_path)
    ts = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO runs (timestamp) VALUES (?)", (ts,))
    run_id = cur.lastrowid
    for r in results:
        conn.execute(
            "INSERT INTO results (run_id, technique_id, technique_name, tactic, detected, rule_file) "
            "VALUES (?,?,?,?,?,?)",
            (run_id, r["technique_id"], r["technique_name"], r["tactic"],
             int(r["detected"]), r.get("rule_file") or ""),
        )
    conn.commit()
    conn.close()
    return run_id, ts


def get_previous_run_results(db_path, before_run_id):
    """Map of technique_id -> was-detected (bool) for the run immediately
    preceding `before_run_id`. Empty dict if there is no prior run."""
    conn = get_conn(db_path)
    cur = conn.execute(
        "SELECT run_id FROM runs WHERE run_id < ? ORDER BY run_id DESC LIMIT 1",
        (before_run_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {}
    prev_run_id = row[0]
    cur = conn.execute(
        "SELECT technique_id, detected FROM results WHERE run_id=?", (prev_run_id,)
    )
    result = {tid: bool(d) for tid, d in cur.fetchall()}
    conn.close()
    return result


def detect_decay(current_results, previous_map):
    """Techniques that flipped from detected -> not detected since last run."""
    decayed = []
    for r in current_results:
        tid = r["technique_id"]
        if previous_map.get(tid) is True and r["detected"] is False:
            decayed.append(tid)
    return decayed


def write_markdown_report(path, run_id, ts, results, decayed, coverage_pct):
    lines = [
        "# Detection Coverage Report\n\n",
        f"**Run ID:** {run_id}  \n**Timestamp:** {ts}  \n**Overall Coverage:** {coverage_pct:.1f}%\n\n",
    ]

    if decayed:
        lines.append("## ⚠️ Coverage Regression Detected\n\n")
        lines.append("The following techniques were previously detected but are **NOT** detected in this run:\n\n")
        for d in decayed:
            lines.append(f"- `{d}`\n")
        lines.append("\n")

    lines.append("## Technique Results\n\n")
    lines.append("| Technique ID | Name | Tactic | Detected | Rule |\n")
    lines.append("|---|---|---|---|---|\n")
    for r in sorted(results, key=lambda x: x["technique_id"]):
        status = "✅" if r["detected"] else "❌"
        lines.append(f"| {r['technique_id']} | {r['technique_name']} | {r['tactic']} | {status} | {r.get('rule_file') or '_no rule_'} |\n")

    Path(path).write_text("".join(lines), encoding="utf-8")
