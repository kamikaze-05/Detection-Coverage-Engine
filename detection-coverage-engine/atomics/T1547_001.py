"""T1547.001 — Boot or Logon Autostart Execution: Registry Run Keys (Persistence)"""

TECHNIQUE_ID = "T1547.001"
NAME = "Registry Run Key Persistence"
TACTIC = "persistence"


def simulate():
    return [
        {
            "EventID": 13,
            "Image": r"C:\Windows\System32\reg.exe",
            "TargetObject": r"HKU\S-1-5-21-...\Software\Microsoft\Windows\CurrentVersion\Run\Updater",
            "Details": r"C:\Users\Public\update.exe",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
