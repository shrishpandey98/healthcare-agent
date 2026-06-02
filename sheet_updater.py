"""
sheet_updater.py - Write results back to the Google Sheet using REAL column names.
"""
import logging
from datetime import datetime
import gspread
from config import COL_SNO

logger = logging.getLogger(__name__)


def _find_row_index(ws, row_id, headers):
    """Return 1-indexed row number for the given S No. value."""
    id_col = headers.index(COL_SNO) + 1
    col_values = ws.col_values(id_col)
    for i, val in enumerate(col_values):
        if str(val).strip() == str(row_id).strip():
            return i + 1
    raise ValueError(f"Row with S No.={row_id} not found in sheet.")


def update_row_fields(ws, headers, row_id, fields):
    """Update arbitrary columns in the row identified by S No."""
    try:
        row_idx = _find_row_index(ws, row_id, headers)
    except ValueError as e:
        logger.error(str(e))
        return

    cells_to_update = []
    for col_name, value in fields.items():
        if col_name not in headers:
            logger.warning(f"Column '{col_name}' not in sheet – skipping.")
            continue
        col_idx = headers.index(col_name) + 1
        cells_to_update.append(gspread.Cell(row=row_idx, col=col_idx, value=str(value)))
        logger.debug(f"  [{row_idx},{col_idx}] ({col_name}) = {value!r}")
        
    if cells_to_update:
        ws.update_cells(cells_to_update)


def set_status(ws, headers, row_id, status, notes=""):
    fields = {"status": status}
    if notes:
        fields["notes"] = notes
    update_row_fields(ws, headers, row_id, fields)


def mark_in_progress(ws, headers, row_id):
    set_status(ws, headers, row_id, "in_progress")


def mark_completed(ws, headers, row_id, notes=""):
    set_status(ws, headers, row_id, "completed", notes)


def mark_error(ws, headers, row_id, reason):
    set_status(ws, headers, row_id, "error", reason)


def write_message_result(ws, headers, row_id,
                         message_content, send_date, send_time,
                         medium_used, delivery_status, notes):
    """Write full message delivery result back to the sheet (real column names)."""
    fields = {
        # Real existing columns
        "Last follow up message content":          message_content,
        "Last follow up message sent":             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Last follow up message - day and time":   f"{send_date} {send_time}",
        # Agent-managed columns
        "medium_used":      medium_used,
        "delivery_status":  delivery_status,
        "status":           "completed" if delivery_status == "sent" else "error",
        "notes":            notes,
    }
    update_row_fields(ws, headers, row_id, fields)
