"""
=========================================================
Barrister_AI
Milestone M3 - Synthetic Dataset Generator
Response 1 of 2

Author:
Saurabh Deshmukh
Prudhvi
Shahid
Aarushi
Shivam
=========================================================
"""

import json
import random
import csv
from pathlib import Path

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

random.seed(42)

ROOT = Path(__file__).parent

TEMPLATE_FOLDER = ROOT / "knowledge_base" / "templates"
GENERATED_FOLDER = ROOT / "knowledge_base" / "generated"
EXPORT_FOLDER = ROOT / "exports"
REPORT_FOLDER = ROOT / "reports"

GENERATED_FOLDER.mkdir(parents=True, exist_ok=True)
EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

NUM_CASES = 50

# -------------------------------------------------------
# Load Templates
# -------------------------------------------------------

templates = []

for file in TEMPLATE_FOLDER.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        templates.append(json.load(f))

if len(templates) == 0:
    raise Exception("No templates found!")

print("=" * 60)
print("Templates Loaded :", len(templates))
print("=" * 60)

# -------------------------------------------------------
# Supporting Data
# -------------------------------------------------------

COURTS = [
    "Supreme Court",
    "Bombay High Court",
    "Delhi High Court",
    "Karnataka High Court",
    "Madras High Court"
]

ACT_SECTION = {
    "Cheque Bounce": (
        "Negotiable Instruments Act",
        "138"
    ),
    "Murder": (
        "Indian Penal Code",
        "302"
    ),
    "Cyber Crime": (
        "Information Technology Act",
        "66"
    ),
    "Consumer": (
        "Consumer Protection Act",
        "35"
    ),
    "Motor Accident": (
        "Motor Vehicles Act",
        "166"
    )
}

# -------------------------------------------------------
# Utility Functions
# -------------------------------------------------------

def pick(items):
    return random.choice(items)


def build_case(template, index):

    domain = template["domain"]

    act, section = ACT_SECTION.get(
        domain,
        ("Unknown Act", "Unknown")
    )

    case = {

        "case_id": f"CASE{index:04d}",

        "domain": domain,

        "act": act,

        "section": section,

        "court": pick(COURTS),

        "facts": " ".join(random.sample(
            template["facts"],
            len(template["facts"])
        )),

        "issues": pick(template["issues"]),

        "arguments": pick(template["arguments"]),

        "analysis": pick(template["analysis"]),

        "ratio": pick(template["ratio"]),

        "decision": pick(template["decision"])

    }

    # Label for supervised learning

    if case["decision"].lower() in [
        "conviction",
        "compensation awarded",
        "compensation granted"
    ]:

        case["label"] = 1

    else:

        case["label"] = 0

    return case


# -------------------------------------------------------
# Dataset Generation
# -------------------------------------------------------

print("\nGenerating Dataset...\n")

dataset = []

for i in range(1, NUM_CASES + 1):

    template = random.choice(templates)

    case = build_case(template, i)

    dataset.append(case)

print(f"{len(dataset)} cases generated successfully.")
# -------------------------------------------------------
# Export JSON
# -------------------------------------------------------

json_file = GENERATED_FOLDER / "legal_cases.json"

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4, ensure_ascii=False)

print("✓ JSON Exported")


# -------------------------------------------------------
# Export CSV
# -------------------------------------------------------

csv_file = EXPORT_FOLDER / "legal_cases.csv"

fieldnames = [
    "case_id",
    "domain",
    "act",
    "section",
    "court",
    "facts",
    "issues",
    "arguments",
    "analysis",
    "ratio",
    "decision",
    "label"
]

with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for row in dataset:
        writer.writerow(row)

print("✓ CSV Exported")


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

print("\nRunning Validation...\n")

required_fields = set(fieldnames)

validation_passed = True

for record in dataset:

    missing = required_fields - set(record.keys())

    if missing:

        validation_passed = False

        print(
            f"Missing fields in {record['case_id']} : {missing}"
        )

if len(dataset) != NUM_CASES:

    validation_passed = False

    print("Dataset size mismatch")

domains = {}

labels = {0: 0, 1: 0}

for record in dataset:

    domains[record["domain"]] = (
        domains.get(record["domain"], 0) + 1
    )

    labels[record["label"]] += 1


# -------------------------------------------------------
# Dataset Report
# -------------------------------------------------------

report_file = REPORT_FOLDER / "dataset_report.txt"

with open(report_file, "w", encoding="utf-8") as report:

    report.write("=" * 60 + "\n")
    report.write("Barrister_AI Dataset Report\n")
    report.write("=" * 60 + "\n\n")

    report.write(f"Total Cases : {len(dataset)}\n\n")

    report.write("Cases by Domain\n")
    report.write("-------------------------\n")

    for d, count in sorted(domains.items()):

        report.write(f"{d} : {count}\n")

    report.write("\n")

    report.write("Label Distribution\n")
    report.write("-------------------------\n")

    report.write(f"Positive (1) : {labels[1]}\n")
    report.write(f"Negative (0) : {labels[0]}\n")

    report.write("\nValidation : ")

    if validation_passed:
        report.write("PASSED\n")
    else:
        report.write("FAILED\n")

print("✓ Dataset Report Created")


# -------------------------------------------------------
# Console Summary
# -------------------------------------------------------

print("\n" + "=" * 60)
print("BARRISTER_AI - M3 COMPLETED")
print("=" * 60)

print(f"Templates Loaded : {len(templates)}")
print(f"Cases Generated  : {len(dataset)}")
print(f"JSON File        : {json_file.name}")
print(f"CSV File         : {csv_file.name}")
print(f"Report           : {report_file.name}")

print("\nDomain Distribution")

for d, count in sorted(domains.items()):
    print(f"  {d:<20} {count}")

print("\nLabel Distribution")
print(f"  Positive : {labels[1]}")
print(f"  Negative : {labels[0]}")

if validation_passed:
    print("\n✅ VALIDATION PASSED")
else:
    print("\n❌ VALIDATION FAILED")

print("=" * 60)