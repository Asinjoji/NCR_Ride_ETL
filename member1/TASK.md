# Member 1 task

**What you do:** Steps 2, 3 and 5 of the assignment: the dataset description, the flow diagram, `extract()`, and transformations 1-4.

**Before you start:** Nothing: you go first.

**Your files:** `etl/member1_extract_structural.py, docs/dataset_description.md, docs/etl_flow_diagram.png, docs/make_flow_diagram.py`

## Steps (PowerShell, inside the `NCR_Ride_Bookings_ETL` folder)

1. Get the latest code (clone the first time, `git pull` afterwards)
```powershell
git clone https://github.com/Abhijithsk/NCR_Ride_Bookings_ETL.git
cd NCR_Ride_Bookings_ETL
git pull origin main
```
2. Create your branch
```powershell
git checkout -b feature/member1-extract-structural
pip install -r requirements-dev.txt
```
3. Copy your code in (this replaces the stub)
```powershell
Copy-Item ..\member_code\member1\etl\*.py etl\ -Force
Copy-Item ..\member_code\member1\docs\* docs\ -Force
```
If the paths fail, drag the files from the `member_code\member1` folder into the matching folders and choose Replace.
Then open the file and **read it**: you will be asked to explain it.

4. Check it
```powershell
flake8 .
pytest
python check_member.py 1
```
You should see: `flake8` prints nothing; pytest ends with **5 passed, 11 skipped**; the checker ends with
**CHECK OK after Member 1: 148,767 rows x 27 columns**.


5. Screenshot: Windows + Shift + S around the `[01]`-`[04]` lines and the CHECK OK line.

6. Save and upload
```powershell
git add etl docs
git status
git commit -m "feat: extract and structural cleaning (rename, text, duplicates, dates) + dataset docs"
git push -u origin feature/member1-extract-structural
```
`git status` must list only your own files. If it lists anything else (for example `__pycache__` or `*_raw_copy.csv`), stop and tell the lead.

7. On GitHub click **Compare & pull request**, fill in the template, paste your screenshot, **Create pull request**,
wait for the green tick, and ask the lead to review and merge.

## Questions you must be able to answer
- Why do booking IDs contain quotes, and how do you remove them?
- Why drop duplicates by `booking_id` and not only whole rows? What is the 0.8% trade-off?
- What does `extract()` print and save, and why save a raw copy?
- Why combine `date` and `time` into one datetime?
