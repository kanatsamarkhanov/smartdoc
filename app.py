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
        "title": "📝 Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
        "nav_gen": "📄 Генератор статей",
        "nav_reg": "👤 Регистрация",
        "sidebar_title": "⚙️ Настройки",
        "lbl_ui_font": "Шрифт интерфейса",
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
        "sec_text": "2. Текст статьи (Загрузка IMRAD)",
        "lbl_abstract": "Аннотация (до 300 слов)",
        "lbl_kw": "Ключевые слова",
        "lbl_kw_help": "Слово 1; слово 2; слово 3 (от 3 до 10 слов)",
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
        "lbl_fig_hint_text": "Если рисунок состоит из нескольких частей (a, b, c), используйте <b>один тег</b> <code>[@fig1]</code> для всей группы.",
        "lbl_tab_hint_title": "💡 Инструкция для сложных таблиц",
        "lbl_tab_hint_text": "Для таблиц с объединенными ячейками загружайте их в формате <b>.docx</b>, чтобы сохранить форматирование.",
        "lbl_eq_hint_title": "💡 Подсказка для формул",
        "lbl_eq_hint_text": "Введите формулу. Разместите тег <code>[@eq1]</code> в тексте статьи.",
        "btn_sample_table": "📥 Скачать образец сложной таблицы",
        "lbl_samples": "📥 Скачать шаблоны файлов",
        "sec_backmatter": "4. Дополнительная информация (Back Matter)",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Переводы метаданных",
        "trans_info": "По требованиям журнала необходимо предоставить название, авторов, аннотацию и ключевые слова на двух других языках.",
        "gen_btn": "🚀 Сгенерировать статью",
        "err_abs_len": "⚠️ Аннотация слишком длинная: {count} слов. Максимум: 300.",
        "succ_abs_len": "Слов в аннотации: {count}/300",
        "err_fill_req": "Пожалуйста, заполните хотя бы Название и Авторов.",
        "err_gen": "Произошла ошибка при генерации: ",
        "succ_gen": "✅ Документ успешно сгенерирован за {time} сек!",
        "btn_dl_docx": "⬇️ Скачать .docx",
        "btn_dl_pdf": "⬇️ Скачать .pdf",
        "err_pdf": "⚠️ Не удалось сгенерировать PDF (требуется LibreOffice на сервере). Доступен DOCX файл.",
        "reg_header": "📝 Регистрация исследователя",
        "reg_name": "ФИО (Полностью)",
        "reg_email": "Ваш Email",
        "reg_phone": "Номер телефона (без кода)",
        "reg_code": "Код",
        "reg_org": "Организация / Университет",
        "reg_pos": "Должность / Статус (например: Докторант)",
        "reg_submit": "Зарегистрироваться",
        "reg_success": "✅ Вы успешно зарегистрированы! Теперь вам доступен генератор статей.",
        "reg_info": "Вы можете перейти в раздел «Генератор статей».",
        "reg_req_msg": "🔒 Для создания статьи необходимо заполнить форму регистрации.",
        "reg_err_fill": "Пожалуйста, корректно заполните Имя, Email и Телефон.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "ЕНУ им. Л.Н. Гумилева — Кафедра физической и экономической географии",
        "browse_files": "Выберите файл",
        "drag_drop": "Перетащите файл сюда\nПоддерживаемые форматы: txt, docx",
        "limit": "Лимит 200MB",
        "fig_prefix": "Рисунок",
        "tab_prefix": "Таблица",
        "fb_header": "💬 Кері байланыс қалдыру",
        "fb_text": "Ваши предложения или найденные ошибки",
        "fb_btn": "Отправить отзыв",
        "fb_succ": "Спасибо за ваш отзыв!",
        "preview": "Предпросмотр",
        "prog_title": "Готовность статьи",
        "prog_text": "Заполнено: {pct}% (Рекомендуется 100% перед генерацией)",
    },
    "kz": {
        "title": "📝 Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · Химия / География · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
        "nav_gen": "📄 Мақала генераторы",
        "nav_reg": "👤 Тіркелу",
        "sidebar_title": "⚙️ Баптаулар",
        "lbl_ui_font": "Интерфейс қаріпі",
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
        "lbl_fig_hint_title": "💡 Күрделі суреттер нұсқаулығы",
        "lbl_fig_hint_text": "Егер сурет бірнеше бөліктен (a, b, c) тұрса, бүкіл топ үшін <b>бір тегті</b> <code>[@fig1]</code> пайдаланыңыз.",
        "lbl_tab_hint_title": "💡 Күрделі кестелер нұсқаулығы",
        "lbl_tab_hint_text": "Кестеңіз өте кең болса немесе біріктірілген ұяшықтары болса, пішімдеуді сақтау үшін оны <b>.docx</b> форматында жүктеңіз.",
        "lbl_eq_hint_title": "💡 Формулалар нұсқаулығы",
        "lbl_eq_hint_text": "Формуланы енгізіңіз. Мәтінге <code>[@eq1]</code> тегін қойыңыз.",
        "btn_sample_table": "📥 Күрделі кесте үлгісін жүктеу",
        "lbl_samples": "📥 Файл үлгілерін жүктеп алу",
        "sec_backmatter": "4. Қосымша ақпарат (Back Matter)",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Метадеректер аудармасы",
        "trans_info": "Журнал талаптарына сәйкес атауын, авторларын, аңдатпасын және түйінді сөздерін басқа екі тілде ұсыну қажет.",
        "gen_btn": "🚀 Мақаланы генерациялау",
        "err_abs_len": "⚠️ Аңдатпа тым ұзын: {count} сөз. Максимум: 300.",
        "succ_abs_len": "Аңдатпадағы сөз саны: {count}/300",
        "err_fill_req": "Кем дегенде Атауын және Авторларын толтырыңыз.",
        "err_gen": "Генерация кезінде қате пайда болды: ",
        "succ_gen": "✅ Құжат сәтті генерацияланды ({time} сек)!",
        "btn_dl_docx": "⬇️ .docx жүктеу",
        "btn_dl_pdf": "⬇️ .pdf жүктеу",
        "err_pdf": "⚠️ PDF жасау мүмкін болмады (серверде LibreOffice қажет). Тек DOCX файлы қолжетімді.",
        "reg_header": "📝 Зерттеушіні тіркеу",
        "reg_name": "Аты-жөні (Толық)",
        "reg_email": "Сіздің Email",
        "reg_phone": "Телефон нөмірі (кодсыз)",
        "reg_code": "Код",
        "reg_org": "Ұйым / Университет",
        "reg_pos": "Қызметі / Мәртебесі (мысалы: Докторант)",
        "reg_submit": "Тіркелу",
        "reg_success": "✅ Сіз жүйеге сәтті тіркелдіңіз! Енді мақала генераторы қолжетімді.",
        "reg_info": "Сіз «Мақала генераторы» бөліміне өтіп, мақала жасай аласыз.",
        "reg_req_msg": "🔒 Мақала жасау үшін тіркелу формасын толтыру қажет.",
        "reg_err_fill": "Аты-жөні, Email және Телефонды дұрыс толтырыңыз.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ — Физикалық және экономикалық география кафедрасы",
        "browse_files": "Файлды таңдаңыз",
        "drag_drop": "Файлды осында сүйреңіз\nҚолдау көрсетілетін форматтар: txt, docx",
        "limit": "Шектеу 200MB",
        "fig_prefix": "Сурет",
        "tab_prefix": "Кесте",
        "fb_header": "💬 Кері байланыс қалдыру",
        "fb_text": "Сіздің ұсыныстарыңыз немесе табылған қателер",
        "fb_btn": "Пікір жіберу",
        "fb_succ": "Пікіріңіз үшін рақмет!",
        "preview": "Алдын ала көру",
        "prog_title": "Мақаланың дайындығы",
        "prog_text": "Толтырылды: {pct}% (Генерация алдында 100% ұсынылады)",
    },
    "en": {
        "title": "📝 Smart Paper Generator",
        "subtitle": "L.N. Gumilyov ENU Bulletin · Chemistry / Geography · 2025",
        "btn_theme_dark": "🌙 Dark mode",
        "btn_theme_light": "☀️ Light mode",
        "nav_gen": "📄 Paper Generator",
        "nav_reg": "👤 Registration",
        "sidebar_title": "⚙️ Paper Settings",
        "lbl_ui_font": "Interface Font",
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
        "sec_text": "2. Main Text (IMRAD Uploads)",
        "lbl_abstract": "Abstract (up to 300 words)",
        "lbl_kw": "Keywords",
        "lbl_kw_help": "Keyword 1; keyword 2; keyword 3 (3 to 10 words)",
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
        "lbl_fig_hint_title": "💡 Hint for Figures",
        "lbl_fig_hint_text": "If a figure has multiple parts (a, b, c), use a <b>single tag</b> <code>[@fig1]</code>.",
        "lbl_tab_hint_title": "💡 Instruction for Complex Tables",
        "lbl_tab_hint_text": "For wide tables or tables with merged cells, please upload a <b>.docx</b> file.",
        "lbl_eq_hint_title": "💡 Equation Hint",
        "lbl_eq_hint_text": "Enter your equation. Place the tag <code>[@eq1]</code> in your text.",
        "btn_sample_table": "📥 Download Complex Table Sample",
        "lbl_samples": "📥 Download Sample Files",
        "sec_backmatter": "4. Additional Information (Back Matter)",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Metadata Translations",
        "trans_info": "According to the journal requirements, the title, authors, abstract and keywords must be provided in two other languages.",
        "gen_btn": "🚀 Generate Document",
        "err_abs_len": "⚠️ Abstract is too long: {count} words. Maximum: 300.",
        "succ_abs_len": "Words in abstract: {count}/300",
        "err_fill_req": "Please fill in at least the Title and Authors.",
        "err_gen": "An error occurred during generation: ",
        "succ_gen": "✅ Document successfully generated in {time} sec!",
        "btn_dl_docx": "⬇️ Download .docx",
        "btn_dl_pdf": "⬇️ Download .pdf",
        "err_pdf": "⚠️ Failed to generate PDF (requires LibreOffice on the server). DOCX is available.",
        "reg_header": "📝 Researcher Registration",
        "reg_name": "Full Name",
        "reg_email": "Your Email",
        "reg_phone": "Phone Number (no code)",
        "reg_code": "Code",
        "reg_org": "Organization / University",
        "reg_pos": "Position / Status (e.g., PhD Student)",
        "reg_submit": "Register",
        "reg_success": "✅ You have successfully registered! The paper generator is now unlocked.",
        "reg_info": "You can now go to the 'Paper Generator' section.",
        "reg_req_msg": "🔒 To generate an article, you must complete the registration form.",
        "reg_err_fill": "Please correctly fill in your Name, Email, and Phone.",
        "f_author": "Kanat Samarkhanov",
        "f_license": "License",
        "f_univ": "L.N. Gumilyov ENU — Department of Physical and Economic Geography",
        "browse_files": "Browse files",
        "drag_drop": "Drag & drop files here\nSupported formats: txt, docx",
        "limit": "Limit 200MB",
        "fig_prefix": "Figure",
        "tab_prefix": "Table",
        "fb_header": "💬 Leave Feedback",
        "fb_text": "Your suggestions or found bugs",
        "fb_btn": "Submit Feedback",
        "fb_succ": "Thank you for your feedback!",
        "preview": "Preview",
        "prog_title": "Article Readiness",
        "prog_text": "Completed: {pct}% (100% recommended before generation)",
    }
}

