import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------

SHEET_NAME = "hospital_operations"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"

DEPARTMENTS_EMAILS = {
    "Операційний блок": "operblock@clinic.ua",
    "Анестезіологія": "anesth@clinic.ua",
    "Реанімація": "icu@clinic.ua",
    "Лабораторія": "lab@clinic.ua",
    "Стерилізаційна": "sterile@clinic.ua",
    "Адміністрація": "admin@clinic.ua",
    "Трансфузіологія": "bloodbank@clinic.ua",
}

def send_email(subject, body, recipients):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipients, msg.as_string())

st.set_page_config(page_title="Форма інформування про операцію", layout="centered")
st.title("🏥 Форма інформування про операцію (ампутанти)")

with st.form("operation_form"):

    st.subheader("🔹 Основні дані операції")
    op_date = st.date_input("Дата операції")
    op_time = st.time_input("Час операції")
    op_type = st.selectbox("Тип операції", ["Планова", "Ургентна"])
    amputation_stage = st.selectbox(
        "Стадія ампутації",
        ["Первинна", "Ревізійна", "Реампутація"]
    )
    amputation_level = st.selectbox(
        "Рівень ампутації",
        ["Стегно", "Гомілка", "Плече", "Передпліччя"]
    )
    department = st.selectbox("Відділення", ["Хірургія", "Ортопедія"])
    operating_room = st.selectbox("Операційна", ["№1", "№2", "№3"])
    surgeon = st.text_input("Хірург (ПІБ)")
    anesthesiologist = st.text_input("Анестезіолог (ПІБ)")

    st.subheader("🔹 Пацієнт")
    patient_name = st.text_input("ПІБ пацієнта")
    patient_dob = st.date_input("Дата народження")
    case_number = st.text_input("Номер історії хвороби")
    diagnosis = st.text_area("Основний діагноз")
    comorbidities = st.multiselect(
        "Супутні захворювання",
        ["Діабет", "Анемія", "ІХС", "Коагулопатія"]
    )

    st.subheader("🔹 Трансфузіологічний блок")
    blood_loss = st.selectbox(
        "Очікувана крововтрата",
        ["< 500 мл", "500–1000 мл", "> 1000 мл"]
    )
    blood_needed = st.radio("Потреба в крові", ["Так", "Можливо", "Ні"])
    blood_components = st.multiselect(
        "Необхідні компоненти",
        ["Еритроцити", "Плазма", "Тромбоцити"]
    )
    blood_group = st.text_input("Група крові (якщо відома)")
    urgency = st.selectbox(
        "Терміновість",
        ["Планово", "Терміново", "Негайно"]
    )

    st.subheader("🔹 Інші ресурси")
    equipment = st.multiselect(
        "Потрібне обладнання",
        ["Апаратура ШВЛ", "Моніторинг", "Рентген", "УЗД"]
    )
    icu_needed = st.checkbox("Потрібна реанімація")
    special_conditions = st.text_area("Особливі умови")

    st.subheader("🔹 Додаткові адресати")
    notify_operblock = st.checkbox("Операційний блок")
    notify_anesth = st.checkbox("Анестезіологія")
    notify_icu = st.checkbox("Реанімація")
    notify_lab = st.checkbox("Лабораторія")
    notify_sterile = st.checkbox("Стерилізаційна")
    notify_admin = st.checkbox("Адміністрація")
    notify_bloodbank = st.checkbox("Трансфузіологія")

    submitted = st.form_submit_button("📩 Надіслати")

if submitted:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        timestamp,
        op_date.isoformat(),
        op_time.strftime("%H:%M"),
        op_type,
        amputation_stage,
        amputation_level,
        department,
        operating_room,
        surgeon,
        anesthesiologist,
        patient_name,
        patient_dob.isoformat(),
        case_number,
        diagnosis,
        ", ".join(comorbidities),
        blood_loss,
        blood_needed,
        ", ".join(blood_components),
        blood_group,
        urgency,
        ", ".join(equipment),
        "Так" if icu_needed else "Ні",
        special_conditions,
    ]

    sheet.append_row(row)

    recipients = set()

    # Автоматичні правила
    if blood_needed == "Так":
        recipients.add(DEPARTMENTS_EMAILS["Трансфузіологія"])

    if icu_needed:
        recipients.add(DEPARTMENTS_EMAILS["Реанімація"])

    if urgency == "Негайно":
        recipients.add(DEPARTMENTS_EMAILS["Операційний блок"])
        recipients.add(DEPARTMENTS_EMAILS["Анестезіологія"])

    if op_type == "Ургентна":
        recipients.add(DEPARTMENTS_EMAILS["Адміністрація"])

    # Ручні чекбокси
    if notify_operblock:
        recipients.add(DEPARTMENTS_EMAILS["Операційний блок"])
    if notify_anesth:
        recipients.add(DEPARTMENTS_EMAILS["Анестезіологія"])
    if notify_icu:
        recipients.add(DEPARTMENTS_EMAILS["Реанімація"])
    if notify_lab:
        recipients.add(DEPARTMENTS_EMAILS["Лабораторія"])
    if notify_sterile:
        recipients.add(DEPARTMENTS_EMAILS["Стерилізаційна"])
    if notify_admin:
        recipients.add(DEPARTMENTS_EMAILS["Адміністрація"])
    if notify_bloodbank:
        recipients.add(DEPARTMENTS_EMAILS["Трансфузіологія"])

    email_subject = f"Операція ({op_type}) — {op_date} {op_time} — {amputation_level}"
    email_body = f"""
    Нова операція зареєстрована:

    Дата: {op_date}
    Час: {op_time}
    Тип: {op_type}
    Стадія ампутації: {amputation_stage}
    Рівень ампутації: {amputation_level}
    Відділення: {department}
    Операційна: {operating_room}

    Хірург: {surgeon}
    Анестезіолог: {anesthesiologist}

    Пацієнт: {patient_name}
    Історія хвороби: {case_number}
    Діагноз: {diagnosis}

    Очікувана крововтрата: {blood_loss}
    Потреба в крові: {blood_needed}
    Компоненти: {", ".join(blood_components)}
    Група крові: {blood_group}
    Терміновість: {urgency}

    Потрібна реанімація: {"Так" if icu_needed else "Ні"}
    Особливі умови: {special_conditions}
    """

    if recipients:
        send_email(email_subject, email_body, list(recipients))

    st.success("✅ Операцію збережено та повідомлення надіслані!")
