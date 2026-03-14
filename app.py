import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
import re

# Битнең көйләүләре (Беттің баптаулары)
st.set_page_config(page_title="Smart Paper Generator", page_icon="📝", layout="wide")

# Сессия халәтен башлау (Сессия күйлерін бастау)
if "lang"  not in st.session_state: st.session_state.lang  = "ru"
if "theme" not in st.session_state: st.session_state.theme = "light"

# Тәрҗемәләр сүзлеге (Аудармалар сөздігі)
locales = {
    "ru": {
        "title": "📝 Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
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
        "sec_text": "2. Текст статьи",
        "lbl_abstract": "Аннотация (до 300 слов)",
        "lbl_kw": "Ключевые слова",
        "lbl_kw_help": "Слово 1; слово 2; слово 3 (от 3 до 10 слов)",
        "lbl_main": "Основной текст статьи (Введение, Материалы, Результаты, Заключение)",
        "lbl_refs": "Список литературы (References)",
        "sec_trans": "3. Переводы метаданных",
        "trans_info": "По требованиям журнала необходимо предоставить название, авторов, аннотацию и ключевые слова на двух других языках.",
        "gen_btn": "🚀 Сгенерировать статью",
        "err_abs_len": "⚠️ Аннотация слишком длинная: {count} слов. Максимум: 300.",
        "succ_abs_len": "Слов в аннотации: {count}/300",
        "err_fill_req": "Пожалуйста, заполните хотя бы Название и Авторов.",
        "err_gen": "Произошла ошибка при генерации: ",
        "succ_gen": "✅ Документ успешно сгенерирован!",
        "btn_dl": "⬇️ Скачать .docx файл",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "ЕНУ им. Л.Н. Гумилева — Кафедра физической и экономической географии",
    },
    "kz": {
        "title": "📝 Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · Химия / География · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
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
        "sec_text": "2. Мақала мәтіні",
        "lbl_abstract": "Аңдатпа (300 сөзге дейін)",
        "lbl_kw": "Түйінді сөздер",
        "lbl_kw_help": "Сөз 1; сөз 2; сөз 3 (3-тен 10 сөзге дейін)",
        "lbl_main": "Мақаланың негізгі мәтіні (Кіріспе, Материалдар, Нәтижелер, Қорытынды)",
        "lbl_refs": "Әдебиеттер тізімі (References)",
        "sec_trans": "3. Метадеректер аудармасы",
        "trans_info": "Журнал талаптарына сәйкес атауын, авторларын, аңдатпасын және түйінді сөздерін басқа екі тілде ұсыну қажет.",
        "gen_btn": "🚀 Мақаланы генерациялау",
        "err_abs_len": "⚠️ Аңдатпа тым ұзын: {count} сөз. Максимум: 300.",
        "succ_abs_len": "Аңдатпадағы сөз саны: {count}/300",
        "err_fill_req": "Кем дегенде Атауын және Авторларын толтырыңыз.",
        "err_gen": "Генерация кезінде қате пайда болды: ",
        "succ_gen": "✅ Құжат сәтті генерацияланды!",
        "btn_dl": "⬇️ .docx файлын жүктеп алу",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ — Физикалық және экономикалық география кафедрасы",
    },
    "en": {
        "title": "📝 Smart Paper Generator",
        "subtitle": "L.N. Gumilyov ENU Bulletin · Chemistry / Geography · 2025",
        "btn_theme_dark": "🌙 Dark mode",
        "btn_theme_light": "☀️ Light mode",
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
        "sec_text": "2. Main Text",
        "lbl_abstract": "Abstract (up to 300 words)",
        "lbl_kw": "Keywords",
        "lbl_kw_help": "Keyword 1; keyword 2; keyword 3 (3 to 10 words)",
        "lbl_main": "Main Text (Introduction, Materials, Results, Conclusion)",
        "lbl_refs": "References",
        "sec_trans": "3. Metadata Translations",
        "trans_info": "According to the journal requirements, the title, authors, abstract and keywords must be provided in two other languages.",
        "gen_btn": "🚀 Generate Document",
        "err_abs_len": "⚠️ Abstract is too long: {count} words. Maximum: 300.",
        "succ_abs_len": "Words in abstract: {count}/300",
        "err_fill_req": "Please fill in at least the Title and Authors.",
        "err_gen": "An error occurred during generation: ",
        "succ_gen": "✅ Document successfully generated!",
        "btn_dl": "⬇️ Download .docx file",
        "f_author": "Kanat Samarkhanov",
        "f_license": "License",
        "f_univ": "L.N. Gumilyov ENU — Department of Physical and Economic Geography",
    }
}

l = locales[st.session_state.lang]

