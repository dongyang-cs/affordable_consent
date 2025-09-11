import os
import yaml
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
RES_DIR = ROOT_DIR / "res"
OUTPUT_DIR = ROOT_DIR / "output"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True)
print("ROOT_DIR", ROOT_DIR)
DATA_DIR = RES_DIR / "data"
CONFIG_DIR = RES_DIR / "config"
LOG_DIR = OUTPUT_DIR / "logs"
SOLIDITY_DIR = SRC_DIR / "solidity"
FIGURE_DIR = OUTPUT_DIR / "figure"
RESULT_DIR = OUTPUT_DIR / "result"
for directory in [LOG_DIR, FIGURE_DIR, RESULT_DIR]:
    if not directory.exists():
        directory.mkdir(parents=True)
os.chdir(ROOT_DIR)
