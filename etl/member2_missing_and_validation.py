"""Member 2: merge columns, missing values, validation (STUB)."""


def merge_reason_columns(df):
    """T5. Three sparse flag/reason pairs -> one 'cancelled_by' + one 'reason' column."""
    raise NotImplementedError("merge_reason_columns: not implemented yet")


def handle_missing(df):
    """T7. Remove every null: label categoricals "Not Applicable", fill numeric nulls with 0."""
    raise NotImplementedError("handle_missing: not implemented yet")


def validate_and_filter(df):
    """T6. Drop physically impossible values. Runs BEFORE nulls are filled with 0."""
    raise NotImplementedError("validate_and_filter: not implemented yet")
