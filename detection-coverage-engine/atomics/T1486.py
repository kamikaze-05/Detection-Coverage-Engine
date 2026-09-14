"""T1486 — Data Encrypted for Impact (Impact) — ransomware-style mass rename"""

TECHNIQUE_ID = "T1486"
NAME = "Data Encrypted for Impact"
TACTIC = "impact"


def simulate():
    return [
        {
            "EventID": 11,
            "Image": r"C:\Users\Public\enc.exe",
            "TargetFilename": rf"C:\Users\jdoe\Documents\file_{i}.docx.locked",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
        for i in range(5)
    ]
