"""T1059.001 — Command and Scripting Interpreter: PowerShell (Execution)"""

TECHNIQUE_ID = "T1059.001"
NAME = "PowerShell"
TACTIC = "execution"


def simulate():
    return [
        {
            "EventID": 1,
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "ParentImage": r"C:\Windows\explorer.exe",
            "CommandLine": "powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgAKABOAGUAdw...",
            "User": "CORP\\jdoe",
            "Hostname": "WKSTN-07",
        }
    ]
