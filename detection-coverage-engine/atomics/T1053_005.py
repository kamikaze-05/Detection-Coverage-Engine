"""T1053.005 — Scheduled Task/Job: Scheduled Task (Persistence)"""

TECHNIQUE_ID = "T1053.005"
NAME = "Scheduled Task Persistence"
TACTIC = "persistence"


def simulate():
    return [
        {
            "EventID": 1,
            "Image": r"C:\Windows\System32\schtasks.exe",
            "ParentImage": r"C:\Windows\System32\cmd.exe",
            "CommandLine": r'schtasks.exe /create /tn "Updater" /tr C:\Users\Public\update.exe /sc onlogon /ru SYSTEM',
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
