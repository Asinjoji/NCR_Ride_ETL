"""Member 1 EDA: data overview, quality, distributions, correlations."""
import numpy as np
import pandas as pd

import eda_common as ec
from eda_common import plt

NUMBERS = {
    "x_value": "Fare (booking value)",
    "x_distance": "Distance (km)",
    "x_vtat": "Driver arrival time (min)",
    "x_ctat": "Trip time (min)",
    "x_driver_rating": "Driver rating",
    "x_customer_rating": "Customer rating",
}


def column_summary(raw):
    """One row per column: type, blanks, zeros, distinct values."""
    rows = []
    for col in raw.columns:
        numeric = pd.api.types.is_numeric_dtype(raw[col])
        zeros = int((raw[col] == 0).sum()) if numeric else 0
        rows.append({"column": col, "type": str(raw[col].dtype),
                     "blanks": int(raw[col].isna().sum()),
                     "zeros": zeros, "distinct": int(raw[col].nunique())})
    return pd.DataFrame(rows).set_index("column")


def histograms(done):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, (col, label) in zip(axes.ravel(), NUMBERS.items()):
        data = done[col].dropna()
        if data.empty:
            ax.set_visible(False)
            continue
        ax.hist(data, bins=30, color=ec.BLUE, edgecolor="white")
        ax.set_title(label)
        ax.set_ylabel("Completed rides")
    fig.suptitle("Distributions (completed rides)", fontweight="bold")
    return ec.save_fig(fig, "m1_distributions.png")


def boxplots(done):
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    items = [("x_value", "Fare"), ("x_distance", "Distance (km)"),
             ("x_price_per_km", "Price per km")]
    for ax, (col, label) in zip(axes, items):
        data = done[col].dropna()
        if data.empty:
            ax.set_visible(False)
            continue
        ax.boxplot(data)
        ax.set_title(label)
        ax.set_xticks([])
    fig.suptitle("Spread and outliers (completed rides)",
                 fontweight="bold")
    return ec.save_fig(fig, "m1_boxplots.png")


def correlation(done):
    cols = list(NUMBERS) + ["x_price_per_km"]
    labels = [NUMBERS.get(c, "Price per km") for c in cols]
    corr = done[cols].corr()
    fig, ax = plt.subplots(figsize=(8, 7))
    image = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), labels, rotation=40, ha="right")
    ax.set_yticks(range(len(cols)), labels)
    for i in range(len(cols)):
        for j in range(len(cols)):
            value = corr.values[i, j]
            if not np.isnan(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center",
                        fontsize=8)
    fig.colorbar(image, ax=ax, shrink=0.8)
    ax.set_title("Correlation of numeric columns", fontweight="bold")
    return ec.save_fig(fig, "m1_correlation.png"), corr


def main():
    raw = ec.load_clean()
    df, missing = ec.prepare(raw)
    done = ec.completed(df)
    f = ec.Findings(1, "Data overview and quality")

    f.heading("1. Size and structure")
    f.bullet(f"Cleaned dataset: {len(raw):,} rows x {raw.shape[1]} columns.")
    if ec.RAW_FILE.exists():
        rows = len(pd.read_csv(ec.RAW_FILE, usecols=[0]))
        f.bullet(f"Raw file: {rows:,} rows, so the pipeline removed "
                 f"{rows - len(raw):,} rows.")
    if missing:
        f.bullet("Columns this EDA could not find: " + ", ".join(missing))
    f.bullet(f"Completed rides: {len(done):,} "
             f"({ec.pct(len(done), len(df)):.1f}% of all bookings).")
    f.table(column_summary(raw))

    f.heading("2. Missing values and zeros")
    nulls = int(raw.isna().sum().sum())
    f.bullet(f"Blank cells left in the cleaned data: {nulls:,}.")
    f.bullet("Cancelled and failed bookings never had a fare, distance or "
             "rating. If the pipeline filled those blanks with 0, the zeros "
             "are placeholders, so this EDA treats 0 as 'no value' and "
             "uses completed rides for money, distance and ratings.")
    if df["x_booking_id"].notna().any():
        repeats = int(df["x_booking_id"].duplicated().sum())
        f.bullet(f"Repeated Booking IDs in the cleaned data: {repeats:,}.")

    f.heading("3. Distributions")
    f.figure(histograms(done), "Histograms of numeric columns")

    f.heading("4. Outliers")
    rows = []
    for col, label in [("x_value", "Fare"), ("x_distance", "Distance"),
                       ("x_price_per_km", "Price per km")]:
        count, low, high = ec.iqr_outliers(done[col])
        rows.append({"column": label, "outliers": count,
                     "lower limit": round(low, 2),
                     "upper limit": round(high, 2)})
    f.table(pd.DataFrame(rows).set_index("column"))
    f.figure(boxplots(done), "Box plots")

    f.heading("5. Correlations")
    link, corr = correlation(done)
    f.figure(link, "Correlation heatmap")
    pair = corr.loc["x_value", "x_distance"]
    f.bullet(f"Correlation between fare and distance: {pair:.2f}.")

    f.heading("6. Summary statistics (completed rides)")
    stats = done[list(NUMBERS) + ["x_price_per_km"]].describe().T.round(2)
    f.table(stats)
    f.write([
        "Is the data clean enough to analyse? What did the pipeline fix?",
        "Which columns have outliers, and should they be removed or kept?",
        "Which numeric columns move together (or not at all)?",
    ])


if __name__ == "__main__":
    main()
