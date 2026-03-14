import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate
from io import BytesIO
import csv
import datetime
import os
import requests
import base64
import io
import pandas as pd
import docx

st.set_page_config(page_title="Smart Paper Generator", page_icon="📝", layout="wide")

if "lang" not in st.session_state:
    st.session_state.lang = "kz"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "is_registered" not in st.session_state:
    st.session_state.is_registered = False

locales = {
    "ru": {
        "title": "📝 Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
        "nav_gen": "📄 Генератор статей",
        "nav_reg": "👤 Регистрация",
        "sidebar_title": "⚙️ Настройки статьи",
        "lbl_lang": "Основной язык статьи",
        "lbl_sec": "Секция",
        "lbl_type": "Тип статьи",
        "lbl_mrnti": "МРНТИ / IRSTI",
        "sec_meta": "1. Основные метаданные",
        "lbl_title": "Название статьи",
        "lbl_authors": "Авторы",
        "lbl_authors_help": "Например: Имя Фамилия1, Имя Фамилия2",
        "lbl_affil": "Аффилиации (Место работы/учебы)",
        "lbl_affil_help": "1 Университет, Город, Страна; email",
        "lbl_email": "Email для корреспонденции",
        "sec_text": "2. Текст статьи (IMRAD Файлы)",
        "lbl_abstract": "Аннотация (до 300 слов)",
        "lbl_kw": "Ключевые слова",
        "lbl_kw_help": "Слово 1; слово 2; слово 3 (от 3 до 10 слов)",
        "lbl_intro": "Введение (.txt или .docx)",
        "lbl_methods": "Материалы и методы (.txt или .docx)",
        "lbl_results": "Результаты (.txt или .docx)",
        "lbl_conclusion": "Заключение (.txt или .docx)",
        "lbl_ref_manager": "📚 Менеджер литературы",
        "lbl_ref_style": "Стиль цитирования",
        "lbl_fig_manager": "📊 Менеджер рисунков и таблиц",
        "sec_trans": "3. Переводы метаданных",
        "trans_info": "По требованиям журнала необходимо предоставить название, авторов, аннотацию и ключевые слова на двух других языках.",
        "gen_btn": "🚀 Сгенерировать статью",
        "err_abs_len": "⚠️ Аннотация слишком длинная: {count} слов. Максимум: 300.",
        "succ_abs_len": "Слов в аннотации: {count}/300",
        "err_fill_req": "Пожалуйста, заполните хотя бы Название и Авторов.",
        "err_gen": "Произошла ошибка при генерации: ",
        "succ_gen": "✅ Документ успешно сгенерирован! Загрузка начнется автоматически.",
        "btn_dl": "⬇️ Скачать .docx файл вручную",
        "reg_header": "📝 Регистрация исследователя",
        "reg_name": "ФИО (Полностью)",
        "reg_email": "Ваш Email",
        "reg_phone": "Номер телефона",
        "reg_org": "Организация / Университет",
        "reg_pos": "Должность / Статус (например: Докторант)",
        "reg_submit": "Зарегистрироваться",
        "reg_success": "✅ Вы успешно зарегистрированы! Теперь вам доступен генератор статей.",
        "reg_info": "Вы можете перейти в раздел «Генератор статей».",
        "reg_req_msg": "🔒 Для создания статьи необходимо заполнить форму регистрации. Перейдите во вкладку «Регистрация» выше.",
        "reg_err_fill": "Пожалуйста, заполните Имя, Email и Телефон.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "ЕНУ им. Л.Н. Гумилева — Кафедра физической и экономической географии",
    },
    "kz": {
        "title": "📝 Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · Химия / География · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
        "nav_gen": "📄 Мақала генераторы",
        "nav_reg": "👤 Тіркелу",
        "sidebar_title": "⚙️ Мақала баптаулары",
        "lbl_lang": "Мақаланың негізгі тілі",
        "lbl_sec": "Секция",
        "lbl_type": "Мақала түрі",
        "lbl_mrnti": "МРНТИ / IRSTI",
        "sec_meta": "1. Негізгі метадеректер",
        "lbl_title": "Мақаланың атауы",
        "lbl_authors": "Авторлар",
        "lbl_authors_help": "Мысалы: Аты Жөні1, Аты Жөні2",
        "lbl_affil": "Аффилиация (Жұмыс/оқу орны)",
        "lbl_affil_help": "1 Университет, Қала, Ел; email",
        "lbl_email": "Корреспонденцияға арналған email",
        "sec_text": "2. Мақала мәтіні (IMRAD Файлдары)",
        "lbl_abstract": "Аңдатпа (300 сөзге дейін)",
        "lbl_kw": "Түйінді сөздер",
        "lbl_kw_help": "Сөз 1; сөз 2; сөз 3 (3-тен 10 сөзге дейін)",
        "lbl_intro": "Кіріспе (.txt немесе .docx)",
        "lbl_methods": "Материалдар мен әдістер (.txt немесе .docx)",
        "lbl_results": "Нәтижелер (.txt немесе .docx)",
        "lbl_conclusion": "Қорытынды (.txt немесе .docx)",
        "lbl_ref_manager": "📚 Әдебиеттер менеджері",
        "lbl_ref_style": "Дәйексөз стилі",
        "lbl_fig_manager": "📊 Суреттер мен кестелер менеджері",
        "sec_trans": "3. Метадеректер аудармасы",
        "trans_info": "Журнал талаптарына сәйкес атауын, авторларын, аңдатпасын және түйінді сөздерін басқа екі тілде ұсыну қажет.",
        "gen_btn": "🚀 Мақаланы генерациялау",
        "err_abs_len": "⚠️ Аңдатпа тым ұзын: {count} сөз. Максимум: 300.",
        "succ_abs_len": "Аңдатпадағы сөз саны: {count}/300",
        "err_fill_req": "Кем дегенде Атауын және Авторларын толтырыңыз.",
        "err_gen": "Генерация кезінде қате пайда болды: ",
        "succ_gen": "✅ Құжат сәтті генерацияланды! Жүктеп алу автоматты түрде басталады.",
        "btn_dl": "⬇️ .docx файлын қолмен жүктеп алу",
        "reg_header": "📝 Зерттеушіні тіркеу",
        "reg_name": "Аты-жөні (Толық)",
        "reg_email": "Сіздің Email",
        "reg_phone": "Телефон нөмірі",
        "reg_org": "Ұйым / Университет",
        "reg_pos": "Қызметі / Мәртебесі (мысалы: Докторант)",
        "reg_submit": "Тіркелу",
        "reg_success": "✅ Сіз жүйеге сәтті тіркелдіңіз! Енді мақала генераторы қолжетімді.",
        "reg_info": "Сіз «Мақала генераторы» бөліміне өтіп, мақала жасай аласыз.",
        "reg_req_msg": "🔒 Мақала жасау үшін тіркелу формасын толтыру қажет. Жоғарыдағы «Тіркелу» бөліміне өтіңіз.",
        "reg_err_fill": "Аты-жөні, Email және Телефонды толтырыңыз.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ — Физикалық және экономикалық география кафедрасы",
    },
    "en": {
        "title": "📝 Smart Paper Generator",
        "subtitle": "L.N. Gumilyov ENU Bulletin · Chemistry / Geography · 2025",
        "btn_theme_dark": "🌙 Dark mode",
        "btn_theme_light": "☀️ Light mode",
        "nav_gen": "📄 Paper Generator",
        "nav_reg": "👤 Registration",
        "sidebar_title": "⚙️ Paper Settings",
        "lbl_lang": "Primary Language",
        "lbl_sec": "Section",
        "lbl_type": "Paper Type",
        "lbl_mrnti": "IRSTI / МРНТИ",
        "sec_meta": "1. Basic Metadata",
        "lbl_title": "Article Title",
        "lbl_authors": "Authors",
        "lbl_authors_help": "E.g.: Firstname Lastname1, Firstname Lastname2",
        "lbl_affil": "Affiliations",
        "lbl_affil_help": "1 University, City, Country; email",
        "lbl_email": "Correspondence Email",
        "sec_text": "2. Main Text (IMRAD Files)",
        "lbl_abstract": "Abstract (up to 300 words)",
        "lbl_kw": "Keywords",
        "lbl_kw_help": "Keyword 1; keyword 2; keyword 3 (3 to 10 words)",
        "lbl_intro": "Introduction (.txt or .docx)",
        "lbl_methods": "Materials and Methods (.txt or .docx)",
        "lbl_results": "Results (.txt or .docx)",
        "lbl_conclusion": "Conclusion (.txt or .docx)",
        "lbl_ref_manager": "📚 Reference Manager",
        "lbl_ref_style": "Citation Style",
        "lbl_fig_manager": "📊 Figure and Table Manager",
        "sec_trans": "3. Metadata Translations",
        "trans_info": "According to the journal requirements, the title, authors, abstract and keywords must be provided in two other languages.",
        "gen_btn": "🚀 Generate Document",
        "err_abs_len": "⚠️ Abstract is too long: {count} words. Maximum: 300.",
        "succ_abs_len": "Words in abstract: {count}/300",
        "err_fill_req": "Please fill in at least the Title and Authors.",
        "err_gen": "An error occurred during generation: ",
        "succ_gen": "✅ Document successfully generated! Downloading automatically...",
        "btn_dl": "⬇️ Download .docx file manually",
        "reg_header": "📝 Researcher Registration",
        "reg_name": "Full Name",
        "reg_email": "Your Email",
        "reg_phone": "Phone Number",
        "reg_org": "Organization / University",
        "reg_pos": "Position / Status (e.g., PhD Student)",
        "reg_submit": "Register",
        "reg_success": "✅ You have successfully registered! The paper generator is now unlocked.",
        "reg_info": "You can now go to the 'Paper Generator' section.",
        "reg_req_msg": "🔒 To generate an article, you must complete the registration form. Please go to the 'Registration' tab above.",
        "reg_err_fill": "Please fill in your Name, Email, and Phone.",
        "f_author": "Kanat Samarkhanov",
        "f_license": "License",
        "f_univ": "L.N. Gumilyov ENU — Department of Physical and Economic Geography",
    }
}

