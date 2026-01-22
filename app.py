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
    st.info("DEMO: Імітація відправки email")
    st.json({
        "subject": subject,
        "recipients": recipients,
        "body": body
    })

# ===========================
# STREAMLIT APP
# ===========================
st.set_page_config(
    page_title="SuperHumans Surgery Notify (DEMO)",
    layout="centered"
)

st.title("SuperHumans Surgery Notify")
st.caption("ДЕМО форма інформування про операцію")

with st.form("operation_form"):

    # ---------- Блок A: Операція ----------
    st.subheader("Основні дані операції")

    op_date = st.date_input("Дата операції")
    op_time = st.time_input("Час операції")

    op_type = st.selectbox(
        "Тип операції",
        ["Планова", "Ургентна"]
    )

    amputation_stage = st.selectbox(
        "Стадія ампутації",
        ["Первинна", "Ревізійна", "Реампутація"]
    )

    amputation_level = st.selectbox(
        "Вид втручання",
        [
            "Щелепно-лицьова",
            "Пересадка клаптів",
            "Реампутація",
            "Тимпанопластика",
            "Інше"
        ]
    )

    department = st.selectbox(
        "Відділення",
        ["Хірургія", "Ортопедія"]
    )

    operating_room = st.selectbox(
        "Операційна",
        ["№1", "№2"]
    )

    surgeon = st.text_input("Хірург (ПІБ)")
    anesthesiologist = st.text_input("Анестезіолог (ПІБ)")

    # ---------- Блок B: Пацієнт ----------
    st.subheader("Пацієнт")

    patient_name = st.text_input("ПІБ пацієнта")
    patient_dob = st.date_input("Дата народження")
    case_number = st.text_input("Номер історії хвороби")
    diagnosis = st.text_area("Основний діагноз")

    comorbidities = st.multiselect(
        "Супутні захворювання",
        ["Діабет", "Анемія", "ІХС", "Коагулопатія"]
    )

    # ---------- Блок C: Трансфузіологія ----------
    st.subheader("Трансфузіологічний блок")

    blood_loss = st.selectbox(
        "Очікувана крововтрата",
        ["< 500 мл", "500–1000 мл", "> 1000 мл"]
    )

    blood_needed = st.radio(
        "Потреба в крові",
        ["Так", "Можливо", "Ні"]
    )

    blood_components = st.multiselect(
        "Необхідні компоненти",
        ["Еритроцити", "Плазма", "Тромбоцити"]
    )

    blood_group = st.text_input("Група крові (якщо відома)")

    urgency = st.selectbox(
        "Терміновість",
        ["Планово", "Евакуація", "Негайно"]
    )

    # ---------- Блок D: Інші ресурси ----------
    st.subheader("Інші ресурси")

    equipment = st.multiselect(
        "Потрібне обладнання",
        ["Апаратура ШВЛ", "Моніторинг", "Рентген", "УЗД"]
    )

    icu_needed = st.checkbox("Потрібна реанімація")
    special_conditions = st.text_area("Особливі умови")

    # ---------- Блок E: Ручні адресати ----------
    st.subheader("Додаткові адресати")

    notify_operblock = st.checkbox("Операційний блок")
    notify_anesth = st.checkbox("Анестезіологія")
    notify_icu = st.checkbox("Реанімація")
    notify_lab = st.checkbox("Лабораторія")
    notify_sterile = st.checkbox("Стерилізаційна")
    notify_admin = st.checkbox("Адміністрація")
    notify_bloodbank = st.checkbox("Трансфузіологія")

    submitted = st.form_submit_button("Надіслати")

# ===========================
# SUBMIT HANDLER
# ===========================
if submitted:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    recipients = set()

    if blood_needed == "Так":
        recipients.add("Трансфузіологія")

    if icu_needed:
        recipients.add("Реанімація")

    if urgency == "Негайно":
        recipients.update(["Операційний блок", "Анестезіологія"])

    if op_type == "Ургентна":
        recipients.add("Адміністрація")

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

    recipients = sorted(recipients)

    email_subject = f"Операція ({op_type}) — {op_date} {op_time}"
    email_body = f"""
Нова операція зареєстрована

Пацієнт: {patient_name}
Операція: {amputation_level}
Стадія: {amputation_stage}
Дата/час: {op_date} {op_time}
Хірург: {surgeon}
Анестезіолог: {anesthesiologist}

Крововтрата: {blood_loss}
Потреба в крові: {blood_needed}
Компоненти: {", ".join(blood_components)}
Реанімація: {"Так" if icu_needed else "Ні"}

Особливі умови:
{special_conditions}
"""

    st.success("Форма прийнята (DEMO)")
    st.subheader("Дані (як для Google Sheets)")
    st.json(row)

    if recipients:
        st.subheader("Адресати")
        st.write(recipients)

        st.subheader("Email (DEMO)")
        send_email_demo(email_subject, email_body, recipients)
    else:
        st.warning("Жоден підрозділ не обраний для сповіщення")
