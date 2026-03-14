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
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import subprocess
import time

# ----------------- СОВМЕСТИМОСТЬ ПЕРЕЗАГРУЗКИ -----------------
def safe_rerun():
    """Умная функция перезагрузки для совместимости со старыми и новыми версиями Streamlit"""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# ----------------- PAGE & SESSION -----------------
st.set_page_config(page_title="Smart Paper Generator", page_icon="📝", layout="wide")

if "lang" not in st.session_state:
    st.session_state.lang = "kz"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "is_registered" not in st.session_state:
    st.session_state.is_registered = False
if "ui_font" not in st.session_state:
    st.session_state.ui_font = "System Default"
if "fig_count" not in st.session_state:
    st.session_state.fig_count = 1
if "tab_count" not in st.session_state:
    st.session_state.tab_count = 1
if "eq_count" not in st.session_state:
    st.session_state.eq_count = 1

# ----------------- LOCALES -----------------
locales = {
    "ru": {
        "title": "Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
        "nav_gen": "📄 Генератор статей",
        "nav_reg": "👤 Регистрация",
        "sidebar_title": "⚙️ Настройки",
        "lbl_ui_font": "Шрифт интерфейса",
        "lbl_lang": "Язык",
        "lbl_sec": "Секция",
        "lbl_type": "Тип статьи",
        "lbl_mrnti": "МРНТИ / IRSTI",
        "sec_meta": "1. Основные метаданные",
        "lbl_title": "Название статьи",
        "lbl_authors": "Авторы",
        "lbl_authors_help": "Например: Имя Фамилия1, Имя Фамилия2",
        "lbl_affil": "Аффилиации",
        "lbl_affil_help": "1 Университет, Город, Страна; email",
        "lbl_email": "Email",
        "sec_text": "2. Текст статьи (IMRAD)",
        "lbl_abstract": "Аннотация (до 300 слов)",
        "lbl_kw": "Ключевые слова",
        "lbl_kw_help": "Слово 1; слово 2; слово 3",
        "lbl_intro": "Введение (.txt/.docx)",
        "lbl_methods": "Материалы и методы (.txt/.docx)",
        "lbl_results": "Результаты (.txt/.docx)",
        "lbl_discussion": "Обсуждение (.txt/.docx)",
        "lbl_conclusion": "Заключение (.txt/.docx)",
        "lbl_ref_manager": "📚 Менеджер литературы",
        "lbl_ref_style": "Стиль цитирования",
        "lbl_fig_manager": "📊 Менеджер рисунков",
        "lbl_tab_manager": "📋 Менеджер таблиц",
        "lbl_eq_manager": "➗ Менеджер формул",
        "lbl_add_fig": "➕ Добавить рисунок",
        "lbl_add_tab": "➕ Добавить таблицу",
        "lbl_add_eq": "➕ Добавить формулу",
        "btn_upload_short": "📎 Загрузить",
        "lbl_fig_hint_title": "💡 Подсказка для графиков",
        "lbl_fig_hint_text": "Используйте тег <code>[@fig1]</code> в тексте.",
        "lbl_tab_hint_title": "💡 Инструкция для таблиц",
        "lbl_tab_hint_text": "Загружайте в формате <b>.docx</b>.",
        "lbl_eq_hint_title": "💡 Подсказка для формул",
        "lbl_eq_hint_text": "Разместите тег <code>[@eq1]</code> в тексте.",
        "btn_sample_table": "📥 Скачать образец таблицы",
        "lbl_samples": "📥 Скачать шаблоны файлов",
        "sec_backmatter": "4. Дополнительная информация (Back Matter)",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Переводы метаданных",
        "trans_info": "Необходимо предоставить метаданные на двух других языках.",
        "gen_btn": "🚀 Сгенерировать статью",
        "err_abs_len": "⚠️ Аннотация слишком длинная: {count} слов.",
        "succ_abs_len": "Слов в аннотации: {count}/300",
        "err_fill_req": "Заполните Название и Авторов.",
        "err_gen": "Ошибка при генерации: ",
        "succ_gen": "✅ Сгенерировано за {time} сек!",
        "btn_dl_docx": "⬇️ Скачать .docx",
        "btn_dl_pdf": "⬇️ Скачать .pdf",
        "err_pdf": "⚠️ Не удалось сгенерировать PDF.",
        "reg_header": "📝 Регистрация исследователя",
        "reg_name": "ФИО (Полностью)",
        "reg_email": "Ваш Email",
        "reg_phone": "Номер телефона",
        "reg_code": "Код",
        "reg_org": "Организация",
        "reg_pos": "Должность",
        "reg_submit": "Зарегистрироваться",
        "reg_success": "✅ Вы успешно зарегистрированы!",
        "reg_info": "Теперь вам доступен генератор статей.",
        "reg_req_msg": "🔒 Пожалуйста, зарегистрируйтесь.",
        "reg_err_fill": "Заполните Имя, Email и Телефон.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "ЕНУ им. Л.Н. Гумилева — Кафедра физической и экономической географии",
        "browse_files": "Файл",
        "drag_drop": "Перетащите файл сюда",
        "limit": "Лимит 200MB",
        "fig_prefix": "Рисунок",
        "tab_prefix": "Таблица",
        "fb_header": "💬 Кері байланыс қалдыру",
        "fb_text": "Ваши предложения или найденные ошибки",
        "fb_btn": "Отправить отзыв",
        "fb_succ": "Спасибо за ваш отзыв!",
        "preview": "Предпросмотр",
        "prog_title": "Готовность статьи",
        "prog_text": "Заполнено: {pct}%",
    },
    "kz": {
        "title": "Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · Химия / География · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
        "nav_gen": "📄 Мақала генераторы",
        "nav_reg": "👤 Тіркелу",
        "sidebar_title": "⚙️ Баптаулар",
        "lbl_ui_font": "Интерфейс қаріпі",
        "lbl_lang": "Тіл",
        "lbl_sec": "Секция",
        "lbl_type": "Мақала түрі",
        "lbl_mrnti": "МРНТИ / IRSTI",
        "sec_meta": "1. Негізгі метадеректер",
        "lbl_title": "Мақаланың атауы",
        "lbl_authors": "Авторлар",
        "lbl_authors_help": "Мысалы: Аты Жөні1, Аты Жөні2",
        "lbl_affil": "Аффилиация",
        "lbl_affil_help": "1 Университет, Қала, Ел; email",
        "lbl_email": "Email",
        "sec_text": "2. Мақала мәтіні (IMRAD)",
        "lbl_abstract": "Аңдатпа",
        "lbl_kw": "Түйінді сөздер",
        "lbl_kw_help": "Сөз 1; сөз 2; сөз 3",
        "lbl_intro": "Кіріспе (.txt/.docx)",
        "lbl_methods": "Материалдар/әдістер (.txt/.docx)",
        "lbl_results": "Нәтижелер (.txt/.docx)",
        "lbl_discussion": "Талдау (.txt/.docx)",
        "lbl_conclusion": "Қорытынды (.txt/.docx)",
        "lbl_ref_manager": "📚 Әдебиеттер менеджері",
        "lbl_ref_style": "Дәйексөз стилі",
        "lbl_fig_manager": "📊 Суреттер менеджері",
        "lbl_tab_manager": "📋 Кестелер менеджері",
        "lbl_eq_manager": "➗ Формулалар менеджері",
        "lbl_add_fig": "➕ Сурет қосу",
        "lbl_add_tab": "➕ Кесте қосу",
        "lbl_add_eq": "➕ Формула қосу",
        "btn_upload_short": "📎 Жүктеу",
        "lbl_fig_hint_title": "💡 Суреттер нұсқаулығы",
        "lbl_fig_hint_text": "Мәтінге <code>[@fig1]</code> тегін қойыңыз.",
        "lbl_tab_hint_title": "💡 Кестелер нұсқаулығы",
        "lbl_tab_hint_text": "Кестені <b>.docx</b> форматында жүктеңіз.",
        "lbl_eq_hint_title": "💡 Формулалар нұсқаулығы",
        "lbl_eq_hint_text": "Мәтінге <code>[@eq1]</code> тегін қойыңыз.",
        "btn_sample_table": "📥 Кесте үлгісін жүктеу",
        "lbl_samples": "📥 Файл үлгілерін жүктеп алу",
        "sec_backmatter": "4. Қосымша ақпарат (Back Matter)",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Метадеректер аудармасы",
        "trans_info": "Метадеректерді басқа екі тілде ұсыну қажет.",
        "gen_btn": "🚀 Мақаланы генерациялау",
        "err_abs_len": "⚠️ Аңдатпа тым ұзын: {count} сөз.",
        "succ_abs_len": "Аңдатпадағы сөз саны: {count}/300",
        "err_fill_req": "Атауын және Авторларын толтырыңыз.",
        "err_gen": "Қате пайда болды: ",
        "succ_gen": "✅ Сәтті генерацияланды ({time} сек)!",
        "btn_dl_docx": "⬇️ .docx жүктеу",
        "btn_dl_pdf": "⬇️ .pdf жүктеу",
        "err_pdf": "⚠️ PDF жасау мүмкін болмады.",
        "reg_header": "📝 Зерттеушіні тіркеу",
        "reg_name": "Аты-жөні (Толық)",
        "reg_email": "Сіздің Email",
        "reg_phone": "Телефон нөмірі",
        "reg_code": "Код",
        "reg_org": "Ұйым / Университет",
        "reg_pos": "Қызметі",
        "reg_submit": "Тіркелу",
        "reg_success": "✅ Тіркелу сәтті өтті!",
        "reg_info": "Енді мақала генераторы қолжетімді.",
        "reg_req_msg": "🔒 Мақала жасау үшін тіркелу қажет.",
        "reg_err_fill": "Мәліметтерді дұрыс толтырыңыз.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ — Физикалық және экономикалық география кафедрасы",
        "browse_files": "Файл",
        "drag_drop": "Файлды осында сүйреңіз",
        "limit": "Шектеу 200MB",
        "fig_prefix": "Сурет",
        "tab_prefix": "Кесте",
        "fb_header": "💬 Кері байланыс қалдыру",
        "fb_text": "Сіздің ұсыныстарыңыз немесе табылған қателер",
        "fb_btn": "Пікір жіберу",
        "fb_succ": "Пікіріңіз үшін рақмет!",
        "preview": "Алдын ала көру",
        "prog_title": "Мақаланың дайындығы",
        "prog_text": "Толтырылды: {pct}%",
    },
    "en": {
        "title": "Smart Paper Generator",
        "subtitle": "L.N. Gumilyov ENU Bulletin · Chemistry / Geography · 2025",
        "btn_theme_dark": "🌙 Dark mode",
        "btn_theme_light": "☀️ Light mode",
        "nav_gen": "📄 Paper Generator",
        "nav_reg": "👤 Registration",
        "sidebar_title": "⚙️ Settings",
        "lbl_ui_font": "Interface Font",
        "lbl_lang": "Language",
        "lbl_sec": "Section",
        "lbl_type": "Paper Type",
        "lbl_mrnti": "IRSTI",
        "sec_meta": "1. Basic Metadata",
        "lbl_title": "Article Title",
        "lbl_authors": "Authors",
        "lbl_authors_help": "E.g.: Firstname Lastname",
        "lbl_affil": "Affiliations",
        "lbl_affil_help": "1 University, City, Country; email",
        "lbl_email": "Email",
        "sec_text": "2. Main Text (IMRAD)",
        "lbl_abstract": "Abstract (up to 300 words)",
        "lbl_kw": "Keywords",
        "lbl_kw_help": "Word 1; word 2; word 3",
        "lbl_intro": "Introduction (.txt/.docx)",
        "lbl_methods": "Materials & Methods (.txt/.docx)",
        "lbl_results": "Results (.txt/.docx)",
        "lbl_discussion": "Analysis (.txt/.docx)",
        "lbl_conclusion": "Conclusion (.txt/.docx)",
        "lbl_ref_manager": "📚 Reference Manager",
        "lbl_ref_style": "Citation Style",
        "lbl_fig_manager": "📊 Figure Manager",
        "lbl_tab_manager": "📋 Table Manager",
        "lbl_eq_manager": "➗ Equation Manager",
        "lbl_add_fig": "➕ Add Figure",
        "lbl_add_tab": "➕ Add Table",
        "lbl_add_eq": "➕ Add Equation",
        "btn_upload_short": "📎 Upload",
        "lbl_fig_hint_title": "💡 Figure Hint",
        "lbl_fig_hint_text": "Place tag <code>[@fig1]</code> in text.",
        "lbl_tab_hint_title": "💡 Table Hint",
        "lbl_tab_hint_text": "Upload as <b>.docx</b>.",
        "lbl_eq_hint_title": "💡 Equation Hint",
        "lbl_eq_hint_text": "Place tag <code>[@eq1]</code> in text.",
        "btn_sample_table": "📥 Download Table Sample",
        "lbl_samples": "📥 Download Sample Files",
        "sec_backmatter": "4. Additional Info",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Translations",
        "trans_info": "Provide metadata in two other languages.",
        "gen_btn": "🚀 Generate Document",
        "err_abs_len": "⚠️ Abstract too long: {count} words.",
        "succ_abs_len": "Words in abstract: {count}/300",
        "err_fill_req": "Fill Title and Authors.",
        "err_gen": "Error: ",
        "succ_gen": "✅ Generated in {time} sec!",
        "btn_dl_docx": "⬇️ Download .docx",
        "btn_dl_pdf": "⬇️ Download .pdf",
        "err_pdf": "⚠️ PDF generation failed.",
        "reg_header": "📝 Registration",
        "reg_name": "Full Name",
        "reg_email": "Your Email",
        "reg_phone": "Phone Number",
        "reg_code": "Code",
        "reg_org": "Organization",
        "reg_pos": "Position",
        "reg_submit": "Register",
        "reg_success": "✅ Registered successfully!",
        "reg_info": "Paper generator is now unlocked.",
        "reg_req_msg": "🔒 Please register first.",
        "reg_err_fill": "Fill Name, Email, and Phone.",
        "f_author": "Kanat Samarkhanov",
        "f_license": "License",
        "f_univ": "L.N. Gumilyov ENU",
        "browse_files": "File",
        "drag_drop": "Drag & drop files here",
        "limit": "Limit 200MB",
        "fig_prefix": "Figure",
        "tab_prefix": "Table",
        "fb_header": "💬 Feedback",
        "fb_text": "Your suggestions",
        "fb_btn": "Submit",
        "fb_succ": "Thank you!",
        "preview": "Preview",
        "prog_title": "Readiness",
        "prog_text": "Completed: {pct}%",
    }
}

