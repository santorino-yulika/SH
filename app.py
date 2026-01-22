import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===========================
# CONFIG
# ===========================

DEMO_MODE = False  # False = реально надсилаємо email

DEFAULT_RECEIVER = st.secrets["EMAIL_RECEIVERS"]

# ===========================
# EMAIL SEND
# ===========================

def send_email(subject: str, body: str, recipients: list[str]):
    sender_email = st.secrets["EMAIL_ADDRESS"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())

        st.success("📧 Email успішно надіслано")

    except Exception as e:
        st.error("❌ Помилка відправки email")
        st.exception(e)


def send_email_demo(subject: str, body: str, recipients: list[str]):
    st.info("📧 DEMO MODE — email не надсилається")
    st.json({
        "subject": subject,
        "recipients": recipients,
        "body": body
    })

# ===========================
# STREAMLIT UI
# ===========================

st.set_page_config(
    page_title="SuperHumans Surgery Notify (DEMO)",
    layout="centered"
)

st.title("🏥 SuperHumans Surgery Notify")
st.caption("Демо-форма інформування про операцію")

with st.form("operation_form"):

    st.subheader("🔹 Основні дані операції")

    op_date = st.date_input("Дата операції")
    op_time = st.time_input("Час операції")
    op_type = st.selectbox("Тип операції", ["Планова", "Ургентна"])

    amputation_stage = st.selectbox(
        "Стадія",
        ["Первинна", "Ревізійна", "Реампутація"]
    )

    amputation_level = st.selectbox(
        "Тип операції",
        ["Щелепно-лицьова", "Пересадка клаптів", "Реампутація", "Тимпанопластика", "Інше"]
    )

    department = st.selectbox("Відділення", ["Хірургія", "Ортопедія"])
    operating_room = st.selectbox("Операційна", ["№1", "№2"])

    surgeon = st.text_input("Хірург (ПІБ)")
    anesthesiologist = st.text_input("Анестезіолог (ПІБ)")

    st.subheader("🔹 Пацієнт")

    patient_name = st.text_input("ПІБ пацієнта")
    patient_dob = st.date_input("Дата народження")
    case_number = st.text_input("Номер історії хвороби")
    diagnosis = st.text_area("Діагноз")

    st.subheader("🔹 Трансфузіологія")

    blood_loss = st.selectbox(
        "Очікувана крововтрата",
        ["< 500 мл", "500–1000 мл", "> 1000 мл"]
    )

    blood_needed = st.radio("Потреба в крові", ["Так", "Можливо", "Ні"])

    blood_components = st.multiselect(
        "Компоненти",
        ["Еритроцити", "Плазма", "Тромбоцити"]
    )

    blood_group = st.text_input("Група крові")

    urgency = st.selectbox(
        "Терміновість",
        ["Планово", "Евакуація", "Негайно"]
    )

    st.subheader("🔹 Інше")

    icu_needed = st.checkbox("Потрібна реанімація")
    special_conditions = st.text_area("Особливі умови")

    submitted = st.form_submit_button("📩 Надіслати")

# ===========================
# SUBMIT HANDLER
# ===========================

if submitted:

    recipients = [DEFAULT_RECEIVER]

    email_subject = (
        f"Операція ({op_type}) — {op_date} {op_time} — {amputation_level}"
    )

    email_body = f"""
Нова операція зареєстрована

Дата: {op_date}
Час: {op_time}
Тип: {op_type}
Стадія: {amputation_stage}
Операція: {amputation_level}

Відділення: {department}
Операційна: {operating_room}

Хірург: {surgeon}
Анестезіолог: {anesthesiologist}

Пацієнт: {patient_name}
Історія: {case_number}
Діагноз: {diagnosis}

Крововтрата: {blood_loss}
Потреба в крові: {blood_needed}
Компоненти: {", ".join(blood_components)}
Група крові: {blood_group}

Терміновість: {urgency}
Реанімація: {"Так" if icu_needed else "Ні"}

Особливі умови:
{special_conditions}
"""

    if DEMO_MODE:
        send_email_demo(email_subject, email_body, recipients)
    else:
        send_email(email_subject, email_body, recipients)
