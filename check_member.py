"""Checkpoint: runs the REAL data through the pipeline up to a member and verifies the result.

Usage:  python check_member.py 1      (or 2, 3, 4)
"""
import sys

import pipeline

# member -> (rows, columns) expected after that member's steps
EXPECTED = {1: (148_767, 27), 2: (148_767, 23), 3: (148_767, 30)}


def fail(msg):
    print(f"\nCHECK FAILED: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in "1234":
        sys.exit("usage: python check_member.py <1|2|3|4>")
    member = int(sys.argv[1])
    try:
        if member == 4:
            clean, reports = pipeline.run_etl_pipeline()
            if len(reports) < 3:
                fail("fewer than 3 reports")
            if int(clean.isna().sum().sum()):
                fail("the cleaned dataset still contains nulls")
            if clean.shape != EXPECTED[3]:
                fail(f"clean shape {clean.shape}, expected {EXPECTED[3]}")
            print(f"\nCHECK OK after Member 4: {len(reports)} reports, "
                  f"clean {clean.shape[0]:,} rows x {clean.shape[1]} columns, 0 null values")
            return
        df = pipeline.extract()
        df, _ = pipeline.transform(df, upto_member=member)
    except NotImplementedError as exc:
        fail(f"a previous member's code is still a stub ({exc}). Run: git pull origin main")
    if df.shape != EXPECTED[member]:
        fail(f"shape {df.shape}, expected {EXPECTED[member]}")
    extra = ""
    if member >= 2:
        nulls = int(df.isna().sum().sum())
        if nulls:
            fail(f"{nulls} null values left: {df.isna().sum()[df.isna().sum() > 0].to_dict()}")
        extra = ", 0 null values"
    print(f"\nCHECK OK after Member {member}: {df.shape[0]:,} rows x {df.shape[1]} columns{extra}")


if __name__ == "__main__":
    main()
