"""Member 1: extract + structural cleaning (STUB)."""
from etl.common import DEFAULT_SOURCE


def extract(source=DEFAULT_SOURCE):
    """Read the raw CSV (local path or URL), report its size, save a raw copy."""
    raise NotImplementedError("extract: not implemented yet")


def rename_columns(df):
    """T1. snake_case names are easier to code against than 'Avg VTAT'."""
    raise NotImplementedError("rename_columns: not implemented yet")


def standardise_text(df):
    """T2. IDs arrive wrapped in literal quotes; locations/labels need uniform case."""
    raise NotImplementedError("standardise_text: not implemented yet")


def remove_duplicates(df):
    """T3. booking_id is the primary key; repeated keys would double-count rides."""
    raise NotImplementedError("remove_duplicates: not implemented yet")


def convert_dates(df):
    """T4. Merge date + time into one timestamp and derive calendar features."""
    raise NotImplementedError("convert_dates: not implemented yet")
