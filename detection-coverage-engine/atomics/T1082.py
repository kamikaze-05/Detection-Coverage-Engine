"""T1082 — System Information Discovery (Discovery)"""

TECHNIQUE_ID = "T1082"
NAME = "System Information Discovery"
TACTIC = "discovery"


def simulate():
    return [
        {
            "EventID": 1,
            "Image": r"C:\Windows\System32\systeminfo.exe",
            "ParentImage": r"C:\Windows\System32\cmd.exe",
            "CommandLine": "systeminfo.exe",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
