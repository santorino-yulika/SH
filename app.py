import streamlit as st
from datetime import datetime

# ===========================
# DEMO MODE (явно увімкнено)
# ===========================
DEMO_MODE = True

# ===========================
# DEMO EMAIL (MOCK)
# ===========================
def send_email_demo(subject: str, body: str, recipients: list[str]):
    st.info("📧 DEMO: Імітація відправки email")
    st.json({
        "subject": subject,
        "recipients": recipients,
        "body": body
    })

# ===========================
# STREAMLIT APP
# ===========================

st.set_page_config(
    page_title="NotifyOR (DEMO)",
    layout="centered"
)

st.title("🏥 SuperHumans — ДЕМО форма інформування про операцію")

with st.form("operation_form"):

    # ---------- Блок A: Операція ----------
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
        ["Стегно", "Гомілка", "Плече", "Передпліччя", "Пересадка шкіри"]
    )

    department = st.selectbox("Відділення", ["Хірургія", "Ортопедія"])
    operating_room = st.selectbox("Операційна", ["№1", "№2", "№3"])

    surgeon = st.text_input("Хірург (ПІБ)")
    anesthesiologist = st.text_input("Анестезіолог (ПІБ)")

    # ---------- Блок B: Пацієнт ----------
    st.subheader("🔹 Пацієнт")

    patient_name = st.text_input("ПІБ пацієнта")
    patient_dob = st.date_input("Дата народження")
    case_number = st.text_input("Номер історії хвороби")
    diagnosis = st.text_area("Основний діагноз")

    comorbidities = st.multiselect(
        "Супутні захворювання",
        ["Діабет", "Анемія", "ІХС", "Коагулопатія"]
    )

    # ---------- Блок C: Трансфузіологія ----------
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

    # ---------- Блок D: Інші ресурси ----------
    st.subheader("🔹 Інші ресурси")

    equipment = st.multiselect(
        "Потрібне обладнання",
        ["Апаратура ШВЛ", "Моніторинг", "Рентген", "УЗД"]
    )

    icu_needed = st.checkbox("Потрібна реанімація")
    special_conditions = st.text_area("Особливі умови")

    # ---------- Блок E: Додаткові адресати ----------
    st.subheader("🔹 Додаткові адресати (ручний вибір)")

    notify_operblock = st.checkbox("Операційний блок")
    notify_anesth = st.checkbox("Анестезіологія")
    notify_icu = st.checkbox("Реанімація")
    notify_lab = st.checkbox("Лабораторія")
    notify_sterile = st.checkbox("Стерилізаційна")
    notify_admin = st.checkbox("Адміністрація")
    notify_bloodbank = st.checkbox("Трансфузіологія")

    submitted = st.form_submit_button("📩 Надіслати")

# ===========================
# ОБРОБКА ПОДІЇ SUBMIT
# ===========================

if submitted:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === 1) Формуємо "рядок таблиці" (як у майбутньому для Google Sheets) ===
    row = {
        "timestamp": timestamp,
        "op_date": op_date.isoformat(),
        "op_time": op_time.strftime("%H:%M"),
        "op_type": op_type,
        "amputation_stage": amputation_stage,
        "amputation_level": amputation_level,
        "department": department,
        "operating_room": operating_room,
        "surgeon": surgeon,
        "anesthesiologist": anesthesiologist,
        "patient_name": patient_name,
        "patient_dob": patient_dob.isoformat(),
        "case_number": case_number,
        "diagnosis": diagnosis,
        "comorbidities": comorbidities,
        "blood_loss": blood_loss,
        "blood_needed": blood_needed,
        "blood_components": blood_components,
        "blood_group": blood_group,
        "urgency": urgency,
        "equipment": equipment,
        "icu_needed": icu_needed,
        "special_conditions": special_conditions,
    }

    # === 2) Правила автоматичних сповіщень ===
    recipients = set()

    # Правило: кров → трансфузіологія
    if blood_needed == "Так":
        recipients.add("Трансфузіологія")

    # Правило: реанімація
    if icu_needed:
        recipients.add("Реанімація")

    # Правило: негайно → операційний блок + анестезіологія
    if urgency == "Негайно":
        recipients.add("Операційний блок")
        recipients.add("Анестезіологія")

    # Правило: ургентна → адміністрація
    if op_type == "Ургентна":
        recipients.add("Адміністрація")

    # === 3) Додаємо ручні чекбокси ===
    if notify_operblock:
        recipients.add("Операційний блок")
    if notify_anesth:
        recipients.add("Анестезіологія")
    if notify_icu:
        recipients.add("Реанімація")
    if notify_lab:
        recipients.add("Лабораторія")
    if notify_sterile:
        recipients.add("Стерилізаційна")
    if notify_admin:
        recipients.add("Адміністрація")
    if notify_bloodbank:
        recipients.add("Трансфузіологія")

    recipients = sorted(list(recipients))

    # === 4) Формуємо тему та тіло листа (як у продакшені) ===
    email_subject = (
        f"Операція ({op_type}) — {op_date} {op_time} — {amputation_level}"
    )

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

    # === 5) Вивід для ІТ (DEMO-результат) ===
    st.success("✅ Форма прийнята (DEMO-режим)")

    st.subheader("📋 Дані, які були б збережені в Google Sheets")
    st.json(row)

    if recipients:
        st.subheader("📨 Адресати (з урахуванням правил)")
        st.write(recipients)

        st.subheader("📧 Текст листа (DEMO)")
        send_email_demo(email_subject, email_body, recipients)
    else:
        st.warning(
            "⚠️ Жоден відділ не був автоматично чи вручну обраний для сповіщення."
        )