l = locales.get(st.session_state.lang, locales["kz"])

# ----------------- THEME & CSS -----------------
font_mapping = {
    "System Default": "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
    "Times New Roman": "'Times New Roman', Times, serif",
    "Arial": "Arial, Helvetica, sans-serif",
    "Georgia": "Georgia, serif"
}
selected_css_font = font_mapping.get(st.session_state.ui_font, font_mapping["System Default"])

css_core = f"""
<style>
/* GLOBAL TYPOGRAPHY */
* {{ font-family: {selected_css_font} !important; }}

/* SMALLER TITLE AS REQUESTED */
.title-block h1 {{ font-size: 1.5rem !important; margin: 0 !important; padding: 0 !important; }}
.title-block p {{ font-size: 0.85rem !important; margin: 0 !important; opacity: 0.8; }}

/* HEADER COMPACTION */
.header-row {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }}

div.element-container:has(style) {{ display: none !important; height: 0 !important; margin: 0 !important; }}

/* UPLOAD ZONES */
[data-testid="stFileUploadDropzone"] {{
    border: 2px dashed #6aa5ff !important;
    border-radius: 12px !important;
    padding: 15px !important;
    transition: all 0.2s ease;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}}

[data-testid="stFileUploadDropzone"] button {{
    border-radius:8px !important; padding:6px 16px !important; font-weight:600;
    color: transparent !important; position: relative; background-color: transparent !important;
    border: 1px solid #4a90e2 !important; box-shadow: none !important;
}}

[data-testid="stFileUploadDropzone"] button::after {{
    content: "{l['browse_files']}"; color: #4a90e2 !important; 
    position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
    visibility: visible; font-weight: 600; font-size: 13px; white-space: nowrap; 
}}

[data-testid="stFileUploadDropzone"]::before {{ content:"📂"; font-size:24px; display:block; margin-bottom:4px; text-align: center; }}

/* REMOVE BLACKS - BLUE SCHEME */
.stApp {{ background: #f4f9ff !important; }}
input, textarea, [data-baseweb="select"] {{ background-color: #ffffff !important; color: #1e3a5f !important; border: 1px solid #cbdff2 !important; }}

/* BUTTON STYLES FROM SCREENSHOT */
.stButton>button:not([kind="primary"]) {{
    background: #ffffff !important; 
    color: #1d4ed8 !important; 
    border: 1px solid #cbdff2 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}}

button[kind="primary"] {{
    background: linear-gradient(90deg, #1d4ed8, #3b82f6) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 10px 22px !important; font-weight: bold !important;
}}

/* INFO CARDS */
.info-card {{ background: white; border-radius:12px; padding:15px; margin-bottom:12px; border: 1px solid #d1e4f9; }}
.info-card-title {{ font-weight:700; font-size:14px; color: #0c335e; }}
.info-card-text {{ font-size:12.5px; color: #475569; }}
</style>
"""

