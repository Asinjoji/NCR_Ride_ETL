"""Member 2 EDA: when do people book? Months, weekdays, hours."""
import sys

import eda_common as ec
from eda_common import plt


def two_panel(table, order, title, name, rotate=False):
    """Bookings as bars (left) and completion rate as a line (right)."""
    table = table.reindex(order).dropna(how="all")
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    labels = [str(i) for i in table.index]
    left.bar(labels, table["bookings"], color=ec.BLUE)
    left.set_title("Bookings")
    right.plot(labels, table["completion_rate_pct"], marker="o",
               color=ec.ORANGE)
    right.set_title("Completion rate (%)")
    right.set_ylim(0, 100)
    for ax in (left, right):
        if rotate:
            plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    fig.suptitle(title, fontweight="bold")
    return ec.save_fig(fig, name)


def heatmap(df):
    grid = df.pivot_table(index="x_weekday", columns="x_hour",
                          values="x_outcome", aggfunc="size", fill_value=0)
    grid = grid.reindex(ec.WEEKDAYS).dropna(how="all")
    fig, ax = plt.subplots(figsize=(12, 5))
    image = ax.imshow(grid.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(grid.shape[1]), [int(h) for h in grid.columns])
    ax.set_yticks(range(grid.shape[0]), grid.index)
    ax.set_xlabel("Hour of day")
    fig.colorbar(image, ax=ax, label="Bookings")
    ax.set_title("Bookings by weekday and hour", fontweight="bold")
    return ec.save_fig(fig, "m2_heatmap_weekday_hour.png")


def main():
    df, missing = ec.prepare(ec.load_clean())
    df = df[df["x_hour"].notna()]
    if df.empty:
        sys.exit("No usable date/time column was found in the data.")
    f = ec.Findings(2, "Time and demand patterns")
    f.bullet(f"Bookings analysed: {len(df):,} from "
             f"{df['x_date'].min().date()} to {df['x_date'].max().date()}.")

    month = ec.outcome_table(df, "x_month_name")
    f.heading("1. Bookings by month")
    f.figure(two_panel(month, ec.MONTHS, "Monthly demand",
                       "m2_bookings_by_month.png", rotate=True), "By month")
    f.table(month.reindex(ec.MONTHS).dropna(how="all"))
    top, low = month["bookings"].idxmax(), month["bookings"].idxmin()
    f.bullet(f"Busiest month: {top} ({month.loc[top, 'bookings']:,}); "
             f"quietest: {low} ({month.loc[low, 'bookings']:,}).")

    day = ec.outcome_table(df, "x_weekday")
    f.heading("2. Bookings by weekday")
    f.figure(two_panel(day, ec.WEEKDAYS, "Demand by weekday",
                       "m2_bookings_by_weekday.png", rotate=True),
             "By weekday")
    f.table(day.reindex(ec.WEEKDAYS).dropna(how="all"))
    f.bullet(f"Busiest weekday: {day['bookings'].idxmax()}; "
             f"quietest: {day['bookings'].idxmin()}.")

    hour = ec.outcome_table(df, "x_hour")
    hour.index = hour.index.astype(int)
    f.heading("3. Bookings by hour")
    f.figure(two_panel(hour, sorted(hour.index), "Demand by hour",
                       "m2_bookings_by_hour.png"), "By hour")
    peak = hour["bookings"].idxmax()
    f.bullet(f"Peak hour: {peak}:00 with {hour.loc[peak, 'bookings']:,} "
             f"bookings; quietest hour: {hour['bookings'].idxmin()}:00.")
    f.bullet(f"Completion rate stays between "
             f"{hour['completion_rate_pct'].min():.1f}% and "
             f"{hour['completion_rate_pct'].max():.1f}% across hours.")

    f.heading("4. Weekday and hour together")
    f.figure(heatmap(df), "Heatmap")

    f.heading("5. Time of day and weekends")
    tod = ec.outcome_table(df, "x_time_of_day").reindex(
        ["Morning", "Afternoon", "Evening", "Night"]).dropna(how="all")
    f.figure(ec.bar(tod["bookings"], "Bookings by time of day",
                    "m2_time_of_day.png", ylabel="Bookings"), "Time of day")
    f.table(tod)
    days = df.groupby("x_is_weekend")["x_date"].nunique()
    count = df.groupby("x_is_weekend").size()
    per_day = (count / days).round(1)
    for flag, name in [(False, "weekday"), (True, "weekend")]:
        if flag in per_day.index:
            f.bullet(f"Average bookings per {name} day: {per_day[flag]:,}.")
    spread = (month["bookings"].max() - month["bookings"].min())
    f.bullet(f"Gap between the busiest and quietest month: "
             f"{ec.pct(spread, month['bookings'].mean()):.1f}% of the "
             f"average month.")
    f.write([
        "Which months, weekdays and hours are busiest, and by how much?",
        "Is demand clearly seasonal, or almost flat over time?",
        "What should the company do at peak times?",
    ])


if __name__ == "__main__":
    main()
