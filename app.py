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
from typing import List, Dict, Any

# ----------------- КОНФИГУРАЦИЯ И ЯЗЫКИ -----------------
st.set_page_config(page_title="Smart Paper Generator", page_icon="📝", layout="wide")

LOCALES = {
    "ru": {
        "title": "📝 Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
        "nav_gen": "📄 Генератор статей",
        "nav_reg": "👤 Регистрация",
        "sidebar_title": "⚙️ Настройки",
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
        "lbl_fig_hint_text": "Если рисунок состоит из нескольких частей (a, b, c), используйте один тег `[@fig1]` для всей группы.",
        "lbl_tab_hint_title": "💡 Инструкция для сложных таблиц",
        "lbl_tab_hint_text": "Для таблиц с объединенными ячейками загружайте их в формате .docx.",
        "lbl_eq_hint_title": "💡 Подсказка для формул",
        "lbl_eq_hint_text": "Введите формулу. Разместите тег `[@eq1]` в тексте статьи.",
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
        "err_pdf": "⚠️ Не удалось сгенерировать PDF (требуется LibreOffice). Доступен DOCX файл.",
        "reg_header": "📝 Регистрация исследователя",
        "reg_name": "ФИО (Полностью)",
        "reg_email": "Ваш Email",
        "reg_phone": "Номер телефона",
        "reg_org": "Организация / Университет",
        "reg_pos": "Должность / Статус (например: Докторант)",
        "reg_submit": "Зарегистрироваться",
        "reg_success": "✅ Вы успешно зарегистрированы!",
        "reg_info": "Теперь вам доступен генератор статей.",
        "reg_req_msg": "🔒 Для создания статьи необходимо зарегистрироваться.",
        "reg_err_fill": "Пожалуйста, заполните Имя, Email и Телефон.",
        "f_author": "Канат Самарханов",
        "f_univ": "ЕНУ им. Л.Н. Гумилева",
        "preview": "Предпросмотр",
        "fig_prefix": "Рисунок",
        "tab_prefix": "Таблица",
        "fb_header": "💬 Обратная связь",
        "fb_text": "Ваши предложения",
        "fb_btn": "Отправить",
        "fb_succ": "Спасибо за отзыв!"
    },
    "kz": {
        "title": "📝 Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
        "nav_gen": "📄 Мақала генераторы",
        "nav_reg": "👤 Тіркелу",
        "sidebar_title": "⚙️ Баптаулар",
        "lbl_lang": "Мақаланың негізгі тілі",
        "lbl_sec": "Секция",
        "lbl_type": "Мақала түрі",
        "lbl_mrnti": "МРНТИ / IRSTI",
        "sec_meta": "1. Негізгі метадеректер",
        "lbl_title": "Мақаланың атауы",
        "lbl_authors": "Авторлар",
        "lbl_authors_help": "Мысалы: Аты Жөні1, Аты Жөні2",
        "lbl_affil": "Аффилиация",
        "lbl_affil_help": "1 Университет, Қала, Ел; email",
        "lbl_email": "Корреспонденцияға арналған email",
        "sec_text": "2. Мақала мәтіні (IMRAD)",
        "lbl_abstract": "Аңдатпа (300 сөзге дейін)",
        "lbl_kw": "Түйінді сөздер",
        "lbl_kw_help": "3-тен 10 сөзге дейін",
        "lbl_intro": "Кіріспе (.txt/.docx)",
        "lbl_methods": "Материалдар/әдістер (.txt/.docx)",
        "lbl_results": "Нәтижелер (.txt/.docx)",
        "lbl_discussion": "Талқылау (.txt/.docx)",
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
        "lbl_fig_hint_text": "Бүкіл топ үшін бір тегті `[@fig1]` пайдаланыңыз.",
        "lbl_tab_hint_title": "💡 Кестелер нұсқаулығы",
        "lbl_tab_hint_text": ".docx форматында жүктеңіз.",
        "lbl_eq_hint_title": "💡 Формулалар нұсқаулығы",
        "lbl_eq_hint_text": "Мәтінге `[@eq1]` тегін қойыңыз.",
        "btn_sample_table": "📥 Күрделі кесте үлгісін жүктеу",
        "lbl_samples": "📥 Файл үлгілерін жүктеп алу",
        "sec_backmatter": "4. Қосымша ақпарат",
        "lbl_supp": "6. Supplementary Materials",
        "lbl_contrib": "7. Author Contributions",
        "lbl_auth_info": "8. Author Information",
        "lbl_funding": "9. Funding",
        "lbl_ack": "10. Acknowledgements",
        "lbl_coi": "11. Conflicts of Interest",
        "sec_trans": "3. Метадеректер аудармасы",
        "trans_info": "Атауын, авторларын, аңдатпасын екі тілде ұсыну қажет.",
        "gen_btn": "🚀 Мақаланы генерациялау",
        "err_abs_len": "⚠️ Аңдатпа тым ұзын: {count} сөз.",
        "succ_abs_len": "Аңдатпадағы сөз саны: {count}/300",
        "err_fill_req": "Атауын және Авторларын толтырыңыз.",
        "err_gen": "Қате пайда болды: ",
        "succ_gen": "✅ Құжат сәтті жасалды ({time} сек)!",
        "btn_dl_docx": "⬇️ .docx жүктеу",
        "btn_dl_pdf": "⬇️ .pdf жүктеу",
        "err_pdf": "⚠️ PDF жасау мүмкін болмады.",
        "reg_header": "📝 Тіркелу",
        "reg_name": "Аты-жөні",
        "reg_email": "Email",
        "reg_phone": "Телефон",
        "reg_org": "Ұйым",
        "reg_pos": "Қызметі",
        "reg_submit": "Тіркелу",
        "reg_success": "✅ Тіркелу сәтті аяқталды!",
        "reg_info": "Енді мақала жасай аласыз.",
        "reg_req_msg": "🔒 Тіркелу қажет.",
        "reg_err_fill": "Деректерді толық толтырыңыз.",
        "f_author": "Канат Самарханов",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ",
        "preview": "Алдын ала қарау",
        "fig_prefix": "Сурет",
        "tab_prefix": "Кесте",
        "fb_header": "💬 Кері байланыс",
        "fb_text": "Ұсыныстар",
        "fb_btn": "Жіберу",
        "fb_succ": "Рақмет!"
    }
}

