"""Shared helpers for the EDA scripts. The lead adds this file; do not edit.

It loads the cleaned data, finds the columns by their usual names, and
gives every script the same standard columns (all start with "x_").
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "eda_outputs"
FIG_DIR = OUT_DIR / "figures"
CLEAN_FILES = [
    ROOT / "output" / "cleaned_ride_bookings.csv",
    ROOT / "output" / "cleaned_data.csv",
]
RAW_FILE = ROOT / "raw_data" / "ncr_ride_bookings.csv"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
OUTCOMES = ["Completed", "Cancelled by Driver", "Cancelled by Customer",
            "No Driver Found", "Incomplete"]
PLACEHOLDERS = {"", "nan", "none", "na", "n/a", "not applicable", "unknown",
                "0", "<na>"}
BLUE = "#2b6cb0"
ORANGE = "#dd6b20"

ALIASES = {
    "status": ["booking_status", "status"],
    "vehicle": ["vehicle_type", "vehicle"],
    "pickup": ["pickup_location", "pickup"],
    "drop": ["drop_location", "drop"],
    "payment": ["payment_method", "payment"],
    "customer": ["customer_id"],
    "booking_id": ["booking_id"],
    "reason": ["cancellation_reason", "cancel_reason",
               "reason_for_cancellation", "reason"],
    "value": ["booking_value", "booking_value_inr", "fare", "fare_amount",
              "booking_amount"],
    "distance": ["ride_distance_km", "ride_distance", "distance_km",
                 "distance"],
    "vtat": ["avg_vtat_min", "avg_vtat", "vtat"],
    "ctat": ["avg_ctat_min", "avg_ctat", "ctat"],
    "driver_rating": ["driver_rating", "driver_ratings"],
    "customer_rating": ["customer_rating", "customer_ratings"],
}
NUMERIC_KEYS = ["value", "distance", "vtat", "ctat", "driver_rating",
                "customer_rating"]


def load_clean():
    """Read the cleaned CSV that `python pipeline.py` creates in output/."""
    for path in CLEAN_FILES:
        if path.exists():
            print(f"Loading {path.relative_to(ROOT)}")
            return pd.read_csv(path)
    sys.exit("Cleaned data not found in output/. Run pipeline.py first.")


def find(df, key):
    """Return the real column name for a standard key, or None."""
    lower = {c.lower(): c for c in df.columns}
    for name in ALIASES[key]:
        if name in lower:
            return lower[name]
    if key == "reason":
        for low, col in lower.items():
            if "reason" in low and "incomplete" not in low:
                return col
    if key == "value":
        for low, col in lower.items():
            if low.startswith(("booking_value", "fare_amount", "fare_inr")):
                return col
    return None


def clean_labels(series):
    """Trim text and turn placeholders such as 'Not Applicable' into NaN."""
    text = series.astype("string").str.strip()
    return text.mask(text.str.lower().isin(PLACEHOLDERS))


def _timestamps(df):
    """Build one datetime series from whatever date columns exist."""
    lower = {c.lower(): c for c in df.columns}
    for name in ("booking_datetime", "datetime", "timestamp"):
        if name in lower:
            return pd.to_datetime(df[lower[name]], errors="coerce")
    if "date" in lower:
        text = df[lower["date"]].astype(str)
        if "time" in lower:
            text = text + " " + df[lower["time"]].astype(str)
        return pd.to_datetime(text, errors="coerce")
    return pd.Series(pd.NaT, index=df.index)


def prepare(raw):
    """Return (data with standard x_ columns, list of keys not found)."""
    df = raw.copy()
    missing = []
    for key in ALIASES:
        col = find(raw, key)
        if col is None:
            missing.append(key)
            df["x_" + key] = np.nan
        else:
            df["x_" + key] = raw[col]
    for key in NUMERIC_KEYS:
        values = pd.to_numeric(df["x_" + key], errors="coerce")
        df["x_" + key] = values.where(values > 0)
    for key in ["status", "vehicle", "pickup", "drop", "payment",
                "customer", "booking_id", "reason"]:
        df["x_" + key] = clean_labels(df["x_" + key])

    status = df["x_status"].fillna("").str.lower()
    is_cancel = status.str.contains("cancel")
    df["x_outcome"] = np.select(
        [status == "completed", status.str.contains("incomplete"),
         status.str.contains("no driver"),
         is_cancel & status.str.contains("customer"),
         is_cancel & status.str.contains("driver")],
        ["Completed", "Incomplete", "No Driver Found",
         "Cancelled by Customer", "Cancelled by Driver"],
        default="Other",
    )
    df["x_completed"] = df["x_outcome"] == "Completed"
    df["x_cancelled"] = df["x_outcome"].str.startswith("Cancelled")

    stamp = _timestamps(raw)
    df["x_date"] = stamp.dt.normalize()
    df["x_hour"] = stamp.dt.hour
    df["x_month"] = stamp.dt.month
    df["x_month_name"] = stamp.dt.month_name()
    df["x_weekday"] = stamp.dt.day_name()
    df["x_is_weekend"] = stamp.dt.day_of_week >= 5
    df["x_time_of_day"] = np.select(
        [df["x_hour"] < 6, df["x_hour"] < 12, df["x_hour"] < 17,
         df["x_hour"] < 22],
        ["Night", "Morning", "Afternoon", "Evening"], default="Night",
    )
    df["x_time_of_day"] = df["x_time_of_day"].where(df["x_hour"].notna())
    df["x_price_per_km"] = (df["x_value"] / df["x_distance"]).round(2)
    return df, missing


def completed(df):
    """Only rides that were completed (the only rows with real fares)."""
    return df[df["x_completed"]]


def outcome_table(df, by):
    """Bookings, completed, cancelled and their rates for each group."""
    table = df.groupby(by).agg(
        bookings=("x_outcome", "size"),
        completed=("x_completed", "sum"),
        cancelled=("x_cancelled", "sum"),
    )
    table["completion_rate_pct"] = pct(table["completed"], table["bookings"])
    table["cancellation_rate_pct"] = pct(table["cancelled"],
                                         table["bookings"])
    return table


def pct(part, whole):
    """Percentage rounded to 2 decimals (works for numbers and columns)."""
    return np.round(100 * part / whole, 2)


def iqr_outliers(series):
    """Return (count, low limit, high limit) using the 1.5 x IQR rule."""
    data = series.dropna()
    q1, q3 = data.quantile([0.25, 0.75])
    low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return int(((data < low) | (data > high)).sum()), low, high


def save_fig(fig, name):
    """Save a figure in eda_outputs/figures and return its link."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=130, facecolor="white")
    plt.close(fig)
    print(f"  saved eda_outputs/figures/{name}")
    return f"figures/{name}"


