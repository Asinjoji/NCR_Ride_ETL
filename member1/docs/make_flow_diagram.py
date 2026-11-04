"""Draws docs/etl_flow_diagram.png (run: python docs/make_flow_diagram.py)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

boxes = [
    ("Data Source", "ncr_ride_bookings.csv (150,000 rows x 21 cols)", "#e8eef7"),
    ("EXTRACT", "read CSV, print records/columns, save raw copy to raw_data/", "#d6e4f7"),
    ("VALIDATE", "range checks: ratings 1-5, fare/distance > 0, pickup != drop", "#fdf0d5"),
    ("CLEAN", "rename, fix quotes, standardise text, remove duplicates, handle nulls", "#fbe0d0"),
    ("TRANSFORM", "dates, merge columns, types, calculated cols, categories, outliers, sort", "#e1f0dc"),
    ("GENERATE REPORTS", "14 reports: status, vehicle, monthly, hourly, top/bottom 10 ...", "#ece0f5"),
    ("LOAD", "output/cleaned_ride_bookings.csv  +  reports/*.csv", "#d6e4f7"),
]
fig, ax = plt.subplots(figsize=(8, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(boxes) * 1.6)
ax.axis("off")
for i, (title, sub, color) in enumerate(boxes):
    y = (len(boxes) - 1 - i) * 1.6 + 0.2
    ax.add_patch(FancyBboxPatch((0.8, y), 8.4, 1.0, boxstyle="round,pad=0.05",
                                fc=color, ec="#333333", lw=1.2))
    ax.text(5, y + 0.66, title, ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(5, y + 0.28, sub, ha="center", va="center", fontsize=8.5)
    if i < len(boxes) - 1:
        ax.annotate("", xy=(5, y - 0.45), xytext=(5, y - 0.05),
                    arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.5))
out = Path(__file__).with_name("etl_flow_diagram.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print("saved", out)
