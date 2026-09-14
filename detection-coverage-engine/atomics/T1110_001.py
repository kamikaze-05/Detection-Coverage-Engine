"""T1110.001 — Brute Force: Password Guessing (Credential Access)

Generates multiple failed-logon events so the volumetric Sigma rule
(condition: selection | count() > 4) has something to threshold against.
"""

TECHNIQUE_ID = "T1110.001"
NAME = "Password Guessing"
TACTIC = "credential-access"


def simulate():
    return [
        {
            "EventID": 4625,
            "TargetUserName": "administrator",
            "SourceIp": "185.220.101.7",
            "Hostname": "DC01",
        }
        for _ in range(6)
    ]