def bar(series, title, name, xlabel="", ylabel="", horizontal=False,
        fmt="{:,.0f}", color=BLUE, figsize=(8, 5)):
    """Simple labelled bar chart from a Series. Returns the figure link."""
    fig, ax = plt.subplots(figsize=figsize)
    labels = [str(i) for i in series.index]
    if horizontal:
        bars = ax.barh(labels, series.values, color=color)
        ax.invert_yaxis()
    else:
        bars = ax.bar(labels, series.values, color=color)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.bar_label(bars, labels=[fmt.format(v) for v in series.values],
                 fontsize=8, padding=2)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if horizontal:
        ax.margins(x=0.12)
    else:
        ax.margins(y=0.1)
    return save_fig(fig, name)


class Findings:
    """Collects the facts and chart links of one member into a .md file."""

    def __init__(self, member, title):
        self.member = member
        self.lines = [f"# Member {member}: {title}", ""]

    def heading(self, text):
        self.lines += ["", f"## {text}", ""]

    def bullet(self, text):
        self.lines.append(f"- {text}")

    def figure(self, link, caption):
        self.lines += ["", f"![{caption}]({link})", ""]

    def table(self, df):
        df = df.reset_index()
        cols = [str(c) for c in df.columns]
        self.lines.append("")
        self.lines.append("| " + " | ".join(cols) + " |")
        self.lines.append("|" + "---|" * len(cols))
        for row in df.itertuples(index=False):
            self.lines.append("| " + " | ".join(_cell(v) for v in row) + " |")
        self.lines.append("")

    def write(self, prompts):
        """Write the facts file and (once) an interpretation template."""
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"member{self.member}_findings.md"
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        note = OUT_DIR / f"member{self.member}_interpretation.md"
        if not note.exists():
            body = [f"## Member {self.member}: my interpretation", "",
                    "(Replace each prompt with 1-2 sentences in your own "
                    "words, using the numbers and charts above.)", ""]
            body += [f"- {p}" for p in prompts]
            note.write_text("\n".join(body) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")


def _cell(value):
    if isinstance(value, (bool, np.bool_)):
        return str(value)
    if isinstance(value, (float, np.floating)):
        return f"{value:,.2f}"
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    return str(value)
