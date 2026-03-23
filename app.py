import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import requests
import uuid
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_ID = "019d0ffe-8561-7638-8151-d347f82de15f"

AUTH_BASE64 = "MDE5ZDBmZmUtODU2MS03NjM4LTgxNTEtZDM0N2Y4MmRlMTVmOjRiMDMwNzgyLTdhYTYtNGVlYy1iOWVjLTdmZmY3NmRkMTc5OA=="

def get_gigachat_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {AUTH_BASE64}"
    }

    payload = "scope=GIGACHAT_API_PERS"

    response = requests.post(url, headers=headers, data=payload, verify=False)

    if response.status_code != 200:
        raise Exception(f"OAUTH ERROR {response.status_code}: {response.text}")

    return response.json()["access_token"]

def check_with_gigachat(text, token):
    url = "https://ngw.devices.sberbank.ru/api/v2/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat:latest",
        "messages": [
            {
                "role": "system",
                "content": "Ты строгий преподаватель. Проверяй работу по ГОСТ."
            },
            {
                "role": "user",
                "content": text[:12000]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)

    if response.status_code != 200:
        raise Exception(f"GigaChat ERROR {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

def format_gost(doc):
    for section in doc.sections:
        section.left_margin = Cm(3)
        section.right_margin = Cm(1)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)

    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            continue
        for run in paragraph.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
        paragraph.paragraph_format.line_spacing = 1.5

def add_title_page(doc, institution, student, group, faculty, department, topic, supervisor, year, work_type):
    title_doc = Document()
    section = title_doc.sections[0]
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    p = title_doc.add_paragraph(institution.upper())
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True

    title_doc.add_paragraph()

    if faculty or department:
        p = title_doc.add_paragraph(f"{faculty}\n{department}".strip())
        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for _ in range(5):
        title_doc.add_paragraph()

    p = title_doc.add_paragraph(work_type)
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for _ in range(3):
        title_doc.add_paragraph()

    p = title_doc.add_paragraph("на тему:")
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    p = title_doc.add_paragraph(topic.upper())
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for _ in range(6):
        title_doc.add_paragraph()

    p = title_doc.add_paragraph(f"Выполнил(а): {group}")
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    p = title_doc.add_paragraph(student.upper())
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    for _ in range(2):
        title_doc.add_paragraph()

    p = title_doc.add_paragraph("Руководитель:")
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    p = title_doc.add_paragraph(supervisor)
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    for _ in range(5):
        title_doc.add_paragraph()

    p = title_doc.add_paragraph(f"ГОРОД — {year}")
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for element in reversed(title_doc.element.body):
        doc.element.body.insert(0, element)

st.set_page_config(page_title="AI Thesis Assistant", layout="wide")
st.title("🎓 AI Thesis Assistant")

# ─── РАСШИРЕННЫЕ СПИСКИ ─────────────────────────────────────────────

russia_universities = [
    "МГУ им. М.В. Ломоносова (Москва)",
    "СПбГУ (Санкт-Петербург)",
    "НИУ ВШЭ (Москва)",
    "МФТИ (Долгопрудный)",
    "МГТУ им. Н.Э. Баумана (Москва)",
    "РАНХиГС (Москва)",
    "РЭУ им. Плеханова (Москва)",
    "СПбПУ Петра Великого (Санкт-Петербург)",
    "УрФУ (Екатеринбург)",
    "КФУ (Казань)",
    "НГУ (Новосибирск)",
    "ТГУ (Томск)",
    "ЮФУ (Ростов-на-Дону)",
    "СФУ (Красноярск)",
    "ДВФУ (Владивосток)",
    "МИФИ (Москва)",
    "МАИ (Москва)",
    "МИРЭА (Москва)",
    "Финансовый университет (Москва)",
    "Первый МГМУ им. Сеченова (Москва)",
    "РНИМУ им. Пирогова (Москва)",
    "БФУ им. Канта (Калининград)",
    "ТюмГУ (Тюмень)",
    "Самарский университет",
    "ПГНИУ (Пермь)",
    "ВолГУ (Волгоград)",
    "ОмГУ (Омск)",
    "ЧелГУ (Челябинск)",
    "КубГУ (Краснодар)",
    "СГУ (Саратов)",
    "ИГУ (Иркутск)",
    "АлтГУ (Барнаул)",
    "КГПУ им. Астафьева (Красноярск)",
    "РГГУ (Москва)",
    "МПГУ (Москва)",
    "РГПУ им. Герцена (СПб)",
    "МТУСИ (Москва)",
    "МГЮА (Москва)",
    "РУДН (Москва)",
    "МИСиС (Москва)",
    "ТПУ (Томск)",
    "СибГУ им. Решетнёва (Красноярск)",
    "НГТУ (Новосибирск)",
    "СПбГЭУ (Санкт-Петербург)",
    "ГУУ (Москва)",
    "Другие / вручную"
]

hakassia_universities = [
    "ХГУ им. Н.Ф. Катанова (Абакан)",
    "Хакасский технический институт СФУ (Абакан)",
    "Саяно-Шушенский филиал СФУ (Саяногорск)",
    "Другие / вручную"
]

russia_colleges = [
    "Петровский колледж (Санкт-Петербург)",
    "Колледж №26 Архитектуры (Москва)",
    "Технологический колледж №34 (Москва)",
    "Московский финансовый колледж",
    "Колледж РАНХиГС (Москва)",
    "Колледж МГУ",
    "Колледж РЭУ им. Плеханова",
    "Колледж связи №54 (Москва)",
    "Волгоградский технологический колледж",
    "Астраханский политехнический колледж",
    "Калининградский бизнес-колледж",
    "Новосибирский колледж ИТ",
    "Екатеринбургский колледж транспорта",
    "Казанский медицинский колледж",
    "Самарский медицинский колледж",
    "Ростовский колледж связи",
    "Пермский колледж экономики",
    "Иркутский педколледж",
    "Омский промышленно-экономический колледж",
    "Челябинский энергетический колледж",
    "Краснодарский торгово-экономический колледж",
    "Другие / вручную"
]

hakassia_colleges = [
    "Хакасский политехнический колледж (Абакан)",
    "Колледж ХГУ им. Катанова",
    "Абаканский строительный техникум",
    "Абаканский медицинский колледж",
    "Хакасский колледж технологий и сервиса",
    "Черногорский горно-строительный техникум",
    "Саянский техникум экономики",
    "Другие / вручную"
]

russia_schools = [
    "Физтех-лицей им. Капицы",
    "СУНЦ МГУ",
    "Лицей №31 (Челябинск)",
    "Лицей «Вторая школа»",
    "Лицей №239 (СПб)",
    "СУНЦ НГУ",
    "Лицей НИУ ВШЭ",
    "Школа №179 (Москва)",
    "Школа «Летово»",
    "Лицей №1535",
    "Школа №57",
    "Гимназия №56 (СПб)",
    "Академическая гимназия СПбГУ",
    "Гимназия №116 (СПб)",
    "Школа №619 (СПб)",
    "Гимназия №1514 (Москва)",
    "Лицей №1580 при МГТУ Баумана",
    "Школа №1502 «Энергия»",
    "Другие / вручную"
]

hakassia_schools = [
    "Лицей им. Булакина (Абакан)",
    "Лицей №7 (Саяногорск)",
    "Хакасская гимназия-интернат",
    "Гимназия (Абакан)",
    "Лицей им. Баженова (Черногорск)",
    "СОШ №1 (Абакан)",
    "СОШ №25 (Абакан)",
    "СОШ №11 (Абакан)",
    "СОШ №19 (Черногорск)",
    "Другие / вручную"
]

st.sidebar.header("Учебное заведение")

region = st.sidebar.selectbox("Регион", ["Россия", "Хакасия"])
education_type = st.sidebar.selectbox("Тип", ["ВУЗ", "Колледж", "Школа"])

if education_type == "ВУЗ":
    data = hakassia_universities if region == "Хакасия" else russia_universities
elif education_type == "Колледж":
    data = hakassia_colleges if region == "Хакасия" else russia_colleges
else:
    data = hakassia_schools if region == "Хакасия" else russia_schools

raw = st.sidebar.selectbox("Выбор", data)
institution = st.sidebar.text_input("Или вручную", value=raw if "Другие" not in raw else "")

st.sidebar.header("Данные")
student = st.sidebar.text_input("ФИО", "Иванов Иван Иванович")
group = st.sidebar.text_input("Группа", "11А")
faculty = st.sidebar.text_input("Факультет", "")
department = st.sidebar.text_input("Кафедра", "")
topic = st.sidebar.text_input("Тема", "Исследование...")
supervisor = st.sidebar.text_input("Руководитель", "Петрова А.А.")
year = st.sidebar.text_input("Год", "2026")
work_type = st.sidebar.selectbox("Тип работы", ["Курсовая", "Диплом"])

uploaded_file = st.file_uploader("Загрузите .docx", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if st.button("Проверить и оформить"):
        try:
            token = get_gigachat_token()
            result = check_with_gigachat(text, token)

            st.subheader("Отчёт")
            st.write(result)

            add_title_page(doc, institution, student, group, faculty, department, topic, supervisor, year, work_type)
            format_gost(doc)

            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)

            st.download_button("Скачать файл", data=bio, file_name="готовый.docx")

        except Exception as e:
            st.error(str(e))
else:
    st.info("Загрузите файл")
