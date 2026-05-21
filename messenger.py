"""
messenger.py - Send messages via Fast2SMS WhatsApp (primary),
               Fast2SMS plain SMS (free fallback for India).

Priority order:
  1. WhatsApp via Fast2SMS  (requires active WABA on fast2sms.com)
  2. SMS via Fast2SMS       (requires ₹100+ recharge on fast2sms.com)
"""
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv("env.txt")
logger = logging.getLogger(__name__)

# ── WhatsApp API ──────────────────────────────────────────────────────────
WHATSAPP_API_KEY          = os.getenv("WHATSAPP_API_KEY", "")
WHATSAPP_BUSINESS_NUMBER  = os.getenv("WHATSAPP_BUSINESS_NUMBER", "")
# phone_number_id: get this from fast2sms.com → WhatsApp → your WABA details
WHATSAPP_PHONE_NUMBER_ID  = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_TEMPLATE_ID      = os.getenv("WHATSAPP_TEMPLATE_ID", "1969832674410162")

USE_WHATSAPP_PRIMARY      = os.getenv("USE_WHATSAPP_PRIMARY", "true").lower() == "true"

_whatsapp_ready = bool(WHATSAPP_API_KEY and WHATSAPP_PHONE_NUMBER_ID and USE_WHATSAPP_PRIMARY)
if _whatsapp_ready:
    logger.info("WhatsApp API ready. Number=%s", WHATSAPP_BUSINESS_NUMBER)
elif WHATSAPP_API_KEY and not WHATSAPP_PHONE_NUMBER_ID:
    logger.warning(
        "WhatsApp API key present but WHATSAPP_PHONE_NUMBER_ID is missing in env.txt. "
        "Get it from: fast2sms.com → WhatsApp → WABA Details."
    )
else:
    logger.warning("WhatsApp API not configured — WhatsApp disabled.")

# ── Fast2SMS (Free SMS for India) ─────────────────────────────────────────────
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "")
FAST2SMS_URL     = "https://www.fast2sms.com/dev/bulkV2"

_fast2sms_ready = bool(FAST2SMS_API_KEY)
if _fast2sms_ready:
    logger.info("Fast2SMS SMS fallback ready.")
else:
    logger.warning("Fast2SMS not configured — SMS fallback disabled. Set FAST2SMS_API_KEY in env.txt.")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_whatsapp(phone: str) -> str:
    """Format phone for Twilio WhatsApp: whatsapp:+91XXXXXXXXXX"""
    phone = str(phone).strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+91" + phone
    if not phone.startswith("whatsapp:"):
        phone = "whatsapp:" + phone
    return phone


def _clean_phone(phone: str) -> str:
    """Strip to digits only for Fast2SMS (10-digit Indian number)."""
    phone = str(phone).strip().replace(" ", "").replace("-", "")
    # Remove country code prefix if present
    if phone.startswith("+91"):
        phone = phone[3:]
    elif phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]
    return phone


# ── Core send function ─────────────────────────────────────────────────────────

def _send_whatsapp(phone: str, message: str, patient_name: str = "", procedure: str = "") -> dict:
    """Send via Fast2SMS WhatsApp Template API.

    Using the approved clinic_followup template:
        "Hi {{1}}, how are you feeling after your recent {{2}}? Please reply if you would like to schedule a follow-up appointment with our care team."

    Variable mapping:
        {{1}} = Patient name (e.g. "Rahul")
        {{2}} = Procedure (e.g. "teeth cleaning")
    """
    clean_number = _clean_phone(phone)
    if len(clean_number) == 10:
        clean_number = "91" + clean_number

    # Strip pipe (|) — it's the Fast2SMS variable separator
    safe_message = message.replace("|", " ").replace("\n", " ").strip()
    safe_name    = (patient_name or "your").replace("|", " ").strip()

    # Get procedure (defaults to "general visit")
    procedure = (procedure or "general visit").replace("|", " ")
    
    var1 = safe_name                           # e.g. "Rahul"
    var2 = procedure                           # e.g. "teeth cleaning"

    url = "https://www.fast2sms.com/dev/whatsapp"
    params = {
        "authorization":    WHATSAPP_API_KEY,
        "message_id":       WHATSAPP_TEMPLATE_ID,
        "phone_number_id":  WHATSAPP_PHONE_NUMBER_ID,
        "numbers":          clean_number,
        "variables_values": f"{var1}|{var2}",
    }

    logger.info(
        "  [WHATSAPP PAYLOAD] To=%s | Template=%s | Vars: {{1}}=%s | {{2}}=%s",
        clean_number, WHATSAPP_TEMPLATE_ID, var1, var2
    )

    resp = requests.get(url, params=params)
    data = resp.json()

    if data.get("return") is True:
        logger.info("  [WHATSAPP SENT] -> %s | response=%s", clean_number, data)
        return {"medium_used": "whatsapp(fast2sms)", "delivery_status": "sent"}
    else:
        errors = data.get("errors", {})
        # Give actionable hints for common errors
        if "senderId" in data.get("errors_keys", []):
            hint = (
                "Fast2SMS WhatsApp sender not verified. "
                "Go to fast2sms.com → WhatsApp → verify your WABA number."
            )
        elif "message_id" in data.get("errors_keys", []):
            hint = f"Template ID '{WHATSAPP_TEMPLATE_ID}' not found. Check WHATSAPP_TEMPLATE_ID in env.txt."
        else:
            hint = str(errors)
        logger.error("  [WHATSAPP ERROR] %s | hint: %s", data, hint)
        raise Exception(f"WhatsApp failed: {hint}")