l = locales[st.session_state.lang]

light_css = """
<style>
.stApp { background-color: #ffffff !important; }
[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e9ecef !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: #1a3a5c !important; }
p, span, label { color: #333333 !important; }
hr { border-color: #e9ecef !important; }
input, textarea, [data-baseweb="select"] > div {
    background-color: #eaf4fc !important;
    color: #1a3a5c !important;
    border: 1px solid #bcdcfa !important;
    border-radius: 6px !important;
}
input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2) !important;
}
input[disabled], textarea[disabled], [data-baseweb="select"] > div[aria-disabled="true"] {
    background-color: #e9ecef !important;
    color: #6c757d !important;
    -webkit-text-fill-color: #6c757d !important;
    border: 1px solid #dddddd !important;
}
button[kind="primary"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #1d4ed8 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
    border-color: #1e40af !important;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.4) !important;
}
div[data-testid="stRadio"] {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
    background-color: #f1f3f4 !important;
    border-radius: 20px !important;
    padding: 4px !important;
    display: inline-flex !important;
    gap: 4px !important;
    flex-direction: row !important;
    border: none !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: transparent !important;
    padding: 8px 24px !important;
    border-radius: 16px !important;
    margin: 0 !important;
    color: #5f6368 !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    border: none !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: rgba(0,0,0,0.05) !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p {
    color: inherit !important;
    font-weight: inherit !important;
    margin: 0 !important;
}
div[data-testid="stRadio"] div[role="radio"] {
    display: none !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(div[aria-checked="true"]) {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    font-weight: 600 !important;
}
</style>
"""

