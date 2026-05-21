"""
message_generator.py - Generate personalized follow-up messages using Groq LLM.
Falls back to template if API fails.
"""
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv("env.txt")
logger = logging.getLogger(__name__)

# ─── Groq setup ───────────────────────────────────────────────────────────────
_groq_available = False
_groq_client = None

try:
    from groq import Groq
    _key = os.getenv("GROQ_API_KEY", "")
    if _key:
        _groq_client = Groq(api_key=_key)
        _groq_available = True
        logger.info("Groq LLM ready.")
    else:
        logger.warning("GROQ_API_KEY not set — LLM disabled.")
except Exception as e:
    logger.warning(f"Groq not available: {e}")

GROQ_MODEL       = "llama-3.3-70b-versatile"  # Current recommended Groq model
SEND_TIME        = "09:30"
DAYS_AFTER_VISIT = 2
DATE_FORMATS     = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"]


def _calc_send_schedule(last_visit_date: str) -> tuple:
    for fmt in DATE_FORMATS:
        try:
            base = datetime.strptime(str(last_visit_date).strip(), fmt)
            return (base + timedelta(days=DAYS_AFTER_VISIT)).strftime("%Y-%m-%d"), SEND_TIME
        except (ValueError, AttributeError):
            continue
    return datetime.today().strftime("%Y-%m-%d"), SEND_TIME


def _groq_message(ctx: dict) -> str:
    prompt = (
        f"You are a healthcare assistant. Generate a warm, professional follow-up WhatsApp message for a patient.\n\n"
        f"Patient Details:\n"
        f"- Name: {ctx['patient_name']}\n"
        f"- Last visit date: {ctx['last_visit_date']}\n"
        f"- Procedure(s): {ctx.get('procedures', 'general visit') or 'general visit'}\n\n"
        f"CRITICAL RULES:\n"
        f"1. Start directly with 'Hi {ctx['patient_name']}'.\n"
        f"2. Keep it under 280 characters.\n"
        f"3. Use a caring and empathetic tone.\n"
        f"4. Ask how they are feeling after their procedure/visit.\n"
        f"5. Offer to schedule a follow-up appointment.\n"
        f"6. End the message EXACTLY with: '- Your Care Team'\n"
        f"7. DO NOT use emojis.\n"
        f"8. OUTPUT ONLY THE EXACT MESSAGE TEXT. No introductory phrases, no markdown."
    )

    response = _groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150,
    )

    msg = response.choices[0].message.content.strip()

    # Strip any leftover markdown wrappers
    if msg.startswith("```"):
        lines = msg.split("\n")
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        msg = "\n".join(lines).strip()

    return msg


def _template_message(**ctx) -> str:
    name       = ctx.get("patient_name", "Patient")
    last_visit = ctx.get("last_visit_date", "your recent visit")
    procedures = ctx.get("procedures", "")
    note       = f" ({procedures})" if procedures else ""
    return (
        f"Hi {name}! We hope you are recovering well after your visit on "
        f"{last_visit}{note}. Please reach out if you have any concerns. "
        f"Reply YES to book a follow-up. - Your Care Team"
    )


def generate_message(ctx: dict) -> dict:
    """Returns: {message_content, send_date, send_time}"""
    send_date, send_time = _calc_send_schedule(ctx.get("last_visit_date", ""))

    if _groq_available:
        try:
            content = _groq_message(ctx)
            logger.info("  Groq LLM message generated.")
        except Exception as e:
            logger.warning(f"  Groq failed ({e}), using template.")
            content = _template_message(**ctx)
    else:
        content = _template_message(**ctx)
        logger.info("  Template message generated.")

    return {"message_content": content, "send_date": send_date, "send_time": send_time}
