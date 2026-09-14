import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.sigma_eval import _match_field, _match_selection, evaluate_rule


def test_match_field_contains():
    event = {"CommandLine": "powershell.exe -Enc SQBFAFgA"}
    assert _match_field(event, "CommandLine|contains", ["-enc", "-encodedcommand"]) is True


def test_match_field_endswith_case_insensitive():
    event = {"Image": r"C:\Windows\System32\SCHTASKS.EXE"}
    assert _match_field(event, "Image|endswith", r"\schtasks.exe") is True


def test_match_field_equals_no_modifier():
    event = {"EventID": 4624}
    assert _match_field(event, "EventID", 4624) is True
    assert _match_field(event, "EventID", 4625) is False


def test_match_field_missing_field_is_false():
    event = {"Image": "foo.exe"}
    assert _match_field(event, "CommandLine|contains", "-enc") is False


def test_match_selection_requires_all_fields():
    selection = {
        "Image|endswith": r"\schtasks.exe",
        "CommandLine|contains": "/create",
    }
    matching_event = {"Image": r"C:\Windows\System32\schtasks.exe", "CommandLine": "schtasks.exe /create /tn X"}
    non_matching_event = {"Image": r"C:\Windows\System32\schtasks.exe", "CommandLine": "schtasks.exe /delete /tn X"}
    assert _match_selection(matching_event, selection) is True
    assert _match_selection(non_matching_event, selection) is False


def test_evaluate_rule_simple_condition():
    rule = {
        "detection": {
            "selection": {"Image|endswith": r"\systeminfo.exe"},
            "condition": "selection",
        }
    }
    events = [{"Image": r"C:\Windows\System32\systeminfo.exe"}, {"Image": "notepad.exe"}]
    matched = evaluate_rule(rule, events)
    assert len(matched) == 1


def test_evaluate_rule_count_threshold():
    rule = {
        "detection": {
            "selection": {"EventID": 4625},
            "condition": "selection | count() > 4",
        }
    }
    few_events = [{"EventID": 4625} for _ in range(3)]
    many_events = [{"EventID": 4625} for _ in range(6)]
    assert evaluate_rule(rule, few_events) == []
    assert len(evaluate_rule(rule, many_events)) == 6


def test_evaluate_rule_unknown_selection_returns_empty():
    rule = {"detection": {"condition": "selection_typo"}}
    assert evaluate_rule(rule, [{"Image": "x"}]) == []
