"""
emulator.py
-----------
Discovers "atomic" technique modules and runs their simulate() function to
generate synthetic telemetry (Sysmon/Windows-Event-Log-shaped JSON events).

Design note: this does NOT execute real attacker tradecraft on the host.
Each atomic module returns data structured exactly like the log event a
real EDR/Sysmon/Windows Event Log sensor would produce if that technique
were executed. This keeps the pipeline safe to run anywhere (laptop, CI
runner) while still exercising the full detection-engineering workflow:
write a detection -> generate matching telemetry -> prove it fires.
"""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


def discover_atomics(atomics_dir):
    """Dynamically load every technique module in the atomics/ directory."""
    modules = []
    for f in sorted(Path(atomics_dir).glob("T*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for attr in ("TECHNIQUE_ID", "NAME", "TACTIC", "simulate"):
            if not hasattr(mod, attr):
                raise ValueError(f"{f.name} is missing required attribute '{attr}'")
        modules.append(mod)
    return modules


def run_emulation(atomics_dir, output_path):
    """Run every technique's simulate() and write the combined telemetry
    stream to a JSONL file. Returns (events, technique_metadata)."""
    modules = discover_atomics(atomics_dir)
    all_events = []
    run_ts = datetime.now(timezone.utc).isoformat()

    for mod in modules:
        events = mod.simulate()
        for e in events:
            e["technique_id"] = mod.TECHNIQUE_ID
            e["technique_name"] = mod.NAME
            e["tactic"] = mod.TACTIC
            e.setdefault("Timestamp", run_ts)
        all_events.extend(events)

    with open(output_path, "w") as f:
        for e in all_events:
            f.write(json.dumps(e) + "\n")

    technique_metadata = [(m.TECHNIQUE_ID, m.NAME, m.TACTIC) for m in modules]
    return all_events, technique_metadata
