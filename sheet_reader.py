"""
sheet_reader.py - Read ALL patient rows from Google Sheet.
Decision on who to message is handled by decision_engine.py, not here.
"""
import logging
import gspread
from google.oauth2.service_account import Credentials
from config import (
    GOOGLE_SHEET_ID, SHEET_NAME, GOOGLE_SERVICE_ACCOUNT_JSON,
)

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

from config import REQUIRED_EXISTING_COLUMNS as REQUIRED_COLUMNS


def _get_worksheet():
    creds  = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)


def get_all_rows():
    """
    Returns (worksheet, all_records, headers).
    Validates that required columns exist.
    Raises ValueError if required columns are missing.
    """
    ws      = _get_worksheet()
    headers = ws.row_values(1)
    records = ws.get_all_records()

    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run setup_sheet.py first.")

    logger.info(f"Read {len(records)} total row(s) from sheet.")
    return ws, records, headers
