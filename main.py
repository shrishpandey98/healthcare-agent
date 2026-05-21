"""
main.py - Healthcare AI Follow-Up Agent (Automated).

The agent automatically decides who needs a follow-up message
based on visit date rules — no manual trigger columns required.

Rules (decision_engine.py):
  - Patient visited 2-7 days ago
  - No message sent in the last 7 days

Run modes:
  py -3 -X utf8 main.py              → run once + start daily scheduler
  py -3 -X utf8 main.py --dry-run    → safe preview, nothing is sent/written
  py -3 -X utf8 main.py --analytics-now → send analytics report and exit
"""
import sys
import logging
import time
import schedule
import pytz

import config
from config import COL_SNO, COL_NAME
from sheet_reader import get_all_rows
from sheet_updater import mark_error, write_message_result
from decision_engine import filter_followup_rows
from message_generator import generate_message
from messenger import send_message
from analytics_agent import run_analytics

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def process_row(ws, headers, row: dict, channel: str = None) -> None:
    """Full follow-up pipeline for a single patient row."""
    row_id = str(row.get(COL_SNO, "")).strip()
    name   = str(row.get(COL_NAME, row_id)).strip()
    reason = row.get("auto_decision_reason", "")
    logger.info(f"-- Processing S.No={row_id} | {name} ({reason}) --")

    # Build context for message generator
    ctx = {
        "action_type":    "follow_up",
        "patient_name":   name,
        "phone_number":   str(row.get(config.COL_PHONE, "")).strip(),
        "uhid":           str(row.get(config.COL_UHID, "")).strip(),
        "last_visit_date":str(row.get(config.COL_LAST_VISIT, "")).strip(),
        "procedures":     str(row.get(config.COL_PROCEDURES, "")).strip(),
    }

    # Validate phone
    if not ctx["phone_number"]:
        logger.warning(f"  Skipping: no phone number for {name}")
        if not config.DRY_RUN:
            mark_error(ws, headers, row_id, "Missing phone number")
        return

    # Generate message
    try:
        msg = generate_message(ctx)
    except Exception as e:
        logger.error(f"  Message generation failed: {e}")
        if not config.DRY_RUN:
            mark_error(ws, headers, row_id, f"Message generation error: {e}")
        return

    content   = msg["message_content"]
    send_date = msg["send_date"]
    send_time = msg["send_time"]

    logger.info(f"  Send on: {send_date} at {send_time}")
    logger.info(f"  Message: {content[:120]}...")

    # Send message (WhatsApp > SMS fallback or override)
    result     = send_message(
        ctx["phone_number"], 
        content, 
        channel=channel,
        patient_name=name,
        procedure=ctx["procedures"]
    )
    medium     = result["medium_used"]
    dlv_status = result["delivery_status"]
    err_detail = result.get("error_detail", "")

    notes = (
        f"[follow_up] [medium:{medium}] [status:{dlv_status}] "
        f"Auto-selected: {reason}."
        + (f" Error: {err_detail}" if err_detail else "")
    )
    logger.info(f"  Result: {notes}")

    # Write back to sheet
    if not config.DRY_RUN:
        write_message_result(
            ws, headers, row_id,
            message_content=content,
            send_date=send_date,
            send_time=send_time,
            medium_used=medium,
            delivery_status=dlv_status,
            notes=notes,
        )


def run_agent(channel: str = None, ignore_delay: bool = False) -> None:
    logger.info("=" * 60)
    logger.info(f"Follow-Up Agent starting | DRY_RUN={config.DRY_RUN}")
    logger.info(f"Sheet: {config.GOOGLE_SHEET_ID} | Tab: {config.SHEET_NAME}")
    logger.info("=" * 60)

    # ── Delay before sending ────────────────────────────────────────────────────
    if config.SEND_DELAY_MINUTES > 0 and not ignore_delay:
        from datetime import datetime, timedelta
        tz = pytz.timezone(getattr(config, "TIMEZONE", "Asia/Kolkata"))
        send_at = datetime.now(tz) + timedelta(minutes=config.SEND_DELAY_MINUTES)
        logger.info(
            f"Waiting {config.SEND_DELAY_MINUTES} min before sending. "
            f"Messages will go out at {send_at.strftime('%I:%M %p')} local time..."
        )
        time.sleep(config.SEND_DELAY_MINUTES * 60)
        logger.info("Delay complete. Starting message dispatch now.")
    # ────────────────────────────────────────────────────────────────────────────
    try:
        ws, all_rows, headers = get_all_rows()
    except ValueError as e:
        logger.critical(f"Column check failed: {e}")
        return

    # Auto-select eligible follow-up rows
    eligible_rows = filter_followup_rows(all_rows)

    if not eligible_rows:
        logger.info("No patients qualify for follow-up today.")
    else:
        for row in eligible_rows:
            try:
                process_row(ws, headers, row, channel=channel)
            except Exception as e:
                row_id = str(row.get(COL_SNO, "?"))
                logger.error(f"Unexpected error on S.No={row_id}: {e}", exc_info=True)
                if not config.DRY_RUN:
                    mark_error(ws, headers, row_id, f"Unexpected error: {e}")

    logger.info("=" * 60)
    logger.info("Agent run complete.")
    logger.info("=" * 60)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--dry-run" in args:
        config.DRY_RUN = True
        logger.info("DRY_RUN mode enabled via CLI.")

    if "--analytics-now" in args:
        run_analytics()
        sys.exit(0)

    run_agent()

    # Schedule: run once per day at 9:00 AM
    schedule.every().day.at("09:00").do(run_agent)
    # Analytics report at 8:00 AM
    if config.ANALYTICS_SCHEDULE == "weekly":
        schedule.every().monday.at("08:00").do(run_analytics)
    else:
        schedule.every().day.at("08:00").do(run_analytics)

    logger.info("Scheduler active. Runs daily at 09:00. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)
