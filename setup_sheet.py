"""
setup_sheet.py - One-time setup: adds agent-required columns to the Google Sheet.
Run ONCE before running the agent: py -3 setup_sheet.py
"""
import sys
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID  = "1tAUIvG5EDaIuHoZEIfyoyV_z3CVSDvYZIMgTABypWcw"
CRED_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Agent columns to add if missing
AGENT_COLUMNS = [
    "action_type",      # follow_up / upsell / feedback
    "status",           # pending / in_progress / completed / error
    "trigger",          # ready / yes / TRUE
    "message_needed",   # YES / NO
    "medium_used",      # whatsapp / sms
    "delivery_status",  # sent / failed
    "notes",            # agent audit log
]

def main():
    print("Healthcare Agent - Sheet Setup")
    print()

    creds  = Credentials.from_service_account_file(CRED_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    ss     = client.open_by_key(SHEET_ID)
    ws     = ss.worksheet("Sheet1")

    headers = ws.row_values(1)
    print(f"Current columns ({len(headers)}): {headers}")
    print()

    added = []
    for col in AGENT_COLUMNS:
        if col not in headers:
            headers.append(col)
            col_idx = len(headers)
            ws.update_cell(1, col_idx, col)
            added.append(col)
            print(f"  Added column: '{col}' at position {col_idx}")
        else:
            print(f"  Already exists: '{col}'")

    print()
    if added:
        print(f"Done. Added {len(added)} new column(s): {added}")
        print()
        print("Next: Set 'action_type', 'status=pending', 'trigger=ready', 'message_needed=YES'")
        print("      for any rows you want the agent to process.")
    else:
        print("All agent columns already present. Sheet is ready.")

    # Show updated columns
    updated_headers = ws.row_values(1)
    print(f"\nFinal columns ({len(updated_headers)}): {updated_headers}")

if __name__ == "__main__":
    main()
