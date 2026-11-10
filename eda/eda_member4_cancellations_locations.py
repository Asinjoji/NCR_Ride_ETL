"""Member 4 EDA: failed bookings, wait times, locations and customers."""
import pandas as pd

import eda_common as ec
from eda_common import plt


def reasons_chart(cancelled):
    data = cancelled.dropna(subset=["x_reason"])
    if data.empty:
        return None, None
    counts = data.groupby(["x_outcome", "x_reason"]).size()
    counts = counts.sort_values(ascending=False).reset_index(name="count")
    labels = [f"{r} ({o.replace('Cancelled by ', '')})"
              for o, r in zip(counts["x_outcome"], counts["x_reason"])]
    series = pd.Series(counts["count"].values, index=labels)
    link = ec.bar(series, "Cancellation reasons", "m4_cancel_reasons.png",
                  xlabel="Cancellations", horizontal=True, figsize=(10, 6))
    return link, counts


def failure_rates(df):
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    vehicle = ec.outcome_table(df, "x_vehicle")
    order = ["Morning", "Afternoon", "Evening", "Night"]
    tod = ec.outcome_table(df, "x_time_of_day").reindex(order).dropna(
        how="all")
    for ax, table, title in [(left, vehicle, "By vehicle type"),
                             (right, tod, "By time of day")]:
        rate = 100 - table["completion_rate_pct"]
        labels = [str(i) for i in table.index]
        bars = ax.bar(labels, rate, color=ec.ORANGE)
        ax.bar_label(bars, labels=[f"{v:.1f}" for v in rate], fontsize=8)
        ax.set_title(title)
        ax.set_ylabel("Not completed (%)")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.suptitle("Share of bookings that were not completed",
                 fontweight="bold")
    return ec.save_fig(fig, "m4_not_completed_rates.png")


def main():
    df, missing = ec.prepare(ec.load_clean())
    f = ec.Findings(4, "Cancellations, service quality and locations")

    f.heading("1. Booking outcomes")
    status = df["x_outcome"].value_counts().reindex(ec.OUTCOMES).dropna()
    share = ec.pct(status, len(df))
    f.figure(ec.bar(share, "Share of bookings by outcome (%)",
                    "m4_status_breakdown.png", ylabel="% of bookings",
                    fmt="{:.1f}"), "Outcomes")
    f.table(pd.DataFrame({"bookings": status, "share_pct": share}))
    f.bullet(f"Only {share.get('Completed', 0):.1f}% of bookings were "
             f"completed; {100 - share.get('Completed', 0):.1f}% were not.")
    cancelled = df[df["x_cancelled"]]
    by_driver = (cancelled["x_outcome"] == "Cancelled by Driver").sum()
    f.bullet(f"Drivers caused {ec.pct(by_driver, len(cancelled)):.1f}% of "
             f"all cancellations.")

    f.heading("2. Why do cancellations happen?")
    link, counts = reasons_chart(cancelled)
    if link:
        f.figure(link, "Cancellation reasons")
        f.bullet(f"Most common reason: {counts['x_reason'].iloc[0]} "
                 f"({counts['x_outcome'].iloc[0]}), "
                 f"{counts['count'].iloc[0]:,} cancellations.")
    else:
        f.bullet("No cancellation reason column was found.")

    f.heading("3. Where and when do bookings fail?")
    f.figure(failure_rates(df), "Not completed rates")

    f.heading("4. Driver arrival time (VTAT)")
    wait = df.groupby("x_outcome")["x_vtat"].agg(["count", "mean"])
    wait = wait[wait["count"] > 0].round(2)
    wait.columns = ["rides_with_time", "avg_arrival_min"]
    f.table(wait)
    f.figure(ec.bar(wait["avg_arrival_min"],
                    "Average driver arrival time (min) by outcome",
                    "m4_vtat_by_outcome.png", ylabel="Minutes",
                    fmt="{:.1f}"), "Arrival time")

    f.heading("5. Locations and routes")
    pick = ec.outcome_table(df.dropna(subset=["x_pickup"]), "x_pickup")
    top = pick.sort_values("bookings", ascending=False).head(10)
    low = pick.sort_values("bookings").head(10)
    f.figure(ec.bar(top["bookings"], "Top 10 pickup locations",
                    "m4_top_pickups.png", xlabel="Bookings",
                    horizontal=True), "Top pickups")
    f.table(top)
    f.bullet("Ten quietest pickup locations: " + ", ".join(low.index) + ".")
    routes = (df["x_pickup"] + " -> " + df["x_drop"]).value_counts()
    f.figure(ec.bar(routes.head(10), "Top 10 routes", "m4_top_routes.png",
                    xlabel="Bookings", horizontal=True, figsize=(10, 6)),
             "Top routes")
    f.bullet(f"Most frequent route: {routes.index[0]} "
             f"({routes.iloc[0]} bookings).")

    f.heading("6. Customers")
    per_customer = df.dropna(subset=["x_customer"]).groupby(
        "x_customer").size()
    repeat = int((per_customer > 1).sum())
    f.bullet(f"{len(per_customer):,} distinct customers; {repeat:,} booked "
             f"more than once ({ec.pct(repeat, len(per_customer)):.2f}%).")
    f.write([
        "How big is the failed-booking problem, and who causes most of it?",
        "What are the main cancellation reasons, and can any be prevented?",
        "Do waiting times differ between completed and cancelled bookings?",
        "Which pickup locations and routes matter most for the business?",
    ])


if __name__ == "__main__":
    main()