dark_css = """
<style>
.stApp { background-color: #0d1b2e !important; }
[data-testid="stSidebar"] { background-color: #0b1727 !important; border-right: 1px solid #1e3a5f !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: #e2edf7 !important; }
p, span, label { color: #c9d8ee !important; }
hr { border-color: #1e3a5f !important; }
input, textarea, [data-baseweb="select"] > div {
    background-color: #172a45 !important;
    color: #e2edf7 !important;
    border: 1px solid #2e5cb8 !important;
    box-shadow: 0 0 4px rgba(46, 92, 184, 0.5) !important;
    border-radius: 6px !important;
}
input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within {
    border: 1px solid #4a86e8 !important;
    box-shadow: 0 0 8px rgba(74, 134, 232, 0.8) !important;
}
input[disabled], textarea[disabled], [data-baseweb="select"] > div[aria-disabled="true"] {
    background-color: #0b1727 !important;
    color: #7b96b8 !important;
    -webkit-text-fill-color: #7b96b8 !important;
    border: 1px solid #152b4a !important;
    box-shadow: none !important;
}
button[kind="primary"] {
    background-color: #3b82f6 !important;
    color: #ffffff !important;
    border: 1px solid #2563eb !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
button[kind="primary"]:hover {
    background-color: #60a5fa !important;
    border-color: #3b82f6 !important;
    box-shadow: 0 0 8px rgba(59, 130, 246, 0.6) !important;
}
div[data-testid="stRadio"] {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
    background-color: #0b1727 !important;
    border-radius: 20px !important;
    padding: 4px !important;
    display: inline-flex !important;
    gap: 4px !important;
    flex-direction: row !important;
    border: 1px solid #1e3a5f !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: transparent !important;
    padding: 8px 24px !important;
    border-radius: 16px !important;
    margin: 0 !important;
    color: #7b96b8 !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    border: none !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: rgba(255,255,255,0.05) !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p {
    color: inherit !important;
    font-weight: inherit !important;
    margin: 0 !important;
}
div[data-testid="stRadio"] div[role="radio"] {
    display: none !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(div[aria-checked="true"]) {
    background-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3) !important;
    font-weight: 600 !important;
}
</style>
"""

