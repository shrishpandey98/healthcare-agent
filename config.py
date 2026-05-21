"""
config.py – Central configuration for the Healthcare AI Agent.
Column names are mapped to match the REAL Google Sheet headers.
"""
import os
from dotenv import load_dotenv

load_dotenv("env.txt")

# ─── Google Sheets ────────────────────────────────────────────────────────────
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "1tAUIvG5EDaIuHoZEIfyoyV_z3CVSDvYZIMgTABypWcw")
SHEET_NAME: str = os.getenv("SHEET_NAME", "Sheet1")
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")

# ─── WhatsApp Business API (Meta Cloud API) ────────────────────────────────────
WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v19.0")
WHATSAPP_API_URL: str = (
    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
    f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
)

# ─── SMS Fallback (Twilio) ─────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")

# ─── Analytics Email (SendGrid) ────────────────────────────────────────────────
SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
ANALYTICS_FROM_EMAIL: str = os.getenv("ANALYTICS_FROM_EMAIL", "agent@yourhospital.com")
ANALYTICS_TO_EMAILS: list = [
    e.strip() for e in os.getenv("ANALYTICS_TO_EMAILS", "").split(",") if e.strip()
]

# ─── Agent Settings ────────────────────────────────────────────────────────────
DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
ANALYTICS_SCHEDULE: str = os.getenv("ANALYTICS_SCHEDULE", "daily")

# Delay (in minutes) between triggering the agent and actually sending messages.
# Default: 60 minutes (1 hour). Set to 0 to send immediately.
SEND_DELAY_MINUTES: int = int(os.getenv("SEND_DELAY_MINUTES", "60"))

# Timezone for the healthcare system (default: Asia/Kolkata)
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")

# ─── Trigger values (any of these in the trigger column = process this row) ────
TRIGGER_VALUES: set = {"true", "yes", "ready"}

# ─────────────────────────────────────────────────────────────────────────────
# REAL column names from the Google Sheet (mapped to agent variable names)
# Sheet: AI_agent: master_data  /  Tab: Sheet1
# ─────────────────────────────────────────────────────────────────────────────

# --- Existing columns (do NOT rename in sheet) ---
COL_SNO           = "S No."                               # row ID
COL_UHID          = "UHID (XXXXX)"
COL_NAME          = "Patient Name"
COL_PHONE         = "Phone"
COL_AGE           = "Age"
COL_GENDER        = "Gender (M/F)"                        
COL_ADDRESS       = "Address"
COL_DATE_REG      = "Date of registration (DD-MM-YYYY)"
COL_LAST_VISIT    = "Last date of visit"
COL_NEXT_FOLLOWUP = "Next follow-up date = (Last date of visit + Next Follow up duration)"
COL_FOLLOWUP_STATUS = "Follow-up status"
COL_PROCEDURES    = "Procedures (*latest)"
COL_LAST_MSG_SENT = "Last follow up message sent"
COL_LAST_MSG_TIME = "Last follow up message - day and time"
COL_LAST_MSG_CONTENT = "Last follow up message content"

# --- Agent-managed columns (will be added to sheet if missing) ---
COL_ACTION_TYPE     = "action_type"       # follow_up / upsell / feedback
COL_STATUS          = "status"            # pending / in_progress / completed / error
COL_TRIGGER         = "trigger"           # ready / yes / TRUE
COL_MSG_NEEDED      = "message_needed"    # YES / NO
COL_MEDIUM_USED     = "medium_used"       # whatsapp / sms
COL_DELIVERY_STATUS = "delivery_status"   # sent / failed
COL_NOTES           = "notes"             # agent audit log

# Columns that must exist (existing + agent-managed)
REQUIRED_EXISTING_COLUMNS = [
    COL_SNO, COL_UHID, COL_NAME, COL_PHONE,
    COL_LAST_VISIT, COL_PROCEDURES,
]

AGENT_COLUMNS = [
    COL_ACTION_TYPE, COL_STATUS, COL_TRIGGER,
    COL_MSG_NEEDED, COL_MEDIUM_USED, COL_DELIVERY_STATUS, COL_NOTES,
]
