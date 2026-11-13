# Member 3: Vehicles, pricing, payments and ratings

- Completed rides analysed: 92,248. Fares, distances and ratings only exist for completed rides.

## 1. Rides and revenue by vehicle type


| x_vehicle | rides | revenue | avg_fare | avg_distance_km | avg_price_per_km |
|---|---|---|---|---|---|
| Auto | 22,970 | 11,636,666.00 | 506.60 | 25.99 | 34.00 |
| Go Mini | 18,404 | 9,340,882.00 | 507.55 | 25.98 | 33.53 |
| Go Sedan | 16,550 | 8,473,799.00 | 512.01 | 25.98 | 34.65 |
| Bike | 13,921 | 7,081,699.00 | 508.71 | 26.00 | 33.87 |
| Premier Sedan | 11,158 | 5,688,549.00 | 509.82 | 25.97 | 33.72 |
| eBike | 6,480 | 3,262,001.00 | 503.40 | 26.34 | 32.45 |
| Uber XL | 2,765 | 1,395,787.00 | 504.81 | 25.74 | 33.66 |


![Rides](figures/m3_rides_by_vehicle.png)


![Revenue](figures/m3_revenue_by_vehicle.png)

- Auto brings the most rides and revenue (24.8% of all revenue).
- Average fare ranges from 503 to 512 across vehicle types.

## 2. Fare, distance and price per km


![Fare, distance, price per km](figures/m3_fare_distance_price.png)


![Fare vs distance](figures/m3_fare_vs_distance.png)

- Correlation between fare and distance: 0.01.
- Median price per km: 17.70; maximum: 1,667.

## 3. Payment methods


| x_payment | rides | avg_fare | total | share_pct |
|---|---|---|---|---|
| UPI | 41,500 | 508.55 | 21,104,861.00 | 44.99 |
| Cash | 22,922 | 508.75 | 11,661,552.00 | 24.85 |
| Uber Wallet | 11,116 | 505.95 | 5,624,188.00 | 12.05 |
| Credit Card | 9,240 | 509.97 | 4,712,151.00 | 10.02 |
| Debit Card | 7,470 | 505.57 | 3,776,631.00 | 8.10 |


![Payment methods](figures/m3_payment_methods.png)

- Most used: UPI (45.0% of rides).

## 4. Ratings


![Ratings](figures/m3_ratings.png)

- Average driver rating: 4.23; average customer rating: 4.40.

| x_vehicle | avg_driver_rating | avg_customer_rating |
|---|---|---|
| Auto | 4.23 | 4.40 |
| Go Mini | 4.23 | 4.40 |
| Go Sedan | 4.23 | 4.41 |
| Bike | 4.23 | 4.40 |
| Premier Sedan | 4.23 | 4.40 |
| eBike | 4.23 | 4.40 |
| Uber XL | 4.24 | 4.40 |

