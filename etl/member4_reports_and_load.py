"""Member 4: reports and load."""
from etl.common import BASE_DIR, CLEANED_FILE, NA_LABEL, OUTPUT_DIR, REPORTS_DIR, banner


def generate_reports(df):
    """Build every report as a DataFrame and return {file_name: DataFrame}."""
    done = df[df["is_completed"]]
    # working copy for averages/sums: the 0 fillers mean "did not happen", so hide them
    v = df.copy()
    for col in ["booking_value_inr", "ride_distance_km", "avg_vtat_min", "avg_ctat_min",
                "driver_rating", "customer_rating", "fare_per_km"]:
        v[col] = v[col].where(v[col] > 0)
    reports = {}

    status = (df["booking_status"].astype(str).value_counts().rename_axis("booking_status")
              .reset_index(name="bookings"))
    status["share_pct"] = (status["bookings"] / status["bookings"].sum() * 100).round(2)
    reports["booking_status_summary.csv"] = status

    vt = v.groupby("vehicle_type", observed=True).agg(
        bookings=("booking_id", "count"), completed=("is_completed", "sum"),
        total_revenue_inr=("booking_value_inr", "sum"),
        avg_booking_value_inr=("booking_value_inr", "mean"),
        avg_distance_km=("ride_distance_km", "mean"),
        avg_driver_rating=("driver_rating", "mean"),
        avg_customer_rating=("customer_rating", "mean")).reset_index()
    vt["completion_rate_pct"] = (vt["completed"] / vt["bookings"] * 100).round(2)
    reports["vehicle_type_report.csv"] = vt.round(2).sort_values("total_revenue_inr",
                                                                 ascending=False)

    m = df.groupby(["year", "month", "month_name"], observed=True).agg(
        bookings=("booking_id", "count"), completed=("is_completed", "sum"),
        revenue_inr=("booking_value_inr", "sum")).reset_index()
    m["cancelled_or_failed"] = m["bookings"] - m["completed"]
    m["completion_rate_pct"] = (m["completed"] / m["bookings"] * 100).round(2)
    reports["monthly_report.csv"] = m.round(2)

    hr = df.groupby("hour").agg(bookings=("booking_id", "count"),
                                completed=("is_completed", "sum")).reset_index()
    hr["rank_by_bookings"] = hr["bookings"].rank(ascending=False, method="min").astype(int)
    reports["hourly_demand_report.csv"] = hr

    loc = done.groupby("pickup_location").agg(
        completed_rides=("booking_id", "count"),
        revenue_inr=("booking_value_inr", "sum"),
        avg_fare_inr=("booking_value_inr", "mean")).round(2).reset_index()
    loc["rank"] = loc["completed_rides"].rank(ascending=False, method="min").astype(int)
    loc = loc.sort_values(["rank", "pickup_location"])
    reports["top10_pickup_locations.csv"] = loc.head(10)
    reports["bottom10_pickup_locations.csv"] = loc.tail(10).iloc[::-1]

    routes = (done.groupby(["pickup_location", "drop_location"]).size()
              .reset_index(name="completed_rides").sort_values("completed_rides", ascending=False))
    reports["top10_routes.csv"] = routes.head(10)

    cols = ["booking_id", "booking_datetime", "vehicle_type", "pickup_location",
            "drop_location", "ride_distance_km", "booking_value_inr"]
    reports["top10_highest_booking_values.csv"] = done.nlargest(10, "booking_value_inr")[cols]
    reports["bottom10_lowest_booking_values.csv"] = done.nsmallest(10, "booking_value_inr")[cols]

    pay = done.groupby("payment_method", observed=True).agg(
        rides=("booking_id", "count"), revenue_inr=("booking_value_inr", "sum"),
        avg_fare_inr=("booking_value_inr", "mean")).round(2).reset_index()
    pay["share_pct"] = (pay["rides"] / pay["rides"].sum() * 100).round(2)
    reports["payment_method_report.csv"] = pay.sort_values("rides", ascending=False)

    canc = (df[df["cancelled_by"] != NA_LABEL]
            .groupby(["cancelled_by", "reason"], observed=True).size()
            .reset_index(name="count").sort_values("count", ascending=False))
    canc["share_pct"] = (canc["count"] / canc["count"].sum() * 100).round(2)
    reports["cancellation_reasons_report.csv"] = canc

    stat_cols = ["booking_value_inr", "ride_distance_km", "avg_vtat_min", "avg_ctat_min",
                 "driver_rating", "customer_rating", "fare_per_km"]
    reports["summary_statistics.csv"] = v[stat_cols].describe().T.round(2).rename_axis("column").reset_index()

    dow = df.groupby(["day_of_week", "time_of_day"], observed=True).size().reset_index(name="bookings")
    reports["day_and_time_of_day_report.csv"] = dow
    return reports


def load(df, reports):
    """Write the cleaned dataset to output/ and every report to reports/."""
    banner("STEP 3: LOAD")
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    paths = []
    clean_path = OUTPUT_DIR / CLEANED_FILE
    df.to_csv(clean_path, index=False)
    paths.append(clean_path)
    for name, report in reports.items():
        path = REPORTS_DIR / name
        report.to_csv(path, index=False)
        paths.append(path)
    for p in paths:
        print(f"saved  {p.relative_to(BASE_DIR)}")
    return paths
