"""
BarristerAI
Milestone 1 - Project Bootstrap

Creates the complete project structure.
"""

from pathlib import Path

ROOT = Path.cwd()

folders = [
    "knowledge_base",
    "knowledge_base/acts",
    "knowledge_base/courts",
    "knowledge_base/domains",
    "knowledge_base/templates",
    "knowledge_base/generated",
    "knowledge_base/exports",

    "src",
    "src/dataset",
    "src/preprocessing",
    "src/clustering",
    "src/supervised",
    "src/bert",
    "src/retrieval",
    "src/mlops",

    "docs",
    "models",
    "logs",
    "tests",
    "reports",
    "presentation",
    "notebooks"
]

files = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "main.py",

    "docs/PROJECT_SCOPE.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
    "docs/CHANGELOG.md",

    "knowledge_base/acts/acts.json",
    "knowledge_base/courts/courts.json",
    "knowledge_base/domains/domains.json",
    "knowledge_base/templates/templates.json"
]

print("=" * 60)
print("Creating Barrister_AI Project Structure")
print("=" * 60)

created_folders = 0
created_files = 0

for folder in folders:
    path = ROOT / folder
    path.mkdir(parents=True, exist_ok=True)
    created_folders += 1

for file in files:
    path = ROOT / file
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

    created_files += 1

print(f"\nFolders Created : {created_folders}")
print(f"Files Created   : {created_files}")

print("\nProject Location")
print(ROOT)

print("\nProject Bootstrap Completed Successfully")

print("=" * 60)