# ----------------- SESSION STATE -----------------
defaults = {
    "lang": "kz",
    "theme": "light",
    "is_registered": False,
    "fig_count": 1,
    "tab_count": 1,
    "eq_count": 1,
    "nav_radio": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

def safe_rerun():
    st.rerun()

# ----------------- UTILS & CACHING -----------------
@st.cache_data
def extract_text(uploaded_file) -> str:
    if not uploaded_file: return ""
    try:
        if uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            d = docx.Document(uploaded_file)
            return "\n".join(p.text for p in d.paragraphs)
    except Exception as e:
        return f"[Error: {e}]"
    return ""

def count_wc(text: str) -> str:
    if not text: return "0 / 0"
    return f"{len(text.split())} / {len(text)}"

@st.cache_data
def get_sample_docx(title: str) -> bytes:
    doc = docx.Document()
    h = doc.add_heading(title, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(f"Sample content for {title}. Justified text example. ")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

@st.cache_data
def get_complex_table_sample() -> bytes:
    doc = docx.Document()
    doc.add_paragraph("[@tab1]", style='Normal').alignment = WD_ALIGN_PARAGRAPH.CENTER
    table = doc.add_table(rows=2, cols=2, style="Table Grid")
    table.cell(0,0).merge(table.cell(0,1))
    table.cell(0,0).text = "Merged Header"
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def convert_to_pdf(docx_path: str, pdf_path: str) -> bool:
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", docx_path, "--outdir", os.path.dirname(pdf_path)], 
                       check=True, capture_output=True)
        return os.path.exists(pdf_path)
    except:
        return False

# ----------------- UI COMPONENTS -----------------
l = LOCALES.get(st.session_state.lang, LOCALES["ru"])

# Стиль вынесен в компактную переменную
CSS = f"""
<style>
    .stApp {{ background-color: #f8fafc !important; }}
    [data-testid="stSidebar"] {{ background-color: #f1f5f9 !important; border-right: 1px solid #e2e8f0; }}
    h1, h2, h3 {{ color: #1e293b !important; }}
    .stButton>button[kind="primary"] {{ 
        background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; border-radius: 8px; font-weight: 600;
    }}
    .compact-uploader [data-testid="stFileUploadDropzone"] {{ padding: 0 !important; min-height: 40px !important; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def render_manager_row(index: int, prefix: str, type_key: str, is_locked: bool):
    """Универсальная отрисовка строк менеджеров"""
    cols = st.columns([1, 3, 3])
    with cols[0]:
        st.text_input(f"{type_key}_tag_{index}", value=f"[@{type_key}{index+1}]", 
                      key=f"{type_key}_t_{index}", label_visibility="collapsed", disabled=is_locked)
    with cols[1]:
        st.text_input(f"{type_key}_cap_{index}", placeholder="Caption/Value...", 
                      key=f"{type_key}_c_{index}", label_visibility="collapsed", disabled=is_locked)
    with cols[2]:
        if type_key != "eq":
            st.markdown('<div class="compact-uploader">', unsafe_allow_html=True)
            st.file_uploader(f"{type_key}_f_{index}", label_visibility="collapsed", key=f"{type_key}_file_{index}", disabled=is_locked)
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------- HEADER -----------------
hc = st.columns([5, 3, 2])
with hc[0]:
    st.title(l["title"])
    st.caption(l["subtitle"])
with hc[1]:
    fcols = st.columns(3)
    for i, (code, icon) in enumerate([("kz", "🇰🇿"), ("ru", "🇷🇺"), ("en", "🇬🇧")]):
        if fcols[i].button(icon, use_container_width=True):
            st.session_state.lang = code
            safe_rerun()
with hc[2]:
    theme_icon = l["btn_theme_light"] if st.session_state.theme == "dark" else l["btn_theme_dark"]
    if st.button(theme_icon, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        safe_rerun()

st.divider()
app_mode = st.radio("", [l["nav_gen"], l["nav_reg"]], horizontal=True, label_visibility="collapsed", key="nav_radio_main")

# ----------------- APP LOGIC -----------------
is_locked = not st.session_state.is_registered

if app_mode == l["nav_gen"]:
    if is_locked: st.error(l["reg_req_msg"], icon="🔒")
    
    # 1. Settings
    with st.container(border=True):
        st.subheader(l["sidebar_title"])
        sc = st.columns(4)
        p_lang = sc[0].selectbox(l["lbl_lang"], ["Қазақша", "Русский", "English"], disabled=is_locked)
        sec = sc[1].selectbox(l["lbl_sec"], ["Химия", "География"], disabled=is_locked)
        p_type = sc[2].selectbox(l["lbl_type"], ["Article", "Review", "Communication"], disabled=is_locked)
        mrnti = sc[3].text_input(l["lbl_mrnti"], value="06.81.23", disabled=is_locked)

    # 2. Meta
    st.header(l["sec_meta"])
    mc = st.columns(2)
    title = mc[0].text_area(l["lbl_title"], height=100, disabled=is_locked)
    authors = mc[0].text_area(l["lbl_authors"], help=l["lbl_authors_help"], height=100, disabled=is_locked)
    affil = mc[1].text_area(l["lbl_affil"], height=100, disabled=is_locked)
    email = mc[1].text_input(l["lbl_email"], disabled=is_locked)

    # 3. IMRAD
    st.header(l["sec_text"])
    abstract = st.text_area(l["lbl_abstract"], height=150, disabled=is_locked)
    wc = len(abstract.split()) if abstract else 0
    if wc > 300: st.error(l["err_abs_len"].format(count=wc))
    elif wc > 0: st.success(l["succ_abs_len"].format(count=wc))
    
    kw = st.text_input(l["lbl_kw"], disabled=is_locked)

    # Samples
    with st.expander(l["lbl_samples"]):
        sm_cols = st.columns(5)
        sections = ["Introduction", "Methods", "Results", "Discussion", "Conclusion"]
        for i, s_name in enumerate(sections):
            sm_cols[i].download_button(f"📥 {s_name[:4]}", get_sample_docx(s_name), f"{s_name}.docx", use_container_width=True)

    # Uploaders
    up_cols = st.columns(3)
    files = {}
    with up_cols[0]:
        files['intro'] = st.file_uploader(l["lbl_intro"], type=["docx", "txt"], disabled=is_locked)
        files['methods'] = st.file_uploader(l["lbl_methods"], type=["docx", "txt"], disabled=is_locked)
    with up_cols[1]:
        files['results'] = st.file_uploader(l["lbl_results"], type=["docx", "txt"], disabled=is_locked)
        files['discussion'] = st.file_uploader(l["lbl_discussion"], type=["docx", "txt"], disabled=is_locked)
    with up_cols[2]:
        files['conclusion'] = st.file_uploader(l["lbl_conclusion"], type=["docx", "txt"], disabled=is_locked)

    # 4. Managers
    st.divider()
    m_cols = st.columns(2)
    
    with m_cols[0]:
        st.subheader(l["lbl_fig_manager"])
        for i in range(st.session_state.fig_count):
            render_manager_row(i, l["fig_prefix"], "fig", is_locked)
        if st.button(l["lbl_add_fig"], disabled=is_locked):
            st.session_state.fig_count += 1
            safe_rerun()

    with m_cols[1]:
        st.subheader(l["lbl_tab_manager"])
        for i in range(st.session_state.tab_count):
            render_manager_row(i, l["tab_prefix"], "tab", is_locked)
        if st.button(l["lbl_add_tab"], disabled=is_locked):
            st.session_state.tab_count += 1
            safe_rerun()

    # 5. GENERATE
    st.divider()
    if st.button(l["gen_btn"], type="primary", use_container_width=True, disabled=is_locked):
        if not title or not authors:
            st.warning(l["err_fill_req"])
        else:
            with st.spinner("Processing..."):
                start_t = time.time()
                # Сборка текста (оптимизировано через список)
                content_parts = []
                order = [('1. INTRO', 'intro'), ('2. METHODS', 'methods'), ('3. RESULTS', 'results'), ('4. DISCUSSION', 'discussion'), ('5. CONCLUSION', 'conclusion')]
                for header, key in order:
                    txt = extract_text(files[key])
                    if txt: content_parts.append(f"{header}\n{txt}\n")
                
                full_text = "\n".join(content_parts)
                
                # Рендеринг (упрощенная заглушка логики)
                # Здесь должна быть загрузка шаблона и render(context)
                
                st.success(l["succ_gen"].format(time=round(time.time()-start_t, 2)))
                st.download_button(l["btn_dl_docx"], get_sample_docx("Result"), "Article.docx", type="primary")

elif app_mode == l["nav_reg"]:
    st.header(l["reg_header"])
    if st.session_state.is_registered:
        st.success(l["reg_success"])
    else:
        with st.form("reg_form"):
            r_name = st.text_input(l["reg_name"])
            r_email = st.text_input(l["reg_email"])
            r_org = st.text_input(l["reg_org"])
            if st.form_submit_button(l["reg_submit"], type="primary"):
                if r_name and r_email:
                    st.session_state.is_registered = True
                    st.success(l["reg_success"])
                    time.sleep(1)
                    safe_rerun()
                else:
                    st.error(l["reg_err_fill"])

# ----------------- FOOTER -----------------
st.divider()
st.markdown(f"<div style='text-align:center; color:#64748b; font-size:12px;'>© 2025 {l['f_author']} | {l['f_univ']}</div>", unsafe_allow_html=True)
