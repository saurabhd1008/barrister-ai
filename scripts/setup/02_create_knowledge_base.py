"""
==============================================================================
Project        : Barrister_AI
Module         : Knowledge Base Generator
Milestone      : M2.1

Generates:
    - Acts
    - Courts
    - Legal Domains

Core Engineering Team

Saurabh Deshmukh      - Lead Solution Architect & ML Engineer
Prudhvi               - Data Engineering Lead
Shahid                - Quality Engineering Lead
Aarushi               - Research & Documentation Lead
Shivam                - Validation & Integration Engineer
==============================================================================
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

KB = ROOT / "knowledge_base"

(KB / "acts").mkdir(parents=True, exist_ok=True)
(KB / "courts").mkdir(parents=True, exist_ok=True)
(KB / "domains").mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# ACTS
# ---------------------------------------------------------------------

acts = [

    {
        "id": "ACT001",
        "name": "Negotiable Instruments Act",
        "year": 1881,
        "section": "138"
    },

    {
        "id": "ACT002",
        "name": "Bharatiya Nyaya Sanhita",
        "year": 2023,
        "section": "103"
    },

    {
        "id": "ACT003",
        "name": "Information Technology Act",
        "year": 2000,
        "section": "66"
    },

    {
        "id": "ACT004",
        "name": "Consumer Protection Act",
        "year": 2019,
        "section": "35"
    },

    {
        "id": "ACT005",
        "name": "Motor Vehicles Act",
        "year": 1988,
        "section": "166"
    }

]

# ---------------------------------------------------------------------
# COURTS
# ---------------------------------------------------------------------

courts = [

    {
        "id": "COURT001",
        "name": "Supreme Court of India"
    },

    {
        "id": "COURT002",
        "name": "Delhi High Court"
    },

    {
        "id": "COURT003",
        "name": "Bombay High Court"
    },

    {
        "id": "COURT004",
        "name": "Gujarat High Court"
    },

    {
        "id": "COURT005",
        "name": "District Court"
    }

]

# ---------------------------------------------------------------------
# DOMAINS
# ---------------------------------------------------------------------

domains = [

    {
        "id": "DOMAIN001",
        "name": "Cheque Bounce",
        "act_id": "ACT001"
    },

    {
        "id": "DOMAIN002",
        "name": "Murder",
        "act_id": "ACT002"
    },

    {
        "id": "DOMAIN003",
        "name": "Cyber Crime",
        "act_id": "ACT003"
    },

    {
        "id": "DOMAIN004",
        "name": "Consumer Complaint",
        "act_id": "ACT004"
    },

    {
        "id": "DOMAIN005",
        "name": "Motor Accident",
        "act_id": "ACT005"
    }

]


# ---------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------

with open(KB / "acts" / "acts.json", "w", encoding="utf-8") as f:
    json.dump(acts, f, indent=4)

with open(KB / "courts" / "courts.json", "w", encoding="utf-8") as f:
    json.dump(courts, f, indent=4)

with open(KB / "domains" / "domains.json", "w", encoding="utf-8") as f:
    json.dump(domains, f, indent=4)

print("=" * 60)
print("Knowledge Base Generated Successfully")
print("=" * 60)

print(f"Acts    : {len(acts)}")
print(f"Courts  : {len(courts)}")
print(f"Domains : {len(domains)}")