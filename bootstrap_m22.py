"""
Barrister_AI
Milestone M2.2
Creates Legal Case Templates

Author:
Saurabh Deshmukh
Prudhvi
Shahid
Aarushi
Shivam
"""

import json
from pathlib import Path


ROOT = Path(__file__).parent

folders = [
    ROOT / "knowledge_base" / "templates",
    ROOT / "scripts" / "setup",
    ROOT / "scripts" / "validation"
]

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)


templates = {

    "cheque_bounce": {

        "domain":"Cheque Bounce",

        "facts":[
            "The accused issued a cheque towards repayment of debt.",
            "The cheque was dishonoured due to insufficient funds.",
            "A statutory notice was served upon the accused."
        ],

        "issues":[
            "Whether Section 138 NI Act is attracted.",
            "Whether legal notice requirements were fulfilled."
        ],

        "arguments":[
            "Complainant proved legally enforceable debt.",
            "Accused denied liability."
        ],

        "analysis":[
            "Court examined bank memo and statutory notice.",
            "Court verified limitation period."
        ],

        "ratio":[
            "Dishonour of cheque constitutes offence under NI Act if statutory conditions are satisfied."
        ],

        "decision":[
            "Conviction",
            "Acquittal"
        ]

    },

    "murder":{

        "domain":"Murder",

        "facts":[
            "Accused allegedly caused death using a deadly weapon.",
            "Eyewitness testimony was produced.",
            "Medical evidence supported prosecution."
        ],

        "issues":[
            "Whether ingredients of Section 302 IPC are established."
        ],

        "arguments":[
            "Prosecution relied upon eyewitnesses.",
            "Defence questioned credibility."
        ],

        "analysis":[
            "Court evaluated motive and forensic evidence."
        ],

        "ratio":[
            "Prosecution must establish guilt beyond reasonable doubt."
        ],

        "decision":[
            "Conviction",
            "Acquittal"
        ]

    },

    "cyber_crime":{

        "domain":"Cyber Crime",

        "facts":[
            "Unauthorized access to computer resources.",
            "Victim suffered financial loss."
        ],

        "issues":[
            "Applicability of Information Technology Act."
        ],

        "arguments":[
            "Digital evidence linked accused.",
            "Defence challenged authenticity."
        ],

        "analysis":[
            "Court examined electronic evidence."
        ],

        "ratio":[
            "Electronic evidence must satisfy admissibility requirements."
        ],

        "decision":[
            "Conviction",
            "Acquittal"
        ]

    },

    "consumer":{

        "domain":"Consumer",

        "facts":[
            "Consumer purchased defective goods.",
            "Seller failed to provide replacement."
        ],

        "issues":[
            "Whether deficiency in service exists."
        ],

        "arguments":[
            "Consumer sought compensation.",
            "Seller denied manufacturing defect."
        ],

        "analysis":[
            "Commission reviewed invoices and expert reports."
        ],

        "ratio":[
            "Consumer entitled to compensation for proven deficiency."
        ],

        "decision":[
            "Compensation Awarded",
            "Complaint Dismissed"
        ]

    },

    "motor_accident":{

        "domain":"Motor Accident",

        "facts":[
            "Road accident caused bodily injuries.",
            "Insurance policy was valid."
        ],

        "issues":[
            "Quantum of compensation."
        ],

        "arguments":[
            "Claimant relied upon medical records.",
            "Insurance company disputed negligence."
        ],

        "analysis":[
            "Tribunal assessed disability percentage."
        ],

        "ratio":[
            "Compensation should be just and reasonable."
        ],

        "decision":[
            "Compensation Granted",
            "Claim Rejected"
        ]

    }

}


template_folder = ROOT/"knowledge_base"/"templates"

print("="*60)
print("CREATING LEGAL TEMPLATES")
print("="*60)

count=0

for name,data in templates.items():

    file=template_folder/f"{name}.json"

    with open(file,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=4)

    print(f"✓ {file.name}")

    count+=1


print("\nVALIDATION")
print("-"*60)

valid=True

for file in template_folder.glob("*.json"):

    try:

        with open(file,encoding="utf-8") as f:
            obj=json.load(f)

        required=[
            "domain",
            "facts",
            "issues",
            "arguments",
            "analysis",
            "ratio",
            "decision"
        ]

        for r in required:
            if r not in obj:
                valid=False
                print(file.name,"Missing",r)

    except Exception as e:

        valid=False
        print(file.name,e)


print()

print("="*60)

if valid:

    print("SUCCESS")
    print(f"{count} Templates Created")
    print("Validation Passed")

else:

    print("Validation Failed")

print("="*60)