if st.session_state.theme == "dark":
    st.markdown(css_core + """
    <style>
    .stApp { background: #0a192f !important; }
    h1, h2, h3, label, p, span { color: #d0e8ff !important; }
    .stButton>button:not([kind="primary"]) { background: #112240 !important; color: #8bb4e5 !important; border: 1px solid #233554 !important; }
    input, textarea, [data-baseweb="select"] { background-color: #112240 !important; color: #cbd5e1 !important; border: 1px solid #233554 !important; }
    .info-card { background: #112240 !important; border-color: #233554 !important; }
    .info-card-title { color: #8bb4e5 !important; }
    .info-card-text { color: #a8b2d1 !important; }
    [data-testid="stFileUploadDropzone"] { background: #112240 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(css_core, unsafe_allow_html=True)

# ----------------- HEADER (ALIGNED & LOWERED BUTTONS) -----------------
hc1, hc2, hc3 = st.columns([6, 2, 2])
with hc1:
    st.markdown(f"""
    <div class="title-block">
        <h1>{l['title']}</h1>
        <p>{l['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)
with hc2:
    _lang_labels = {"kz": "🇰🇿 Қазақша", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    _sel = st.selectbox("lang", list(_lang_labels.keys()), 
                        index=list(_lang_labels.keys()).index(st.session_state.lang),
                        format_func=lambda x: _lang_labels[x], label_visibility="collapsed")
    if _sel != st.session_state.lang:
        st.session_state.lang = _sel
        safe_rerun()
with hc3:
    _tbtn = l["btn_theme_light"] if st.session_state.theme == "dark" else l["btn_theme_dark"]
    if st.button(_tbtn, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        safe_rerun()
st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

# ----------------- HELPERS -----------------
def extract_text(uploaded_file):
    if not uploaded_file: return ""
    try:
        if uploaded_file.name.endswith('.txt'): return uploaded_file.read().decode('utf-8')
        elif uploaded_file.name.endswith('.docx'):
            doc_file = docx.Document(uploaded_file)
            return '\n'.join([p.text for p in doc_file.paragraphs])
    except: return ""
    return ""

def render_live_uploader(label, key, loc_preview, is_locked):
    f = st.file_uploader(label, type=["txt", "docx"], disabled=is_locked, key=key)
    if f:
        text = extract_text(f)
        with st.expander(f"👀 {loc_preview}", expanded=True):
            bg = "#112240" if st.session_state.theme == "dark" else "#ffffff"
            st.markdown(f"<div style='max-height:120px; overflow-y:auto; font-size:12px; padding:10px; background:{bg}; border:1px solid #4a90e2; border-radius:8px;'>{text}</div>", unsafe_allow_html=True)
    return f

# ----------------- NAVIGATION -----------------
app_mode = st.radio("", [l["nav_gen"], l["nav_reg"]], horizontal=True, label_visibility="collapsed")
is_locked = not st.session_state.is_registered

if app_mode == l["nav_gen"]:
    progress_placeholder = st.empty()
    if is_locked: st.error(l["reg_req_msg"], icon="🔒")

    st.subheader(l["sidebar_title"])
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.selectbox(l["lbl_lang"], ["Русский", "Қазақша", "English"], disabled=is_locked)
    with c2: st.selectbox(l["lbl_sec"], ["Химия", "География"], disabled=is_locked)
    with c3: st.selectbox(l["lbl_type"], ["Статья", "Обзор"], disabled=is_locked)
    with c4: st.text_input(l["lbl_mrnti"], value="06.81.23", disabled=is_locked)

    st.header(l["sec_meta"])
    m1, m2 = st.columns(2)
    with m1:
        title = st.text_area(l["lbl_title"], height=68, disabled=is_locked)
        authors = st.text_area(l["lbl_authors"], height=68, disabled=is_locked)
    with m2:
        affiliations = st.text_area(l["lbl_affil"], height=68, disabled=is_locked)
        corr_email = st.text_input(l["lbl_email"], disabled=is_locked)

    st.header(l["sec_text"])
    abstract = st.text_area(l["lbl_abstract"], height=100, disabled=is_locked)
    keywords = st.text_input(l["lbl_kw"], disabled=is_locked)

    i1, i2, i3 = st.columns(3)
    with i1:
        f_intro = render_live_uploader(l["lbl_intro"], "up_i", l["preview"], is_locked)
        f_meth = render_live_uploader(l["lbl_methods"], "up_m", l["preview"], is_locked)
    with i2:
        f_res = render_live_uploader(l["lbl_results"], "up_r", l["preview"], is_locked)
        f_disc = render_live_uploader(l["lbl_discussion"], "up_d", l["preview"], is_locked)
    with i3:
        f_conc = render_live_uploader(l["lbl_conclusion"], "up_c", l["preview"], is_locked)

    if not is_locked:
        pct = 35 # Mock
        st.progress(pct/100)

    st.button(l["gen_btn"], type="primary", use_container_width=True, disabled=is_locked)

elif app_mode == l["nav_reg"]:
    st.header(l["reg_header"])
    if st.session_state.is_registered:
        st.success(l["reg_success"])
    else:
        with st.form("reg"):
            st.text_input(l["reg_name"])
            st.text_input(l["reg_email"])
            st.text_input(l["reg_phone"])
            if st.form_submit_button(l["reg_submit"], type="primary"):
                st.session_state.is_registered = True
                safe_rerun()

# ----------------- FEEDBACK (OPEN BY DEFAULT) -----------------
st.markdown("---")
st.subheader(l["fb_header"])
with st.expander(l["fb_text"], expanded=True):
    with st.form("fb", clear_on_submit=True):
        st.text_input("Email (Optional)")
        st.text_area(l["fb_text"], height=80)
        if st.form_submit_button(l["fb_btn"]):
            st.success(l["fb_succ"])

# ----------------- FOOTER -----------------
st.markdown("---")
f_c = "#7b96b8" if st.session_state.theme == "dark" else "#555"
st.markdown(f"<div style='text-align:center; font-size:11px; color:{f_c}; padding:15px;'>© 2025 {l['f_author']} | {l['f_univ']}</div>", unsafe_allow_html=True)