st.markdown(dark_css if st.session_state.theme == "dark" else light_css, unsafe_allow_html=True)


def auto_download(bio, filename):
    b64 = base64.b64encode(bio.getvalue()).decode()
    custom_html = f"""
        <a id="auto_download_link" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="{filename}"></a>
        <script>
            document.getElementById('auto_download_link').click();
        </script>
    """
    components.html(custom_html, height=0)


def extract_text(uploaded_file):
    if not uploaded_file:
        return ""
    try:
        if uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode('utf-8')
        elif uploaded_file.name.endswith('.docx'):
            doc_file = docx.Document(uploaded_file)
            return '\n'.join([p.text for p in doc_file.paragraphs])
    except Exception as e:
        return f"[Қате / Error: {str(e)}]"
    return ""


def append_to_github_csv(filename, row_data, header_data):
    try:
        github_token = st.secrets["GITHUB_TOKEN"]
        github_repo = st.secrets["GITHUB_REPO"]
    except Exception:
        file_exists = os.path.isfile(filename)
        with open(filename, mode="a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header_data)
            writer.writerow(row_data)
        return

    url = f"https://api.github.com/repos/{github_repo}/contents/{filename}"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(url, headers=headers)
    sha = None

    if response.status_code == 200:
        data = response.json()
        sha = data["sha"]
        content = base64.b64decode(data["content"]).decode("utf-8")
    else:
        content = "\ufeff"

    output = io.StringIO()
    writer = csv.writer(output)
    if content == "\ufeff":
        writer.writerow(header_data)
    writer.writerow(row_data)

    new_content = content + output.getvalue()
    payload = {
        "message": f"Жаңа дерек қосылды: {filename}",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    requests.put(url, headers=headers, json=payload)


def log_generation(title_text, authors_text, lang):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, lang, title_text, authors_text]
    header = ["Уақыты (Timestamp)", "Тіл (Language)", "Тақырып (Title)", "Авторлар (Authors)"]
    append_to_github_csv("generation_logs.csv", row, header)


def log_registration(name, email, phone, org, pos):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, name, email, phone, org, pos]
    header = [
        "Уақыты (Timestamp)", "Аты-жөні (Full Name)", "Email",
        "Телефон (Phone)", "Ұйым (Organization)", "Лауазымы (Position)"
    ]
    append_to_github_csv("registered_users.csv", row, header)


hc1, hc2, hc3 = st.columns([6, 1.8, 1.8])
with hc1:
    st.title(l["title"])
    st.caption(l["subtitle"])
