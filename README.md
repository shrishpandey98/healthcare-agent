# Healthcare Follow-up AI Agent & Manager Dashboard

A modern, web-based control panel and background automation engine for managing patient follow-up communication. The system synchronizes patient records from Google Sheets, runs a localized scheduler to determine eligibility, and automates outgoing messages using Fast2SMS APIs (WhatsApp business API and SMS fallback).

---

## Key Features

- **Google Sheets Synchronization**: Connects to the master patient Google Sheet to read and update states.
- **Smart Eligibility Logic**: Evaluates patient procedures and follow-up dates to determine who requires a follow-up message.
- **WhatsApp Integration**: Sends customized reminders to patient numbers using WhatsApp templates.
- **PythonAnywhere Local Dashboard**: Provides a unified panel to view resource usage, run commands in active consoles, list/search files, and reload web apps.
- **Timezone Aware Scheduling**: Localized scheduler (`Asia/Kolkata` IST) that ensures messages are triggered at the correct local hour.

---

## Directory Structure

```
├── app.py                      # Flask Application Server (Dashboard & Console Proxy)
├── config.py                   # Central settings, schema mappings, and constants
├── decision_engine.py          # Eligibility rules for daily message delivery
├── main.py                     # Daily execution loop and background scheduling
├── message_generator.py        # String and content template generator
├── messenger.py                # Meta Cloud API / Fast2SMS API interface
├── sheet_reader.py             # Read/write access handler for Google Sheets API
├── static_app.js               # Dashboard interface state and interactive views
├── templates_index.html        # Glassmorphic single page dashboard frontend
├── test_connection.py          # Connectivity diagnostics (Google Sheets and API test)
├── .gitignore                  # Prevents committing environment variables and credentials
└── requirements.txt            # Python library dependencies
```

---

## Installation & Setup

### 1. Clone the Repository
Download the files to your local workstation or server.

### 2. Create Virtual Environment & Install Dependencies
Initialize a virtual environment to manage dependencies securely and install from `requirements.txt`:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 3. Local Environment Variables (`env.txt`)
Create a local file named `env.txt` in the root of this project. **This file must not be committed to Git.** Populate it with the following configuration variables:

```ini
# Google Sheets Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here
SHEET_NAME=Sheet1
GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json

# WhatsApp Business / Fast2SMS API Credentials
WHATSAPP_API_KEY=your_fast2sms_whatsapp_key
WHATSAPP_BUSINESS_NUMBER=your_waba_phone_number
WHATSAPP_PHONE_NUMBER_ID=your_waba_phone_number_id
WHATSAPP_TEMPLATE_ID=your_whatsapp_template_id
USE_WHATSAPP_PRIMARY=true

# Twilio SMS Fallback (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=your_twilio_phone_number

# SendGrid Email Analytics (Optional)
SENDGRID_API_KEY=your_sendgrid_api_key
ANALYTICS_FROM_EMAIL=agent@yourhospital.com
ANALYTICS_TO_EMAILS=recipient1@email.com,recipient2@email.com

# PythonAnywhere API credentials (for dashboard proxy)
PYTHONANYWHERE_USERNAME=your_pythonanywhere_username
PYTHONANYWHERE_TOKEN=your_pythonanywhere_api_token

# Agent settings
DRY_RUN=true
LOG_LEVEL=INFO
TIMEZONE=Asia/Kolkata
SEND_DELAY_MINUTES=60
```

### 4. Google Sheets API Credentials
Place your Google service account credentials JSON file in the root directory and name it `credentials.json` (as mapped by `GOOGLE_SERVICE_ACCOUNT_JSON` in your configuration).

---

## Usage

### Running the Dashboard
To start the interactive manager panel locally:
```bash
python app.py
```
Open your web browser and navigate to `http://localhost:5000` to monitor CPU load, reload web apps, manage active consoles, and navigate your server's filesystem.

### Running the Automation Engine
To launch the background AI follow-up loop:
```bash
python main.py
```
This script will read rows from the Google Sheet, evaluate eligibility, register daily trigger queues, and dispatch notifications based on the schedule configured in `config.py`.
