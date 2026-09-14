"""T1070.004 — Indicator Removal: File Deletion (Defense Evasion)

NOTE: intentionally left without a matching Sigma rule in detections/.
This is a real, honest coverage gap used to demonstrate that the pipeline
surfaces techniques nobody has written a detection for yet, rather than
only proving out techniques already covered.
"""

TECHNIQUE_ID = "T1070.004"
NAME = "Indicator Removal: File Deletion"
TACTIC = "defense-evasion"


def simulate():
    return [
        {
            "EventID": 23,
            "Image": r"C:\Windows\System32\cmd.exe",
            "TargetFilename": r"C:\Windows\System32\winevt\Logs\Security.evtx",
            "CommandLine": r"cmd.exe /c del /f /q C:\Windows\System32\winevt\Logs\Security.evtx",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
