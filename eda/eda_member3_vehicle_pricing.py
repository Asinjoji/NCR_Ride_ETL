"""Member 3 EDA: vehicle types, fares, revenue, payments and ratings."""
import eda_common as ec
from eda_common import plt


def per_vehicle(done):
    table = done.groupby("x_vehicle").agg(
        rides=("x_outcome", "size"),
        revenue=("x_value", "sum"),
        avg_fare=("x_value", "mean"),
        avg_distance_km=("x_distance", "mean"),
        avg_price_per_km=("x_price_per_km", "mean"),
        avg_driver_rating=("x_driver_rating", "mean"),
        avg_customer_rating=("x_customer_rating", "mean"),
    )
    return table.sort_values("rides", ascending=False).round(2)


def three_bars(table):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    items = [("avg_fare", "Average fare"),
             ("avg_distance_km", "Average distance (km)"),
             ("avg_price_per_km", "Average price per km")]
    for ax, (col, label) in zip(axes, items):
        labels = [str(i) for i in table.index]
        ax.bar(labels, table[col], color=ec.BLUE)
        ax.set_title(label)
        plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    fig.suptitle("Fare, distance and price per km by vehicle (completed)",
                 fontweight="bold")
    return ec.save_fig(fig, "m3_fare_distance_price.png")


def scatter(done):
    data = done.dropna(subset=["x_value", "x_distance"])
    sample = data.sample(min(5000, len(data)), random_state=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(sample["x_distance"], sample["x_value"], s=6, alpha=0.3,
               color=ec.BLUE)
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Fare")
    ax.set_title("Fare vs distance (5,000 random completed rides)",
                 fontweight="bold")
    return ec.save_fig(fig, "m3_fare_vs_distance.png")


def ratings(done, table):
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    labels = [str(i) for i in table.index]
    width = 0.4
    positions = range(len(labels))
    left.bar([p - width / 2 for p in positions], table["avg_driver_rating"],
             width, label="Driver", color=ec.BLUE)
    left.bar([p + width / 2 for p in positions],
             table["avg_customer_rating"], width, label="Customer",
             color=ec.ORANGE)
    left.set_xticks(list(positions), labels, rotation=40, ha="right")
    left.set_ylim(3, 5)
    left.set_title("Average rating by vehicle type")
    left.legend()
    right.hist(done["x_driver_rating"].dropna(), bins=20, alpha=0.7,
               label="Driver", color=ec.BLUE)
    right.hist(done["x_customer_rating"].dropna(), bins=20, alpha=0.7,
               label="Customer", color=ec.ORANGE)
    right.set_title("Rating distribution")
    right.legend()
    return ec.save_fig(fig, "m3_ratings.png")


def main():
    df, missing = ec.prepare(ec.load_clean())
    done = ec.completed(df)
    f = ec.Findings(3, "Vehicles, pricing, payments and ratings")
    f.bullet(f"Completed rides analysed: {len(done):,}. Fares, distances "
             f"and ratings only exist for completed rides.")

    table = per_vehicle(done)
    f.heading("1. Rides and revenue by vehicle type")
    f.table(table[["rides", "revenue", "avg_fare", "avg_distance_km",
                   "avg_price_per_km"]])
    f.figure(ec.bar(table["rides"], "Completed rides by vehicle type",
                    "m3_rides_by_vehicle.png", ylabel="Rides"), "Rides")
    f.figure(ec.bar(table["revenue"], "Revenue by vehicle type",
                    "m3_revenue_by_vehicle.png", ylabel="Total fare",
                    color=ec.ORANGE), "Revenue")
    share = ec.pct(table["revenue"].iloc[0], table["revenue"].sum())
    f.bullet(f"{table.index[0]} brings the most rides and revenue "
             f"({share:.1f}% of all revenue).")
    f.bullet(f"Average fare ranges from {table['avg_fare'].min():,.0f} to "
             f"{table['avg_fare'].max():,.0f} across vehicle types.")

    f.heading("2. Fare, distance and price per km")
    f.figure(three_bars(table), "Fare, distance, price per km")
    f.figure(scatter(done), "Fare vs distance")
    corr = done["x_value"].corr(done["x_distance"])
    f.bullet(f"Correlation between fare and distance: {corr:.2f}.")
    f.bullet(f"Median price per km: {done['x_price_per_km'].median():.2f}; "
             f"maximum: {done['x_price_per_km'].max():,.0f}.")

    f.heading("3. Payment methods")
    pay = done.dropna(subset=["x_payment"]).groupby("x_payment").agg(
        rides=("x_outcome", "size"), avg_fare=("x_value", "mean"),
        total=("x_value", "sum")).sort_values("rides", ascending=False)
    pay["share_pct"] = ec.pct(pay["rides"], pay["rides"].sum())
    f.table(pay.round(2))
    f.figure(ec.bar(pay["share_pct"], "Share of rides by payment method (%)",
                    "m3_payment_methods.png", ylabel="% of rides",
                    fmt="{:.1f}"), "Payment methods")
    if len(pay):
        f.bullet(f"Most used: {pay.index[0]} "
                 f"({pay['share_pct'].iloc[0]:.1f}% of rides).")

    f.heading("4. Ratings")
    f.figure(ratings(done, table), "Ratings")
    f.bullet(f"Average driver rating: "
             f"{done['x_driver_rating'].mean():.2f}; average customer "
             f"rating: {done['x_customer_rating'].mean():.2f}.")
    f.table(table[["avg_driver_rating", "avg_customer_rating"]])
    f.write([
        "Which vehicle type earns the most, and is that because of volume "
        "or higher fares?",
        "Does a longer distance mean a higher fare? What does the "
        "correlation say?",
        "Which payment method do customers prefer?",
        "Do ratings differ between vehicle types or between drivers and "
        "customers?",
    ])


if __name__ == "__main__":
    main()
