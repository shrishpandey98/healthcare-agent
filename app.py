import os, sys, secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load local env file and override any stale shell vars.
load_dotenv(os.path.join(BASE_DIR, "env.txt"), override=True)

sys.path.insert(0, BASE_DIR)
import os as _os
import config

app = Flask(__name__, template_folder=_os.path.join(BASE_DIR, "templates"))
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hca2026")
app.jinja_env.globals.update(enumerate=enumerate)

# Fix for PythonAnywhere (HTTPS proxy) — prevents CSRF state mismatch in OAuth
app.config["SESSION_COOKIE_SECURE"] = True       # Only send cookie over HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"    # Allow redirect from Google
app.config["SESSION_COOKIE_HTTPONLY"] = True      # Protect from JS access
app.config["SESSION_COOKIE_NAME"] = "hca_session" # Unique name avoids conflicts
# Tell Flask it's behind a trusted HTTPS proxy (PythonAnywhere)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

scheduler = BackgroundScheduler()
scheduler.start()

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_auth_user():
    return {"auth_user": session.get("user")}


@app.route("/login")
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/auth/google/<role>")
def google_login(role: str):
    if role not in ("patient", "hospital"):
        flash("Invalid login role.", "danger")
        return redirect(url_for("login"))

    if not os.getenv("GOOGLE_OAUTH_CLIENT_ID") or not os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"):
        flash("Google SSO is not configured. Add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in env.txt.", "danger")
        return redirect(url_for("login"))

    session["login_role"] = role
    nonce = secrets.token_urlsafe(24)
    session["oauth_nonce"] = nonce
    redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or url_for("google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce, prompt="select_account")


@app.route("/auth/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, nonce=session.pop("oauth_nonce", None))
        if not user_info:
            flash("Unable to fetch Google profile.", "danger")
            return redirect(url_for("login"))

        email = str(user_info.get("email", "")).lower().strip()
        role = session.pop("login_role", "patient")
        allowed_hospital_emails = {
            e.strip().lower()
            for e in os.getenv("HOSPITAL_ALLOWED_EMAILS", "").split(",")
            if e.strip()
        }

        if role == "hospital" and allowed_hospital_emails and email not in allowed_hospital_emails:
            flash("This Google account is not allowed for hospital login.", "danger")
            return redirect(url_for("login"))

        session["user"] = {
            "email": email,
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "role": role,
        }
        # Removed banner per user request
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Google sign in failed: {e}", "danger")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Signed out successfully.", "success")
    return redirect(url_for("login"))

def get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials
    from config import GOOGLE_SHEET_ID, SHEET_NAME, GOOGLE_SERVICE_ACCOUNT_JSON

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # Use local credentials.json (or value from env.txt via config)
    creds = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=SCOPES,
    )
    return (
        gspread.authorize(creds)
        .open_by_key(GOOGLE_SHEET_ID)
        .worksheet(SHEET_NAME)
    )

@app.route("/")
@login_required
def dashboard():
    try:
        ws = get_sheet()
        patients = ws.get_all_records()
        
        # Localize today's date for dashboard computations
        tz = pytz.timezone(getattr(config, "TIMEZONE", "Asia/Kolkata"))
        today_local = datetime.now(tz).date()
        today = str(today_local)
        
        eligible=suppressed=responses=0
        for p in patients:
            v=str(p.get(config.COL_LAST_VISIT,"")).strip()
            status = "suppressed"
            try:
                days=(today_local-datetime.strptime(v,"%Y-%m-%d").date()).days
                if 2<=days<=7: 
                    eligible+=1
                    status = "eligible"
                else: suppressed+=1
            except: suppressed+=1
            p["computed_status"] = status
            if str(p.get("response_received","")).upper()=="YES": responses+=1
        stats={"total":len(patients),"eligible":eligible,"suppressed":suppressed,"responses":responses}
        return render_template("index.html",patients=patients,stats=stats,today=today,config=config,sheet_link="1tAUIvG5EDaIuHoZEIfyoyV_z3CVSDvYZIMgTABypWcw")
    except Exception as e:
        tz = pytz.timezone(getattr(config, "TIMEZONE", "Asia/Kolkata"))
        today_local = datetime.now(tz).date()
        return render_template("index.html",patients=[],stats={},error=str(e),today=str(today_local),config=config,sheet_link="1tAUIvG5EDaIuHoZEIfyoyV_z3CVSDvYZIMgTABypWcw")

@app.route("/add-patient", methods=["POST"])
@login_required
def add_patient():
    try:
        ws=get_sheet(); headers=ws.row_values(1)
        row=[""] * len(headers)
        for col,key in [(config.COL_NAME,"name"),(config.COL_PHONE,"phone"),(config.COL_UHID,"uhid"),(config.COL_LAST_VISIT,"visit_date"),(config.COL_PROCEDURES,"procedures"),(config.COL_AGE,"age"),(config.COL_GENDER,"gender")]:
            if col in headers: row[headers.index(col)]=request.form.get(key,"")
        ws.append_row(row)
        flash("Patient added successfully", "success")
    except Exception as e: flash(f"Error: {e}", "danger")
    return redirect(url_for("dashboard"))

@app.route("/run-agent", methods=["POST"])
@login_required
def run_agent_route():
    try:
        channel = request.form.get("channel", "whatsapp")
        from main import run_agent
        
        # Run agent synchronously immediately (by-passing uWSGI scheduler issues and delay)
        run_agent(channel=channel, ignore_delay=True)
        
        flash(f"Agent executed successfully via {channel.upper()}! Messages have been dispatched.", "success")
    except Exception as e:
        flash(f"Error running agent: {e}", "danger")
    return redirect(url_for("dashboard"))

@app.route("/schedule-agent", methods=["POST"])
@login_required
def schedule_agent():
    try:
        run_datetime_str = request.form.get("run_datetime")
        channel = request.form.get("channel", "whatsapp")
        if not run_datetime_str:
            raise ValueError("No datetime provided.")
        
        # HTML datetime-local format is "YYYY-MM-DDTHH:MM"
        run_date_naive = datetime.fromisoformat(run_datetime_str)
        
        tz = pytz.timezone(getattr(config, "TIMEZONE", "Asia/Kolkata"))
        run_date_aware = tz.localize(run_date_naive)
        
        now_local = datetime.now(tz)
        if run_date_aware <= now_local:
            raise ValueError("Scheduled time must be in the future.")
            
        def run_agent_wrapper():
            from main import run_agent
            run_agent(channel=channel)

        # Schedule the job with timezone-aware datetime
        scheduler.add_job(run_agent_wrapper, 'date', run_date=run_date_aware)
        flash(f"Agent scheduled successfully via {channel.upper()} for {run_date_aware.strftime('%Y-%m-%d %I:%M %p')}", "success")
    except Exception as e:
        flash(f"Error scheduling agent: {e}", "danger")
    return redirect(url_for("dashboard"))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
