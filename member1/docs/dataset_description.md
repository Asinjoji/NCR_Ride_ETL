# Step 2: Dataset Description

**1. What is your data source?**
The *NCR Ride Bookings* dataset (Uber-style ride bookings in the Delhi-NCR region), a public
CSV published on Kaggle as "Uber Ride Analytics Dashboard". The file used is `ncr_ride_bookings.csv`.

**2. Why did you choose it?**
It looks like real operational data: 150,000 bookings, many categorical fields, timestamps,
fares, ratings, cancellations, and *deliberately messy* parts (IDs wrapped in quotes, 1,233 repeated
booking IDs, large blocks of "null"). That gives plenty of room for cleaning, feature creation and
business reports (demand, cancellations, revenue), which is what a future data-science project needs.

**3. What information does it contain?**
One row per booking request (1 Jan to 30 Dec 2024): date and time, booking and customer IDs,
booking status (Completed, Cancelled by Driver, Cancelled by Customer, No Driver Found, Incomplete),
vehicle type (Auto, Bike, eBike, Go Mini, Go Sedan, Premier Sedan, Uber XL), pickup and drop
location (176 pickup areas), driver arrival time (VTAT) and customer turnaround time (CTAT),
cancellation / incomplete-ride reasons, booking value (INR), ride distance (km), driver and
customer ratings, and payment method.

**4. Structured, semi-structured or unstructured?**
**Structured**: fixed columns, one record per row, no nested fields.

**5. What format is the data?**
CSV (comma-separated text, 21 columns, about 25 MB).

**6. How frequently is the data updated?**
It is a **one-off static snapshot** of calendar year 2024, not a live feed, so it is not updated on a
schedule. The pipeline takes a `--source` argument, so a refreshed file or URL can be processed with
no code change.
