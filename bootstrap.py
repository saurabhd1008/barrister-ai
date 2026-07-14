"""
==============================================================================
Project        : Barrister_AI
Module         : Project Bootstrap
Milestone      : M1/M2
Description    : Creates the complete Barrister_AI project structure.

Core Engineering Team

Saurabh Deshmukh      - Lead Solution Architect & ML Engineer
Prudhvi               - Data Engineering Lead
Shahid                - Quality Engineering Lead
Aarushi               - Research & Documentation Lead
Shivam                - Validation & Integration Engineer

Institution    : IIT Kanpur - AI & Machine Learning Program
Version        : 1.0.0
==============================================================================

This script is safe to execute multiple times.
"""

from pathlib import Path
from datetime import datetime

# =============================================================================
# PROJECT ROOT
# =============================================================================

ROOT = Path(__file__).resolve().parent

# =============================================================================
# FOLDERS
# =============================================================================

FOLDERS = [

    # Documentation
    "docs",

    # Knowledge Base
    "knowledge_base",
    "knowledge_base/acts",
    "knowledge_base/courts",
    "knowledge_base/domains",
    "knowledge_base/templates",
    "knowledge_base/generated",
    "knowledge_base/exports",

    # Scripts
    "scripts",
    "scripts/setup",
    "scripts/validation",
    "scripts/dataset",
    "scripts/preprocessing",
    "scripts/training",
    "scripts/retrieval",
    "scripts/mlops",
    "scripts/utils",

    # Source Code
    "src",
    "src/common",
    "src/dataset",
    "src/preprocessing",
    "src/clustering",
    "src/supervised",
    "src/bert",
    "src/retrieval",
    "src/mlops",

    # Others
    "datasets",
    "models",
    "reports",
    "logs",
    "tests",
    "presentation",
    "notebooks"
]

# =============================================================================
# FILES
# =============================================================================

FILES = {

    "README.md": "# Barrister_AI\n\nAI Powered Legal Precedent Recommendation Engine\n",

    "TEAM.md":
"""# Core Engineering Team

Saurabh Deshmukh - Lead Solution Architect & ML Engineer

Prudhvi - Data Engineering Lead

Shahid - Quality Engineering Lead

Aarushi - Research & Documentation Lead

Shivam - Validation & Integration Engineer
""",

    "LICENSE":
"""Academic Capstone Project
IIT Kanpur AI & Machine Learning Program
""",

    "CONTRIBUTING.md":
"""# Contribution Guidelines

1. Create feature branch.
2. Commit frequently.
3. Validate before merging.
4. Keep code modular.
""",

    ".gitignore":
"""__pycache__/
*.pyc
.venv/
.vscode/

logs/
models/

knowledge_base/generated/
knowledge_base/exports/
""",

    "requirements.txt": "",

    "main.py":
'''def main():
    print("\\nWelcome to Barrister_AI\\n")


if __name__ == "__main__":
    main()
''',

    "config.py":
'''from pathlib import Path

PROJECT_NAME = "Barrister_AI"
VERSION = "1.0.0"

ROOT_DIR = Path(__file__).resolve().parent

KNOWLEDGE_BASE = ROOT_DIR / "knowledge_base"

DATASET_SIZE = 500

ENCODING = "utf-8"
'''
}

# =============================================================================
# CREATE FOLDERS
# =============================================================================

created_folders = 0

for folder in FOLDERS:

    path = ROOT / folder

    if not path.exists():
        path.mkdir(parents=True)
        created_folders += 1

# =============================================================================
# CREATE __init__.py
# =============================================================================

for folder in ROOT.rglob("*"):

    if folder.is_dir():

        if folder.name not in [
            "datasets",
            "reports",
            "logs",
            "presentation",
            "notebooks",
            "models"
        ]:

            init_file = folder / "__init__.py"

            if not init_file.exists():
                init_file.touch()

# =============================================================================
# CREATE FILES
# =============================================================================

created_files = 0

for filename, content in FILES.items():

    file_path = ROOT / filename

    if not file_path.exists():

        file_path.write_text(content, encoding="utf-8")

        created_files += 1

# =============================================================================
# REPORT
# =============================================================================

report = ROOT / "reports" / "BOOTSTRAP_REPORT.txt"

report.parent.mkdir(exist_ok=True)

with open(report, "w", encoding="utf-8") as f:

    f.write("=" * 60 + "\n")
    f.write("Barrister_AI Bootstrap Report\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Generated : {datetime.now()}\n\n")

    f.write(f"Folders Created : {created_folders}\n")
    f.write(f"Files Created   : {created_files}\n")

    f.write("\nProject Root\n")
    f.write(str(ROOT))

# =============================================================================
# SUMMARY
# =============================================================================

print("=" * 60)
print(" Barrister_AI Bootstrap Completed")
print("=" * 60)

print(f"Project Root     : {ROOT}")
print(f"Folders Created  : {created_folders}")
print(f"Files Created    : {created_files}")
print("\nBootstrap Report : reports/BOOTSTRAP_REPORT.txt")
print("=" * 60)