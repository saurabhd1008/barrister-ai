"""
BarristerAI
Milestone 1 Validation
"""

from pathlib import Path
import platform

ROOT = Path.cwd()

required_folders = [
    "knowledge_base",
    "knowledge_base/acts",
    "knowledge_base/courts",
    "knowledge_base/domains",
    "knowledge_base/templates",
    "knowledge_base/generated",
    "knowledge_base/exports",
    "src",
    "docs",
    "models",
    "tests",
    "reports",
    "presentation"
]

required_files = [
    "README.md",
    "requirements.txt",
    "main.py",
    ".gitignore"
]

passed = 0
failed = 0

print("=" * 60)
print("BarristerAI Validation Report")
print("=" * 60)

print(f"\nPython Version : {platform.python_version()}")

print("\nChecking Folders")

for folder in required_folders:

    if (ROOT / folder).exists():
        print(f"PASS   {folder}")
        passed += 1
    else:
        print(f"FAIL   {folder}")
        failed += 1

print("\nChecking Files")

for file in required_files:

    if (ROOT / file).exists():
        print(f"PASS   {file}")
        passed += 1
    else:
        print(f"FAIL   {file}")
        failed += 1

print("\n" + "=" * 60)

print(f"Passed : {passed}")
print(f"Failed : {failed}")

if failed == 0:
    print("\nPROJECT STATUS : READY")
else:
    print("\nPROJECT STATUS : FIX ISSUES")

print("=" * 60)

report = ROOT / "reports" / "M1_Validation_Report.txt"

with open(report, "w") as f:

    f.write("BarristerAI Milestone 1 Validation\n")
    f.write("=" * 40 + "\n")
    f.write(f"Passed : {passed}\n")
    f.write(f"Failed : {failed}\n")

    if failed == 0:
        f.write("\nSTATUS : READY\n")
    else:
        f.write("\nSTATUS : FIX ISSUES\n")

print("\nValidation report generated:")
print(report)