"""
decision_engine.py - Automatic follow-up eligibility rules.

Scans all patient rows and decides who needs a follow-up message
WITHOUT requiring manual trigger/message_needed columns.

Rules:
  SEND if:
    - Last date of visit was between 2 and 7 days ago
    - No message has been sent in the last 7 days (or never messaged)

  SUPPRESS if:
    - Already messaged within last 7 days
    - Visit was less than 2 days ago (too soon)
    - Visit was more than 7 days ago (too late for post-visit follow-up)
    - No visit date recorded
"""
from datetime import datetime, timedelta
import logging
import pytz
import config

logger = logging.getLogger(__name__)

# ─── Configurable thresholds ──────────────────────────────────────────────────
VISIT_MIN_DAYS   = 2   # Visit must have been at least this many days ago
VISIT_MAX_DAYS   = 7   # Visit must be within this many days
RESEND_COOLDOWN  = 7   # Don't re-message if already sent within this many days

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d %b %Y"]


def _parse_date(val: str):
    """Try multiple date formats. Returns date or None."""
    val = str(val).strip()
    if not val:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


def should_send_followup(row: dict) -> tuple[bool, str]:
    """
    Returns (should_send: bool, reason: str)
    reason explains why the decision was made (for logging/notes).

    Uses these real sheet column names:
      'Last date of visit'         - when the patient last visited
      'Last follow up message sent' - when we last messaged this patient
    """
    tz = pytz.timezone(getattr(config, "TIMEZONE", "Asia/Kolkata"))
    today = datetime.now(tz).date()

    # ── Check visit date ───────────────────────────────────────────────────────
    visit_raw   = row.get("Last date of visit", "")
    visit_date  = _parse_date(visit_raw)

    if not visit_date:
        return False, f"No valid visit date found (value: '{visit_raw}')"

    days_since_visit = (today - visit_date).days

    if days_since_visit < VISIT_MIN_DAYS:
        return False, f"Too soon after visit ({days_since_visit}d ago, min={VISIT_MIN_DAYS}d)"

    if days_since_visit > VISIT_MAX_DAYS:
        return False, f"Visit too long ago ({days_since_visit}d ago, max={VISIT_MAX_DAYS}d)"

    # ── Check cooldown (don't re-send too soon) ────────────────────────────────
    last_sent_raw  = row.get("Last follow up message sent", "")
    last_sent_date = _parse_date(last_sent_raw)

    if last_sent_date:
        days_since_sent = (today - last_sent_date).days
        if days_since_sent < RESEND_COOLDOWN:
            return False, (
                f"Message already sent {days_since_sent}d ago "
                f"(cooldown={RESEND_COOLDOWN}d, last sent={last_sent_date})"
            )

    return True, (
        f"Eligible: visit {days_since_visit}d ago, "
        f"last message={'never' if not last_sent_date else f'{(today-last_sent_date).days}d ago'}"
    )


def filter_followup_rows(all_rows: list[dict]) -> list[dict]:
    """
    Given all sheet rows, return only the ones that should receive a follow-up.
    Also attaches 'auto_decision_reason' to each qualifying row.
    """
    eligible = []
    for row in all_rows:
        name = row.get("Patient Name", row.get("Name", "Unknown"))
        send, reason = should_send_followup(row)
        if send:
            row["auto_decision_reason"] = reason
            eligible.append(row)
            logger.info(f"  ELIGIBLE   | {name}: {reason}")
        else:
            logger.info(f"  SUPPRESSED | {name}: {reason}")

    logger.info(f"Auto-decision: {len(eligible)}/{len(all_rows)} rows selected for follow-up.")
    return eligible
