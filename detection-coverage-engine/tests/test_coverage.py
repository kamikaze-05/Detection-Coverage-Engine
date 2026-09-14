import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.coverage import record_run, get_previous_run_results, detect_decay


def _result(tid, detected, tactic="execution", rule_file="rule.yml"):
    return {"technique_id": tid, "technique_name": tid, "tactic": tactic,
            "detected": detected, "rule_file": rule_file if detected else None}


def test_record_and_retrieve_previous_run():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"

        run1_id, _ = record_run(db_path, [_result("T1059.001", True), _result("T1070.004", False)])
        previous = get_previous_run_results(db_path, run1_id)
        assert previous == {}  # no run before the first one

        run2_id, _ = record_run(db_path, [_result("T1059.001", False), _result("T1070.004", False)])
        previous = get_previous_run_results(db_path, run2_id)
        assert previous == {"T1059.001": True, "T1070.004": False}


def test_detect_decay_flags_regression_only():
    current = [_result("T1059.001", False), _result("T1070.004", False), _result("T1486", True)]
    previous_map = {"T1059.001": True, "T1070.004": False, "T1486": True}
    decayed = detect_decay(current, previous_map)
    assert decayed == ["T1059.001"]


def test_detect_decay_no_previous_data():
    current = [_result("T1059.001", False)]
    assert detect_decay(current, {}) == []