# ------------ CSS ТЕМАЛАРЫ (CSS тақырыптары) ------------
dark_css = (
    "<style>"
    "html,body,[class*='css'],.stApp{background-color:#0d1b2e !important;color:#c9d8ee !important;"
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif !important;}"
    "h1,h2,h3,h4,h5,h6,[data-testid='stMarkdownContainer'] h1,[data-testid='stMarkdownContainer'] h2,"
    "[data-testid='stMarkdownContainer'] h3{color:#e2edf7 !important;font-weight:600 !important;}"
    "p,span,label,div,li,[data-testid='stMarkdownContainer'] p,"
    "[data-testid='stCaptionContainer'],.stCaption{color:#c9d8ee !important;}"
    "[data-testid='block-container'],[data-testid='stVerticalBlock'],"
    "section[data-testid='stSidebar']{background-color:#0d1b2e !important;}"
    ".stButton>button{background-color:#0f2340 !important;color:#c9d8ee !important;"
    "border:1px solid #1e3a5f !important;border-radius:6px !important;}"
    ".stButton>button:hover{background-color:#1e3a5f !important;color:#e2edf7 !important;}"
    "[data-testid='stDownloadButton']>button{background-color:#238636 !important;color:#fff !important;"
    "border:1px solid #2ea043 !important;border-radius:6px !important;}"
    "[data-testid='stDownloadButton']>button:hover{background-color:#2ea043 !important;}"
    "input,textarea,select{background-color:#0f2340 !important;color:#c9d8ee !important;"
    "border:1px solid #1e3a5f !important;}"
    "[data-testid='stSelectbox']>div>div{background-color:#0f2340 !important;"
    "border:1px solid #1e3a5f !important;border-radius:6px !important;color:#c9d8ee !important;}"
    "[data-testid='stAlert']{background-color:#0f2340 !important;border:1px solid #1f6feb !important;"
    "color:#c9d8ee !important;border-radius:6px !important;}"
    "hr{border-color:#1e3a5f !important;}"
    "</style>"
)

light_css = (
    "<style>"
    "h1,h2,h3{color:#1a3a5c;}"
    "[data-testid='stDownloadButton']>button{background-color:#2ea043;color:#fff;border-radius:6px;}"
    "</style>"
)

# CSS стильләрен куллану (CSS стильдерін қолдану)
st.markdown(dark_css if st.session_state.theme == "dark" else light_css, unsafe_allow_html=True)

# ------------ БАШЛЫК (Тақырып) ------------
hc1, hc2, hc3 = st.columns([6, 1.8, 1.8])
with hc1:
    st.title(l["title"])
    st.caption(l["subtitle"])
