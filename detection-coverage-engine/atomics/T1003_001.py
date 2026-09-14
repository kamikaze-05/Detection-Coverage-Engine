"""T1003.001 — OS Credential Dumping: LSASS Memory (Credential Access)"""

TECHNIQUE_ID = "T1003.001"
NAME = "LSASS Memory Dump"
TACTIC = "credential-access"


def simulate():
    return [
        {
            "EventID": 10,
            "SourceImage": r"C:\Users\Public\procdump.exe",
            "TargetImage": r"C:\Windows\System32\lsass.exe",
            "GrantedAccess": "0x1410",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
