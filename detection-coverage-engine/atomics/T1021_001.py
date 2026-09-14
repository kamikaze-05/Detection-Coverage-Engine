"""T1021.001 — Remote Services: RDP (Lateral Movement)"""

TECHNIQUE_ID = "T1021.001"
NAME = "RDP Lateral Movement"
TACTIC = "lateral-movement"


def simulate():
    return [
        {
            "EventID": 4624,
            "LogonType": 10,
            "SourceIp": "10.10.14.22",
            "User": "CORP\\svc_backup",
            "Hostname": "DC01",
        }
    ]