with hc2:
    _lang_labels = {"kz": "🇰🇿 Қазақша", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    _lang_keys = list(_lang_labels.keys())
    _sel = st.selectbox(
        "lang", _lang_keys,
        index=_lang_keys.index(st.session_state.lang),
        format_func=lambda x: _lang_labels[x],
        label_visibility="collapsed",
    )
    if _sel != st.session_state.lang:
        st.session_state.lang = _sel
        st.rerun()
with hc3:
    _tbtn = l["btn_theme_light"] if st.session_state.theme == "dark" else l["btn_theme_dark"]
    if st.button(_tbtn, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

st.markdown("---")

if "nav_radio" not in st.session_state or st.session_state.nav_radio not in [l["nav_gen"], l["nav_reg"]]:
    st.session_state.nav_radio = l["nav_gen"]

if st.session_state.get("go_to_gen"):
    st.session_state.nav_radio = l["nav_gen"]
    st.session_state.go_to_gen = False

app_mode = st.radio(
    "",
    [l["nav_gen"], l["nav_reg"]],
    horizontal=True,
    label_visibility="collapsed",
    key="nav_radio",
)
st.markdown("---")

is_locked = not st.session_state.is_registered

if app_mode == l["nav_gen"]:
    if is_locked:
        st.error(l["reg_req_msg"], icon="🔒")

    st.subheader(l["sidebar_title"])
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        primary_lang = st.selectbox(l["lbl_lang"], ["Русский", "Қазақша", "English"], disabled=is_locked)
    with col_s2:
        section = st.selectbox(l["lbl_sec"], ["Химия", "География"], disabled=is_locked)
    with col_s3:
        paper_type = st.selectbox(
            l["lbl_type"],
            ["Научная статья (Article)", "Обзор (Review)", "Мини-обзор (Mini-review)", "Краткое сообщение (Communication)"],
            disabled=is_locked,
        )
    with col_s4:
        mrnti = st.text_input(l["lbl_mrnti"], value="06.81.23", disabled=is_locked)

    st.markdown("<br>", unsafe_allow_html=True)

    st.header(l["sec_meta"])
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_area(l["lbl_title"], height=68, disabled=is_locked)
        authors = st.text_area(l["lbl_authors"], help=l["lbl_authors_help"], height=68, disabled=is_locked)
    with col2:
        affiliations = st.text_area(l["lbl_affil"], help=l["lbl_affil_help"], height=68, disabled=is_locked)
        corr_email = st.text_input(l["lbl_email"], disabled=is_locked)

    st.header(l["sec_text"])
    abstract = st.text_area(l["lbl_abstract"], height=150, disabled=is_locked)
    abstract_word_count = len(abstract.split()) if abstract else 0

    if not is_locked:
        if abstract_word_count > 300:
            st.error(l["err_abs_len"].format(count=abstract_word_count))
        elif abstract_word_count > 0:
            st.success(l["succ_abs_len"].format(count=abstract_word_count))

    keywords = st.text_input(l["lbl_kw"], help=l["lbl_kw_help"], disabled=is_locked)

    st.subheader("IMRAD: Файлдарды жүктеп алу (Upload files)")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        file_intro = st.file_uploader(l["lbl_intro"], type=["txt", "docx"], disabled=is_locked)
        file_methods = st.file_uploader(l["lbl_methods"], type=["txt", "docx"], disabled=is_locked)
    with col_i2:
        file_results = st.file_uploader(l["lbl_results"], type=["txt", "docx"], disabled=is_locked)
        file_conclusion = st.file_uploader(l["lbl_conclusion"], type=["txt", "docx"], disabled=is_locked)

    st.header(l["lbl_fig_manager"])
    fig_df = pd.DataFrame(columns=["Type (Figure/Table)", "Number", "Caption", "In-text reference (e.g., Fig. 1)"])
    if not is_locked:
        edited_figs = st.data_editor(fig_df, num_rows="dynamic", use_container_width=True)
    else:
        st.dataframe(fig_df, use_container_width=True)

    st.header(l["lbl_ref_manager"])
    ref_style = st.selectbox(l["lbl_ref_style"], ["GOST", "APA", "IEEE"], disabled=is_locked)
    ref_df = pd.DataFrame(columns=["Author(s)", "Year", "Title", "Journal/Publisher", "Volume/Pages"])

    if not is_locked:
        edited_refs = st.data_editor(ref_df, num_rows="dynamic", use_container_width=True)
    else:
        st.dataframe(ref_df, use_container_width=True)

    st.header(l["sec_trans"])
    st.info(l["trans_info"])

    trans_langs = ["Русский", "Қазақша", "English"]
    if primary_lang in trans_langs:
        trans_langs.remove(primary_lang)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader(f"{trans_langs[0]}")
        t1_title = st.text_input(f"{l['lbl_title']} ({trans_langs[0]})", disabled=is_locked)
        t1_authors = st.text_input(f"{l['lbl_authors']} ({trans_langs[0]})", disabled=is_locked)
        t1_abstract = st.text_area(f"{l['lbl_abstract']} ({trans_langs[0]})", height=100, disabled=is_locked)
        t1_keywords = st.text_input(f"{l['lbl_kw']} ({trans_langs[0]})", disabled=is_locked)

    with col_t2:
        st.subheader(f"{trans_langs[1]}")
        t2_title = st.text_input(f"{l['lbl_title']} ({trans_langs[1]})", disabled=is_locked)
        t2_authors = st.text_input(f"{l['lbl_authors']} ({trans_langs[1]})", disabled=is_locked)
        t2_abstract = st.text_area(f"{l['lbl_abstract']} ({trans_langs[1]})", height=100, disabled=is_locked)
        t2_keywords = st.text_input(f"{l['lbl_kw']} ({trans_langs[1]})", disabled=is_locked)

    st.markdown("---")
    generate_btn = st.button(l["gen_btn"], type="primary", use_container_width=True, disabled=is_locked)

    if generate_btn and not is_locked:
        if abstract_word_count > 300:
            st.error(l["err_abs_len"].format(count=abstract_word_count))
        elif not title or not authors:
            st.warning(l["err_fill_req"])
        else:
            try:
                main_text_compiled = ""
                if file_intro: main_text_compiled += "1. INTRODUCTION\n" + extract_text(file_intro) + "\n\n"
                if file_methods: main_text_compiled += "2. MATERIALS AND METHODS\n" + extract_text(file_methods) + "\n\n"
                if file_results: main_text_compiled += "3. RESULTS\n" + extract_text(file_results) + "\n\n"
                if file_conclusion: main_text_compiled += "4. CONCLUSION\n" + extract_text(file_conclusion) + "\n\n"

                fig_text_compiled = ""
                for _, row in edited_figs.iterrows():
                    c_type = str(row.get("Type (Figure/Table)", "")).strip()
                    c_num = str(row.get("Number", "")).strip()
                    c_cap = str(row.get("Caption", "")).strip()
                    if c_cap and c_cap != "nan":
                        fig_text_compiled += f"{c_type} {c_num}. {c_cap}\n"

                if fig_text_compiled:
                    main_text_compiled += "\n\n--- FIGURES & TABLES ---\n" + fig_text_compiled

                refs_compiled = []
                for i, row in edited_refs.iterrows():
                    r_author = str(row.get("Author(s)", "")).strip()
                    r_year = str(row.get("Year", "")).strip()
                    r_title = str(row.get("Title", "")).strip()
                    r_journal = str(row.get("Journal/Publisher", "")).strip()
                    r_vol = str(row.get("Volume/Pages", "")).strip()

                    if r_author == "nan" or not r_author: continue

                    if ref_style == "APA":
                        refs_compiled.append(f"{r_author} ({r_year}). {r_title}. {r_journal}, {r_vol}.")
                    elif ref_style == "IEEE":
                        refs_compiled.append(f"[{i+1}] {r_author}, \"{r_title},\" {r_journal}, {r_vol}, {r_year}.")
                    else:
                        refs_compiled.append(f"{i+1}. {r_author} {r_title} // {r_journal}. - {r_year}. - {r_vol}.")

                final_references = "\n".join(refs_compiled)

                template_filename = "Russian_template_2025.docx"
                if primary_lang == "Русский":
                    template_filename = "Russian_template_2025.docx"
                elif primary_lang == "Қазақша":
                    template_filename = "Kazakh_template_2025.docx"
                elif primary_lang == "English":
                    template_filename = "English_template_2025.docx"

                context = {
                    "mrnti": mrnti,
                    "section": section,
                    "paper_type": paper_type,
                    "title": title,
                    "authors": authors,
                    "affiliations": affiliations,
                    "corr_email": corr_email,
                    "abstract": abstract,
                    "keywords": keywords,
                    "main_text": main_text_compiled,
                    "references": final_references,
                    "t1_title": t1_title,
                    "t1_authors": t1_authors,
                    "t1_abstract": t1_abstract,
                    "t1_keywords": t1_keywords,
                    "t2_title": t2_title,
                    "t2_authors": t2_authors,
                    "t2_abstract": t2_abstract,
                    "t2_keywords": t2_keywords,
                }

                doc = DocxTemplate(template_filename)
                doc.render(context)

                bio = BytesIO()
                doc.save(bio)

                st.success(l["succ_gen"])

                with st.spinner("Деректер сақталуда... (Saving logs...)"):
                    log_generation(title, authors, primary_lang)

                auto_download(bio, "Formatted_Article.docx")

                st.download_button(
                    label=l["btn_dl"],
                    data=bio.getvalue(),
                    file_name="Formatted_Article.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="secondary",
                )
            except Exception as e:
                st.error(f"{l['err_gen']} {e}")
                st.info(
                    "💡 Ескерту: 'Russian_template_2025.docx', 'Kazakh_template_2025.docx' және 'English_template_2025.docx' файлдары бумада болуы тиіс."
                )

elif app_mode == l["nav_reg"]:
    st.header(l["reg_header"])

    if st.session_state.is_registered:
        st.success(l["reg_success"])
        st.info(l["reg_info"])
    else:
        with st.form("registration_form"):
            r_name = st.text_input(l["reg_name"])
            r_email = st.text_input(l["reg_email"])
            r_phone = st.text_input(l["reg_phone"])
            r_org = st.text_input(l["reg_org"])
            r_pos = st.text_input(l["reg_pos"])

            submitted = st.form_submit_button(l["reg_submit"], type="primary")

            if submitted:
                if r_name and r_email and r_phone:
                    with st.spinner("Тіркелу жүріп жатыр..."):
                        log_registration(r_name, r_email, r_phone, r_org, r_pos)

                    st.session_state.is_registered = True
                    st.session_state.go_to_gen = True
                    st.success(l["reg_success"])
                    st.rerun()
                else:
                    st.error(l["reg_err_fill"])

with st.sidebar:
    if os.path.exists("generation_logs.csv") or os.path.exists("registered_users.csv"):
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.caption("🔒 Панель администратора")

        if os.path.exists("generation_logs.csv"):
            with open("generation_logs.csv", "rb") as f:
                st.download_button(
                    label="📊 Логи генерации (.csv)",
                    data=f,
                    file_name="generation_logs.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        if os.path.exists("registered_users.csv"):
            with open("registered_users.csv", "rb") as f:
                st.download_button(
                    label="👥 База пользователей (.csv)",
                    data=f,
                    file_name="registered_users.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

st.markdown("---")
st.markdown(
    f'<div style="text-align:center;font-size:12px;color:gray;padding:12px 0 20px 0;line-height:2.2;">'
    f'<b style="font-size:13px;">© 2025 {l["f_author"]}</b><br>'
    f'📧 <a href="mailto:samarkhanov_kb@enu.kz" style="text-decoration:none;">samarkhanov_kb@enu.kz</a>'
    f'&nbsp;·&nbsp;'
    f'<a href="mailto:kanat.baurzhanuly@gmail.com" style="text-decoration:none;">kanat.baurzhanuly@gmail.com</a><br>'
    f'🏛️ <a href="https://fns.enu.kz/kz/page/departments/physical-and-economical-geography/faculty-members"'
    f'     target="_blank" style="text-decoration:none;">{l["f_univ"]}</a><br>'
    f'</div>',
    unsafe_allow_html=True,
)
