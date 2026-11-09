"""Lead only: run every member's EDA script and build docs/EDA_report.md.

Usage:  python eda/run_all_eda.py            (runs scripts, then report)
        python eda/run_all_eda.py --report   (only rebuild the report)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = ROOT / "eda_outputs"
REPORT = ROOT / "docs" / "EDA_report.md"


def run_scripts():
    for script in sorted(HERE.glob("eda_member*.py")):
        print(f"\n=== {script.name}")
        subprocess.run([sys.executable, str(script)], check=True,
                       cwd=str(ROOT))


def build_report():
    parts = ["# Exploratory Data Analysis: NCR Ride Bookings", "",
             "Each section was written by one team member. Charts are in "
             "`eda_outputs/figures/`.", ""]
    for number in range(1, 5):
        for kind in ("findings", "interpretation"):
            path = OUT_DIR / f"member{number}_{kind}.md"
            if path.exists():
                text = path.read_text(encoding="utf-8")
                parts += [text.replace("](figures/",
                                       "](../eda_outputs/figures/"), ""]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nReport written to {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--report" not in sys.argv:
        run_scripts()
    build_report()
