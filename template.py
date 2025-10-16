import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

# All the files that are needed for this project
list_of_files = [
    "app.py",
    "requirements.txt",
    ".env",
    "setup.py",
    "README.md",

    # Source code
    "src/__init__.py",
    "src/helper.py",
    "src/aws_service.py",
    "src/translator.py",

    # Frontend
    "templates/index.html",
    "static/style.css",
    "static/script.js",

    # Data / uploads
    "uploads/.gitkeep",

    # Research or notebook experiments
    "research/trials.ipynb"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
        logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists.")
