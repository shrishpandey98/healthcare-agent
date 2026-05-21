import config
import pytz
from sheet_reader import get_all_rows
from decision_engine import should_send_followup

print("Reading sheet rows...")
try:
    ws, records, headers = get_all_rows()
    print(f"Total rows in sheet: {len(records)}")
    
    for i, row in enumerate(records, start=2):
        should_send, reason = should_send_followup(row)
        print(f"Row {i} | Patient: {row.get('Patient Name')} | Visit Date: {row.get('Last date of visit')} | Phone: {row.get('Phone')} | Status: {'ELIGIBLE' if should_send else 'SUPPRESSED'} | Reason: {reason}")
except Exception as e:
    print(f"Error checking sheet: {e}")