with hc2:
    _lang_labels = {"kz": "🇰🇿 Қазақша", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    _lang_keys   = list(_lang_labels.keys())
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


# ------------ ЯНДАГЫ ПАНЕЛЬ (Бүйірлік тақта) ------------
with st.sidebar:
    st.header(l["sidebar_title"])
    
    primary_lang = st.selectbox(
        l["lbl_lang"],
        ["Русский", "Қазақша", "English"]
    )
    
    section = st.selectbox(
        l["lbl_sec"],
        ["Химия", "География"]
    )
    
    paper_type = st.selectbox(
        l["lbl_type"],
        ["Научная статья (Article)", "Обзор (Review)", "Мини-обзор (Mini-review)", "Краткое сообщение (Communication)"]
    )
    
    mrnti = st.text_input(l["lbl_mrnti"], value="06.81.23")


# ------------ ТӨП ФОРМАЛАР (Негізгі формалар) ------------
st.header(l["sec_meta"])
col1, col2 = st.columns(2)

with col1:
    title = st.text_area(l["lbl_title"], height=68)
    authors = st.text_area(l["lbl_authors"], help=l["lbl_authors_help"], height=68)

with col2:
    affiliations = st.text_area(l["lbl_affil"], help=l["lbl_affil_help"], height=68)
    corr_email = st.text_input(l["lbl_email"])


st.header(l["sec_text"])
abstract = st.text_area(l["lbl_abstract"], height=150)
abstract_word_count = len(abstract.split())

if abstract_word_count > 300:
    st.error(l["err_abs_len"].format(count=abstract_word_count))
elif abstract_word_count > 0:
    st.success(l["succ_abs_len"].format(count=abstract_word_count))

keywords = st.text_input(l["lbl_kw"], help=l["lbl_kw_help"])
main_text = st.text_area(l["lbl_main"], height=300)
references = st.text_area(l["lbl_refs"], height=200)


# ------------ ТӘРҖЕМӘЛӘР (Аудармалар) ------------
st.header(l["sec_trans"])
st.info(l["trans_info"])

# Телләр логикасы (Тілдер логикасы)
trans_langs = ["Русский", "Қазақша", "English"]
if primary_lang in trans_langs:
    trans_langs.remove(primary_lang)

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader(f"{trans_langs[0]}")
    t1_title = st.text_input(f"{l['lbl_title']} ({trans_langs[0]})")
    t1_authors = st.text_input(f"{l['lbl_authors']} ({trans_langs[0]})")
    t1_abstract = st.text_area(f"{l['lbl_abstract']} ({trans_langs[0]})", height=100)
    t1_keywords = st.text_input(f"{l['lbl_kw']} ({trans_langs[0]})")

with col_t2:
    st.subheader(f"{trans_langs[1]}")
    t2_title = st.text_input(f"{l['lbl_title']} ({trans_langs[1]})")
    t2_authors = st.text_input(f"{l['lbl_authors']} ({trans_langs[1]})")
    t2_abstract = st.text_area(f"{l['lbl_abstract']} ({trans_langs[1]})", height=100)
    t2_keywords = st.text_input(f"{l['lbl_kw']} ({trans_langs[1]})")


# ------------ ГЕНЕРАЦИЯ (Генерациялау) ------------
st.markdown("---")
generate_btn = st.button(l["gen_btn"], type="primary", use_container_width=True)

if generate_btn:
    if abstract_word_count > 300:
        st.error(l["err_abs_len"].format(count=abstract_word_count))
    elif not title or not authors:
        st.warning(l["err_fill_req"])
    else:
        try:
            # Шаблонны сайлау (Үлгіні таңдау)
            template_filename = "Russian_template_2025.docx" 
            if primary_lang == "Русский":
                template_filename = "Russian_template_2025.docx"
            elif primary_lang == "Қазақша":
                template_filename = "Kazakh_template_2025.docx"
            elif primary_lang == "English":
                template_filename = "English_template_2025.docx"
                
            # Сүзлек төзү (Сөздік құру)
            context = {
                'mrnti': mrnti,
                'section': section,
                'paper_type': paper_type,
                'title': title,
                'authors': authors,
                'affiliations': affiliations,
                'corr_email': corr_email,
                'abstract': abstract,
                'keywords': keywords,
                'main_text': main_text,
                'references': references,
                't1_title': t1_title,
                't1_authors': t1_authors,
                't1_abstract': t1_abstract,
                't1_keywords': t1_keywords,
                't2_title': t2_title,
                't2_authors': t2_authors,
                't2_abstract': t2_abstract,
                't2_keywords': t2_keywords
            }
            
            # Файлны барлыкка китерү (Файлды жасау)
            doc = DocxTemplate(template_filename)
            doc.render(context)
            
            bio = BytesIO()
            doc.save(bio)
            
            st.success(l["succ_gen"])
            st.balloons()
            
            st.download_button(
                label=l["btn_dl"],
                data=bio.getvalue(),
                file_name="Formatted_Article.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"{l['err_gen']} {e}")
            st.info("💡 Исеге төшерү: Генерация дөрес эшләсен өчен, 'Russian_template_2025.docx', 'Kazakh_template_2025.docx' һәм 'English_template_2025.docx' дигән файллар app.py белән бер папкада булырга тиеш.")


# ------------ АСКЫ КОЛОНТИТУЛ (Төменгі колонтитул) ------------
fc  = "#7b96b8" if st.session_state.theme == "dark" else "#555"
flk = "#58a6ff"  if st.session_state.theme == "dark" else "#0969da"
st.markdown("---")
st.markdown(
    f'<div style="text-align:center;font-size:12px;color:{fc};padding:12px 0 20px 0;line-height:2.2;">'
    f'<b style="font-size:13px;">© 2025 {l["f_author"]}</b><br>'
    f'📧 <a href="mailto:samarkhanov_kb@enu.kz" style="color:{flk};text-decoration:none;">samarkhanov_kb@enu.kz</a>'
    f'&nbsp;·&nbsp;'
    f'<a href="mailto:kanat.baurzhanuly@gmail.com" style="color:{flk};text-decoration:none;">kanat.baurzhanuly@gmail.com</a><br>'
    f'🏛️ <a href="https://fns.enu.kz/kz/page/departments/physical-and-economical-geography/faculty-members"'
    f'     target="_blank" style="color:{flk};text-decoration:none;">{l["f_univ"]}</a><br>'
    f'📄 {l["f_license"]}:&nbsp;'
    f'<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" style="color:{flk};text-decoration:none;">'
    f'CC BY 4.0 — Creative Commons Attribution 4.0 International</a>'
    f'</div>',
    unsafe_allow_html=True)