def _send_fast2sms(phone: str, message: str) -> dict:
    """Send plain SMS via Fast2SMS (India only). Requires ₹100+ recharge."""
    clean = _clean_phone(phone)
    payload = {
        "route":    "q",
        "message":  message,
        "language": "english",
        "flash":    0,
        "numbers":  clean,
    }
    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type":  "application/json",
    }
    resp = requests.post(FAST2SMS_URL, json=payload, headers=headers, timeout=10)
    data = resp.json()

    if data.get("return") is True:
        logger.info("  [SMS SENT] Fast2SMS -> %s | response=%s", clean, data)
        return {"medium_used": "sms(fast2sms)", "delivery_status": "sent"}
    else:
        raw_msg = data.get("message", str(data))
        # Give actionable hints for common errors
        if "transaction" in str(raw_msg).lower() or "100" in str(raw_msg):
            hint = "Fast2SMS SMS requires a ₹100+ recharge. Go to fast2sms.com → Wallet → Add Money."
        elif "Invalid Authentication" in str(raw_msg) or data.get("status_code") == 412:
            hint = "Fast2SMS API key is invalid/expired. Go to fast2sms.com → API → regenerate your key and update FAST2SMS_API_KEY in env.txt."
        else:
            hint = raw_msg
        logger.error("  [SMS FAILED] %s", hint)
        return {"medium_used": "sms(fast2sms)", "delivery_status": "failed",
                "error_detail": hint}


def send_message(phone: str, message: str, channel: str = None, **kwargs) -> dict:
    """
    Full messaging pipeline:
      - If channel is 'whatsapp', try WhatsApp. If it fails, fallback to SMS.
      - If channel is 'sms', try SMS only.
      - If channel is None, use default behavior (WhatsApp primary, fallback to SMS).
    """
    # ── Option A: Send via SMS ONLY if channel is explicitly 'sms' ──
    if channel == "sms":
        if _fast2sms_ready:
            try:
                return _send_fast2sms(phone, message)
            except Exception as sms_err:
                logger.error("  [SMS FAILED] Fast2SMS exception: %s", sms_err)
                return {"medium_used": "sms(fast2sms)", "delivery_status": "failed",
                        "error_detail": str(sms_err)}
        else:
            logger.error("  [SMS SKIP] Fast2SMS API not configured.")
            return {"medium_used": "sms(fast2sms)", "delivery_status": "failed",
                    "error_detail": "SMS provider not configured"}

    # ── Option B: Try WhatsApp (if channel is 'whatsapp' or None) ──
    if _whatsapp_ready:
        try:
            # Pass patient_name and procedure if caller supplies it (kwarg)
            patient_name = kwargs.get("patient_name", "")
            procedure = kwargs.get("procedure", "general visit")
            return _send_whatsapp(phone, message, patient_name=patient_name, procedure=procedure)
        except Exception as wa_err:
            logger.error("  [WHATSAPP FAILED] %s", wa_err)
            return {"medium_used": "whatsapp(fast2sms)", "delivery_status": "failed",
                    "error_detail": str(wa_err)}
    else:
        logger.info("  [WHATSAPP SKIP] WhatsApp API not configured.")

    # ── Option C: Use SMS as fallback only if WhatsApp is not configured ──
    if _fast2sms_ready:
        try:
            return _send_fast2sms(phone, message)
        except Exception as sms_err:
            logger.error("  [SMS FAILED] Fast2SMS exception: %s", sms_err)
            return {"medium_used": "sms(fast2sms)", "delivery_status": "failed",
                    "error_detail": str(sms_err)}

    # ── Option D: Nothing configured ──
    logger.error("  [NO SENDER] Neither Twilio nor Fast2SMS is configured.")
    return {"medium_used": "none", "delivery_status": "failed",
            "error_detail": "No messaging provider configured"}