l = locales[st.session_state.lang]

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

/* SMALLER TITLES */
h1 {{ font-size: 1.55rem !important; margin-bottom: 0.1rem !important; }}
h2 {{ font-size: 1.25rem !important; margin-bottom: 0.2rem !important; }}
h3 {{ font-size: 1.05rem !important; margin-bottom: 0.15rem !important; }}

/* MAIN CONTAINER WIDTH */
.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}}

/* -------------------------------- */
/* UPLOAD ZONES */
/* -------------------------------- */
[data-testid="stFileUploadDropzone"] {{
    border: 2px dashed #6aa5ff !important;
    border-radius: 14px !important;
    padding: 18px !important;
    transition: all 0.2s ease;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}}

[data-testid="stFileUploadDropzone"]:hover {{ border-color:#2563eb !important; }}

[data-testid="stFileUploadDropzone"] button {{
    border-radius:10px !important; padding:8px 20px !important; font-weight:600;
    color: transparent !important; position: relative; background-color: transparent !important;
    border: 1px solid #4a90e2 !important; box-shadow: none !important;
}}

[data-testid="stFileUploadDropzone"] button::after {{
    content: "{l['browse_files']}"; color: #4a90e2 !important; 
    position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
    visibility: visible; font-weight: 600; font-size: 14px; white-space: nowrap; 
}}

[data-testid="stFileUploadDropzone"] > div > svg {{ display: none !important; }}
[data-testid="stFileUploadDropzone"]::before {{ content:"📂"; font-size:28px; display:block; margin-bottom:4px; text-align: center; }}

[data-testid="stFileUploadDropzone"] div[data-testid="stText"]::after {{
    content: "{l['drag_drop']}"; font-size: 12px !important; color: #888888 !important; display: block; white-space: pre-wrap; margin-top: 5px;
}}

/* -------------------------------- */
/* COMPACT UPLOAD BUTTONS (STYLE FROM SCREENSHOT) */
/* -------------------------------- */
div.element-container:has(.compact-uploader) {{ display: none !important; }}
div.element-container:has(.compact-uploader) + div.element-container [data-testid="stFileUploadDropzone"] {{
    padding:0 !important; height:38px !important; border:1px dashed #9bbcf7 !important; border-radius:8px !important;
}}
div.element-container:has(.compact-uploader) + div.element-container [data-testid="stFileUploadDropzone"]::before {{ display: none !important; }}
div.element-container:has(.compact-uploader) + div.element-container [data-testid="stFileUploadDropzone"] button::after {{
    content: "{l['btn_upload_short']}" !important; font-size: 12px !important;
}}

/* -------------------------------- */
/* PRIMARY BUTTONS (BLUE) */
/* -------------------------------- */
button[kind="primary"] {{
    background: linear-gradient(90deg, #1d4ed8, #3b82f6) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 10px 20px !important; font-weight: bold !important; transition: all 0.2s ease !important;
    box-shadow: 0 2px 5px rgba(29, 78, 216, 0.2) !important;
}}
button[kind="primary"]:hover {{
    background: linear-gradient(90deg, #1e40af, #2563eb) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
}}

/* -------------------------------- */
/* INFO CARDS */
/* -------------------------------- */
.info-card {{ border-radius:14px; padding:15px; margin-bottom:10px; box-shadow:0 2px 6px rgba(0,0,0,0.04); }}
.info-card-title {{ font-weight:700; font-size:14px; margin-bottom:4px; }}
.info-card-text {{ font-size:12.5px; line-height:1.4; }}

/* Segmented Control */
div[data-testid="stRadio"] div[role="radiogroup"] {{ border-radius: 20px !important; padding: 4px !important; gap: 4px !important; }}
div[data-testid="stRadio"] div[role="radiogroup"] label {{ padding: 6px 20px !important; border-radius: 16px !important; font-size:13.5px !important; }}
</style>
"""

light_css = css_core + """
<style>
/* DAY MODE (LIGHT BLUE) - MATCHING SCREENSHOT */
.stApp { background: #f4f9ff !important; }
h1, h2, h3, h4, h5, h6 { color: #0c335e !important; }
p, span, label, div, li { color: #1e3a5f !important; }

/* Non-primary buttons style from screenshot (White bg, blue border/text) */
.stButton>button:not([kind="primary"]) {
    background: #ffffff !important; 
    color: #1d4ed8 !important; 
    border: 1px solid #cbdff2 !important;
}
.stButton>button:not([kind="primary"]):hover {
    background: #f0f7ff !important;
    border-color: #3b82f6 !important;
}

[data-testid="stFileUploadDropzone"] { background: #ffffff !important; border-color: #8bb4e5 !important; }
.info-card { background: #ffffff !important; border: 1px solid #d1e4f9 !important; }
.info-card-title { color: #0c335e !important; }
.info-card-text { color: #4b6a90 !important; }

/* Inputs (White background for clarity) */
input, textarea, [data-baseweb="select"] { 
    background-color: #ffffff !important; 
    color: #1e3a5f !important; 
    border: 1px solid #cbdff2 !important; 
}

/* Sidebar */
section[data-testid="stSidebar"] { background-color: #f4f9ff !important; }
</style>
"""

dark_css = css_core + """
<style>
/* DARK MODE (OCEAN BLUE) - NO BLACKS */
.stApp { background: #1a314d !important; }
h1, h2, h3, h4, h5, h6 { color: #d0e8ff !important; }
p, span, label, div, li { color: #e1f0ff !important; }

[data-testid='block-container'], section[data-testid='stSidebar'] { background-color: #1a314d !important; }

.stButton>button:not([kind="primary"]) {
    background: #2a528a !important; color: #ffffff !important; border: 1px solid #4a90e2 !important;
}

[data-testid="stFileUploadDropzone"] { background: #254b7c !important; border-color: #4ea1ff !important; }
.info-card { background: linear-gradient(180deg, #2a528a, #1a314d) !important; border: 1px solid #4a90e2 !important; }
.info-card-title { color: #d0e8ff !important; }
.info-card-text { color: #b6d4f0 !important; }

/* Inputs */
input, textarea, [data-baseweb="select"] { background-color: #2a528a !important; color: #ffffff !important; border: 1px solid #4a90e2 !important; }

/* Segmented */
div[data-testid="stRadio"] div[role="radiogroup"] { background-color: #112233 !important; }
div[data-testid="stRadio"] div[role="radiogroup"] label:has(div[aria-checked="true"]) { background-color: #3b82f6 !important; color: #ffffff !important; }
</style>
"""

st.markdown(dark_css if st.session_state.theme == "dark" else light_css, unsafe_allow_html=True)

# ----------------- HIDE SIDEBAR IF NOT REGISTERED -----------------
if not st.session_state.is_registered:
    st.markdown("<style>section[data-testid='stSidebar'] {display:none;}</style>", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.title(l["title"])
st.caption(l["subtitle"])

hcol1, hcol2, hcol3 = st.columns([6, 2, 2])
with hcol2:
    _lang_labels = {"kz": "🇰🇿 Қазақша", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    _lang_keys   = list(_lang_labels.keys())
    _sel = st.selectbox("lang", _lang_keys, index=_lang_keys.index(st.session_state.lang), format_func=lambda x: _lang_labels[x], label_visibility="collapsed")
    if _sel != st.session_state.lang:
        st.session_state.lang = _sel
        safe_rerun()
with hcol3:
    _tbtn = l["btn_theme_light"] if st.session_state.theme == "dark" else l["btn_theme_dark"]
    if st.button(_tbtn, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        safe_rerun()
st.markdown("---")

# ----------------- HELPERS -----------------
def extract_text(uploaded_file):
    if not uploaded_file: return ""
    try:
        if uploaded_file.name.endswith('.txt'): return uploaded_file.read().decode('utf-8')
        elif uploaded_file.name.endswith('.docx'):
            doc_file = docx.Document(uploaded_file)
            return '\n'.join([p.text for p in doc_file.paragraphs])
    except Exception as e: return f"[Error: {str(e)}]"
    return ""

def count_wc(text):
    if not text: return "0 / 0"
    words = len(text.split()); chars = len(text)
    return f"{words} / {chars}"

def create_sample_docx(section_title):
    doc = docx.Document()
    h = doc.add_heading(section_title, level=1); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(f"Content for {section_title}..."); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    bio = BytesIO(); doc.save(bio); return bio.getvalue()

# ----------------- LIVE PREVIEW UPLOADER -----------------
def render_live_uploader(label, key, loc_preview, is_locked):
    f = st.file_uploader(label, type=["txt", "docx"], disabled=is_locked, key=key)
    if f:
        text = extract_text(f); wc = count_wc(text)
        with st.expander(f"👀 {loc_preview} ({wc})", expanded=True):
            bg = "#2a528a" if st.session_state.theme == "dark" else "#ffffff"
            st.markdown(f"<div style='max-height:140px; overflow-y:auto; font-size:12px; padding:10px; background:{bg}; border:1px solid #4a90e2; border-radius:8px;'>{text}</div>", unsafe_allow_html=True)
    return f

# ----------------- NAVIGATION -----------------
app_mode = st.radio("", [l["nav_gen"], l["nav_reg"]], horizontal=True, label_visibility="collapsed", key="nav_radio")
st.markdown("---")

is_locked = not st.session_state.is_registered

# ======================================================================
# GENERATOR MODE
# ======================================================================
if app_mode == l["nav_gen"]:
    progress_placeholder = st.empty()
    if is_locked: st.error(l["reg_req_msg"], icon="🔒")

    st.subheader(l["sidebar_title"])
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
    with col_s1: primary_lang = st.selectbox(l["lbl_lang"], ["Русский", "Қазақша", "English"], disabled=is_locked)
    with col_s2: section = st.selectbox(l["lbl_sec"], ["Химия", "География"], disabled=is_locked)
    with col_s3: paper_type = st.selectbox(l["lbl_type"], ["Статья (Article)", "Обзор (Review)"], disabled=is_locked)
    with col_s4: mrnti = st.text_input(l["lbl_mrnti"], value="06.81.23", disabled=is_locked)
    with col_s5: st.selectbox(l["lbl_ui_font"], list(font_mapping.keys()), key="ui_font_select")

    st.header(l["sec_meta"])
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_area(l["lbl_title"], height=68, disabled=is_locked)
        authors = st.text_area(l["lbl_authors"], height=68, disabled=is_locked)
    with col2:
        affiliations = st.text_area(l["lbl_affil"], height=68, disabled=is_locked)
        corr_email = st.text_input(l["lbl_email"], disabled=is_locked)

    st.header(l["sec_text"])
    abstract = st.text_area(l["lbl_abstract"], height=110, disabled=is_locked)
    keywords = st.text_input(l["lbl_kw"], disabled=is_locked)

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        file_intro = render_live_uploader(l["lbl_intro"], "up_intro", l["preview"], is_locked)
        file_methods = render_live_uploader(l["lbl_methods"], "up_meth", l["preview"], is_locked)
    with col_i2:
        file_results = render_live_uploader(l["lbl_results"], "up_res", l["preview"], is_locked)
        file_discussion = render_live_uploader(l["lbl_discussion"], "up_disc", l["preview"], is_locked)
    with col_i3:
        file_conclusion = render_live_uploader(l["lbl_conclusion"], "up_conc", l["preview"], is_locked)

    col_ft1, col_ft2 = st.columns(2)
    with col_ft1:
        st.header(l["lbl_fig_manager"])
        st.markdown(f"<div class='info-card'><div class='info-card-title'>{l['lbl_fig_hint_title']}</div><div class='info-card-text'>{l['lbl_fig_hint_text']}</div></div>", unsafe_allow_html=True)
        st.button(l["lbl_add_fig"], disabled=is_locked)
    with col_ft2:
        st.header(l["lbl_tab_manager"])
        st.markdown(f"<div class='info-card'><div class='info-card-title'>{l['lbl_tab_hint_title']}</div><div class='info-card-text'>{l['lbl_tab_hint_text']}</div></div>", unsafe_allow_html=True)
        st.button(l["lbl_add_tab"], disabled=is_locked)

    if not is_locked:
        tracked = [title, authors, affiliations, abstract, keywords, file_intro, file_methods, file_results, file_discussion, file_conclusion]
        pct = int((sum(bool(f) for f in tracked) / len(tracked)) * 100)
        p_color = "#3b82f6"; t_bg = "#112233" if st.session_state.theme == "dark" else "#e0efff"
        progress_placeholder.markdown(f"""
        <div class="info-card" style="margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="font-weight:700; font-size:13px;">{l['prog_title']}</span>
                <span style="font-weight:700;">{pct}%</span>
            </div>
            <div style="background:{t_bg}; border-radius:10px; height:8px; width:100%;"><div style="background:{p_color}; height:100%; width:{pct}%; border-radius:10px;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    st.button(l["gen_btn"], type="primary", use_container_width=True, disabled=is_locked)

# ======================================================================
# REGISTRATION MODE
# ======================================================================
elif app_mode == l["nav_reg"]:
    st.header(l["reg_header"])
    if st.session_state.is_registered:
        st.success(l["reg_success"])
    else:
        with st.form("reg_form"):
            r_name = st.text_input(l["reg_name"])
            r_email = st.text_input(l["reg_email"])
            r_phone = st.text_input(l["reg_phone"])
            r_org = st.text_input(l["reg_org"])
            r_pos = st.text_input(l["reg_pos"])
            if st.form_submit_button(l["reg_submit"], type="primary"):
                if r_name and r_email:
                    st.session_state.is_registered = True
                    safe_rerun()

# ----------------- FEEDBACK SECTION (OPEN) -----------------
st.markdown("---")
st.subheader(l["fb_header"])
with st.form("feedback_form", clear_on_submit=True):
    fb_email = st.text_input("Email (Optional)")
    fb_text = st.text_area(l["fb_text"], height=80)
    if st.form_submit_button(l["fb_btn"]):
        st.success(l["fb_succ"])

# ----------------- FOOTER -----------------
st.markdown("---")
f_color = "#8bb4e5" if st.session_state.theme == "dark" else "#555"
st.markdown(f"<div style='text-align:center; font-size:11px; color:{f_color}; padding:20px;'>© 2025 {l['f_author']} | {l['f_univ']}</div>", unsafe_allow_html=True)
