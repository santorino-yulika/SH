import streamlit as st
import smtplib
from email.message import EmailMessage
from datetime import datetime

# =========================
# SECRETS (Streamlit)
# =========================
EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVERS = st.secrets["EMAIL_RECEIVERS"]  # через кому, якщо декілька

# =========================
# UI
# =========================
st.set_page_config(page_title="Operation Notice", layout="centered")

st.title("Operation Notification Form")
st.caption("Demo version for IT department")

with st.form("operation_form"):
    patient_id = st.text_input("Patient ID")
    operation_type = st.text_input("Operation type")
    operation_date = st.date_input("Operation date")
    operation_time = st.time_input("Operation time")
    surgeon = st.text_input("Surgeon")
    notes = st.text_area("Additional notes")

    submitted = st.form_submit_button("Send notification")

# =========================
# ACTION
# =========================
if submitted:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    email_body = f"""
OPERATION NOTIFICATION

Patient ID: {patient_id}
Operation: {operation_type}
Date: {operation_date}
Time: {operation_time}
Surgeon: {surgeon}

Notes:
{notes}

Submitted at: {timestamp}
"""

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Operation Notice: {patient_id}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_RECEIVERS
        msg.set_content(email_body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        st.success("Notification email sent successfully.")

    except Exception as e:
        st.error("Email sending failed.")
        st.exception(e)

    # =========================
    # GOOGLE SHEETS (DISABLED)
    # =========================
    """
    import gspread
    from google.oauth2.service_account import Credentials

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=SCOPES
