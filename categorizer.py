"""
categorizer.py – Validate row and determine branch using REAL column names.
"""
import logging
from config import (
    COL_ACTION_TYPE, COL_NAME, COL_PHONE,
    COL_LAST_VISIT, COL_PROCEDURES, COL_MSG_NEEDED, COL_UHID, COL_SNO,
)

logger = logging.getLogger(__name__)

VALID_ACTION_TYPES = {"follow_up", "upsell", "feedback"}


def _require(row, *cols):
    missing = [c for c in cols if not str(row.get(c, "")).strip()]
    if missing:
        raise ValueError(f"Required field(s) empty: {missing}")


def categorize(row):
    """
    Validate the row using real sheet column names.
    Returns action context dict or raises ValueError.
    """
    action_type = str(row.get(COL_ACTION_TYPE, "")).strip().lower()

    if action_type not in VALID_ACTION_TYPES:
        raise ValueError(
            f"Unrecognized action_type: '{action_type}'. "
            f"Expected one of: {VALID_ACTION_TYPES}"
        )

    # Common required fields for all branches
    _require(row, COL_NAME, COL_PHONE, COL_UHID)

    # Branch-specific required fields
    if action_type in ("follow_up", "feedback"):
        _require(row, COL_LAST_VISIT)
    elif action_type == "upsell":
        _require(row, COL_PROCEDURES)

    msg_needed_raw = str(row.get(COL_MSG_NEEDED, "YES")).strip().upper()
    message_needed = msg_needed_raw in {"YES", "TRUE", "1"}

    return {
        "action_type":     action_type,
        "message_needed":  message_needed,
        "patient_name":    str(row.get(COL_NAME, "")).strip(),
        "phone_number":    str(row.get(COL_PHONE, "")).strip(),
        "uhid":            str(row.get(COL_UHID, "")).strip(),
        "last_visit_date": str(row.get(COL_LAST_VISIT, "")).strip(),
        "procedures":      str(row.get(COL_PROCEDURES, "")).strip(),
        "row_id":          str(row.get(COL_SNO, "")).strip(),
    }
