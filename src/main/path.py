import os
import yaml
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
OUTPUT_DIR = ROOT_DIR / "output"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True)
print("ROOT_DIR", ROOT_DIR)
DATA_DIR = ROOT_DIR / "res/data"
LOG_DIR = OUTPUT_DIR / "logs"
SOLIDITY_DIR = SRC_DIR / "solidity"
FIGURE_DIR = OUTPUT_DIR / "figure"
os.chdir(ROOT_DIR)
