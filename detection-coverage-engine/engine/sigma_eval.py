"""
sigma_eval.py
-------------
A minimal, dependency-light Sigma rule loader and matcher.

Supported subset (deliberately scoped for this project — see README
"Limitations" section for what a production system would add via pySigma):
  - A single `selection` block with implicit AND across fields
  - Field modifiers: |contains, |endswith, |startswith (case-insensitive),
    and plain equality when no modifier is given
  - List values under a field are OR'd together
  - condition: "selection"  (single named block)
  - condition: "selection | count() > N"  (basic threshold aggregation,
    used for volumetric detections like brute-force)

This is NOT a full Sigma spec implementation. It is enough to demonstrate
detection-as-code: rules are plain YAML, version-controlled, and testable
in CI exactly like the ones your SIEM would ingest.
"""

import re
from pathlib import Path

import yaml


def load_rules(rules_dir):
    rules = []
    for f in sorted(Path(rules_dir).glob("*.yml")):
        with open(f) as fh:
            rule = yaml.safe_load(fh)
        rule["_file"] = f.name
        rules.append(rule)
    return rules


def _match_field(event, field_expr, expected):
    if "|" in field_expr:
        field, modifier = field_expr.split("|", 1)
    else:
        field, modifier = field_expr, "equals"

    actual = event.get(field)
    if actual is None:
        return False
    actual_str = str(actual).lower()

    expected_values = expected if isinstance(expected, list) else [expected]
    for v in expected_values:
        v_str = str(v).lower()
        if modifier == "contains" and v_str in actual_str:
            return True
        if modifier == "endswith" and actual_str.endswith(v_str):
            return True
        if modifier == "startswith" and actual_str.startswith(v_str):
            return True
        if modifier == "equals" and actual_str == v_str:
            return True
    return False


def _match_selection(event, selection):
    """AND across every field in the selection block."""
    return all(_match_field(event, field_expr, value) for field_expr, value in selection.items())


_COUNT_RE = re.compile(r"count\(\)\s*(>=|>)\s*(\d+)")


def evaluate_rule(rule, events):
    """Return the list of events (from a single technique run) that satisfy
    this rule's condition. Empty list means the rule did not fire."""
    detection = rule.get("detection", {})
    condition = str(detection.get("condition", "selection")).strip()

    count_threshold = None
    m = _COUNT_RE.search(condition)
    if m:
        op, num = m.group(1), int(m.group(2))
        count_threshold = (op, num)
        selection_name = condition.split("|")[0].strip()
    else:
        selection_name = condition

    selection = detection.get(selection_name)
    if selection is None:
        return []

    matched = [e for e in events if _match_selection(e, selection)]

    if count_threshold:
        op, num = count_threshold
        ok = (len(matched) > num) if op == ">" else (len(matched) >= num)
        return matched if ok else []

    return matched
