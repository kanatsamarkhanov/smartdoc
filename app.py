import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
import csv
import datetime
import os
import requests
import base64
import io

# Беттің баптаулары (Настройка страницы)
st.set_page_config(page_title="Smart Paper Generator", page_icon="📝", layout="wide")

# Сессия күйлерін бастау (Инициализация состояния сессии)
if "lang" not in st.session_state: 
    st.session_state.lang = "kz"
if "theme" not in st.session_state: 
    st.session_state.theme = "light"
if "is_registered" not in st.session_state:
    st.session_state.is_registered = False

# Аудармалар сөздігі (Словарь переводов)
locales = {
    "ru": {
        "title": "📝 Умный генератор научных статей",
        "subtitle": "Вестник ЕНУ им. Л.Н. Гумилева · Химия / География · 2025",
        "btn_theme_dark": "🌙 Тёмная тема",
        "btn_theme_light": "☀️ Светлая тема",
        "nav_title": "🧭 Навигация",
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
        "reg_header": "📝 Регистрация исследователя",
        "reg_name": "ФИО (Полностью)",
        "reg_email": "Ваш Email",
        "reg_phone": "Номер телефона",
        "reg_org": "Организация / Университет",
        "reg_pos": "Должность / Статус (например: Докторант)",
        "reg_submit": "Зарегистрироваться",
        "reg_success": "✅ Вы успешно зарегистрированы! Теперь вам доступен генератор статей.",
        "reg_req_msg": "🔒 Для создания статьи необходимо заполнить форму регистрации. Перейдите в раздел «Регистрация» в боковом меню.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "ЕНУ им. Л.Н. Гумилева — Кафедра физической и экономической географии",
    },
    "kz": {
        "title": "📝 Ғылыми мақалалардың ақылды генераторы",
        "subtitle": "Л.Н. Гумилев атындағы ЕҰУ Хабаршысы · Химия / География · 2025",
        "btn_theme_dark": "🌙 Түнгі режим",
        "btn_theme_light": "☀️ Күндізгі режим",
        "nav_title": "🧭 Навигация",
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
        "reg_header": "📝 Зерттеушіні тіркеу",
        "reg_name": "Аты-жөні (Толық)",
        "reg_email": "Сіздің Email",
        "reg_phone": "Телефон нөмірі",
        "reg_org": "Ұйым / Университет",
        "reg_pos": "Қызметі / Мәртебесі (мысалы: Докторант)",
        "reg_submit": "Тіркелу",
        "reg_success": "✅ Сіз жүйеге сәтті тіркелдіңіз! Енді мақала генераторы қолжетімді.",
        "reg_req_msg": "🔒 Мақала жасау үшін тіркелу формасын толтыру қажет. Бүйірлік мәзірдегі «Тіркелу» бөліміне өтіңіз.",
        "f_author": "Канат Самарханов / Kanat Samarkhanov",
        "f_license": "Лицензия",
        "f_univ": "Л.Н. Гумилев атындағы ЕҰУ — Физикалық және экономикалық география кафедрасы",
    },
    "en": {
        "title": "📝 Smart Paper Generator",
        "subtitle": "L.N. Gumilyov ENU Bulletin · Chemistry / Geography · 2025",
        "btn_theme_dark": "🌙 Dark mode",
        "btn_theme_light": "☀️ Light mode",
        "nav_title": "🧭 Navigation",
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
        "reg_header": "📝 Researcher Registration",
        "reg_name": "Full Name",
        "reg_email": "Your Email",
        "reg_phone": "Phone Number",
        "reg_org": "Organization / University",
        "reg_pos": "Position / Status (e.g., PhD Student)",
        "reg_submit": "Register",
        "reg_success": "✅ You have successfully registered! The paper generator is now unlocked.",
        "reg_req_msg": "🔒 To generate an article, you must complete the registration form. Please go to the 'Registration' section in the sidebar.",
        "f_author": "Kanat Samarkhanov",
        "f_license": "License",
        "f_univ": "L.N. Gumilyov ENU — Department of Physical and Economic Geography",
    }
}

l = locales[st.session_state.lang]

# ------------ CSS Дизайн (Ақ және Қою көк режимдер) ------------
light_css = """
<style>
/* Основной фон и боковая панель */
.stApp { background-color: #ffffff !important; }
[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e9ecef !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: #1a3a5c !important; }
p, span, label { color: #333333 !important; }
hr { border-color: #e9ecef !important; }

/* Обычные активные поля ввода (Светло-голубой фон как на скриншоте) */
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

/* ЗАБЛОКИРОВАННЫЕ поля (до регистрации) - серые */
input[disabled], textarea[disabled], [data-baseweb="select"] > div[aria-disabled="true"] {
    background-color: #e9ecef !important;
    color: #6c757d !important;
    -webkit-text-fill-color: #6c757d !important;
    border: 1px solid #dddddd !important;
}

/* Панели предупреждений и инфо (Alerts) */
[data-testid="stAlert"] {
    background-color: #f0f2f6 !important;
    color: #333333 !important;
}
</style>
"""

dark_css = """
<style>
/* Основной фон и боковая панель для ночного режима */
.stApp { background-color: #0d1b2e !important; }
[data-testid="stSidebar"] { background-color: #0b1727 !important; border-right: 1px solid #1e3a5f !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: #e2edf7 !important; }
p, span, label { color: #c9d8ee !important; }
hr { border-color: #1e3a5f !important; }

/* Обычные активные поля ввода (Светящийся контур как на скриншоте 2) */
input, textarea, [data-baseweb="select"] > div {
    background-color: #172a45 !important;
    color: #e2edf7 !important;
    border: 1px solid #2e5cb8 !important;
    box-shadow: 0 0 3px rgba(46, 92, 184, 0.4) !important;
    border-radius: 6px !important;
}
input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within {
    border: 1px solid #4a86e8 !important;
    box-shadow: 0 0 6px rgba(74, 134, 232, 0.6) !important;
}

/* ЗАБЛОКИРОВАННЫЕ поля в ночном режиме (без свечения) */
input[disabled], textarea[disabled], [data-baseweb="select"] > div[aria-disabled="true"] {
    background-color: #0b1727 !important;
    color: #7b96b8 !important;
    -webkit-text-fill-color: #7b96b8 !important;
    border: 1px solid #152b4a !important;
    box-shadow: none !important;
}

/* Панели предупреждений и инфо (Alerts) */
[data-testid="stAlert"] {
    background-color: #0f2340 !important;
    color: #c9d8ee !important;
    border: 1px solid #1e3a5f !important;
}
</style>
"""

st.markdown(dark_css if st.session_state.theme == "dark" else light_css, unsafe_allow_html=True)


# ------------ GitHub API Интеграциясы ------------
def append_to_github_csv(filename, row_data, header_data):
    # Streamlit Cloud құпия кілттерін оқу (Оқу орындалмаса, локальді сақтайды)
    try:
        github_token = st.secrets["GITHUB_TOKEN"]
        github_repo = st.secrets["GITHUB_REPO"]
    except Exception:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header_data)
            writer.writerow(row_data)
        return

    # GitHub-қа жіберу логикасы
    url = f"https://api.github.com/repos/{github_repo}/contents/{filename}"
    headers = {"Authorization": f"token {github_token}"}
    
    response = requests.get(url, headers=headers)
    sha = None
    content = ""
    if response.status_code == 200:
        data = response.json()
        sha = data['sha']
        content = base64.b64decode(data['content']).decode('utf-8')
    
    output = io.StringIO()
    writer = csv.writer(output)
    if not content:
        writer.writerow(header_data)
    writer.writerow(row_data)
    
    new_content = content + output.getvalue()
    payload = {
        "message": f"Жаңа дерек қосылды: {filename}",
        "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
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
    header = ["Уақыты (Timestamp)", "Аты-жөні (Full Name)", "Email", "Телефон (Phone)", "Ұйым (Organization)", "Лауазымы (Position)"]
    append_to_github_csv("registered_users.csv", row, header)


# ------------ Басты Тақырып ------------
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

# ------------ Навигация (Бүйірлік мәзір) ------------
with st.sidebar:
    st.header(l["nav_title"])
    app_mode = st.radio("", [l["nav_gen"], l["nav_reg"]], label_visibility="collapsed")
    st.markdown("---")

# Тіркелмеген жағдайда бұғаттау айнымалысы
is_locked = not st.session_state.is_registered

# ==========================================
# РЕЖИМ: ГЕНЕРАТОР (МАҚАЛА ЖАСАУ)
# ==========================================
if app_mode == l["nav_gen"]:
    
    if is_locked:
        st.error(l["reg_req_msg"], icon="🔒")
        
    with st.sidebar:
        st.header(l["sidebar_title"])
        primary_lang = st.selectbox(l["lbl_lang"], ["Русский", "Қазақша", "English"], disabled=is_locked)
        section = st.selectbox(l["lbl_sec"], ["Химия", "География"], disabled=is_locked)
        paper_type = st.selectbox(l["lbl_type"], ["Научная статья (Article)", "Обзор (Review)", "Мини-обзор (Mini-review)", "Краткое сообщение (Communication)"], disabled=is_locked)
        mrnti = st.text_input(l["lbl_mrnti"], value="06.81.23", disabled=is_locked)

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
    main_text = st.text_area(l["lbl_main"], height=300, disabled=is_locked)
    references = st.text_area(l["lbl_refs"], height=200, disabled=is_locked)

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
                template_filename = "Russian_template_2025.docx" 
                if primary_lang == "Русский": template_filename = "Russian_template_2025.docx"
                elif primary_lang == "Қазақша": template_filename = "Kazakh_template_2025.docx"
                elif primary_lang == "English": template_filename = "English_template_2025.docx"
                    
                context = {
                    'mrnti': mrnti, 'section': section, 'paper_type': paper_type,
                    'title': title, 'authors': authors, 'affiliations': affiliations,
                    'corr_email': corr_email, 'abstract': abstract, 'keywords': keywords,
                    'main_text': main_text, 'references': references,
                    't1_title': t1_title, 't1_authors': t1_authors, 't1_abstract': t1_abstract, 't1_keywords': t1_keywords,
                    't2_title': t2_title, 't2_authors': t2_authors, 't2_abstract': t2_abstract, 't2_keywords': t2_keywords
                }
                
                doc = DocxTemplate(template_filename)
                doc.render(context)
                
                bio = BytesIO()
                doc.save(bio)
                
                st.success(l["succ_gen"])
                st.balloons()
                
                # Журналды GitHub-қа немесе локальді файлға жазу
                with st.spinner("Деректер сақталуда... (Сохранение логов)"):
                    log_generation(title, authors, primary_lang)
                
                st.download_button(
                    label=l["btn_dl"],
                    data=bio.getvalue(),
                    file_name="Formatted_Article.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
            except Exception as e:
                st.error(f"{l['err_gen']} {e}")
                st.info("💡 Ескерту: 'Russian_template_2025.docx', 'Kazakh_template_2025.docx' және 'English_template_2025.docx' файлдары бумада болуы тиіс.")


# ==========================================
# РЕЖИМ: РЕГИСТРАЦИЯ (ТІРКЕЛУ)
# ==========================================
elif app_mode == l["nav_reg"]:
    st.header(l["reg_header"])
    
    if st.session_state.is_registered:
        st.success(l["reg_success"])
        st.info("Сіз 'Генератор' бөліміне өтіп, мақала жасай аласыз. / Вы можете перейти в раздел 'Генератор статей'.")
    else:
        with st.form("registration_form"):
            r_name = st.text_input(l["reg_name"])
            r_email = st.text_input(l["reg_email"])
            r_phone = st.text_input(l["reg_phone"]) # Телефон нөмірін сұрау қосылды
            r_org = st.text_input(l["reg_org"])
            r_pos = st.text_input(l["reg_pos"])
            
            submitted = st.form_submit_button(l["reg_submit"], type="primary")
            
            if submitted:
                if r_name and r_email and r_phone:
                    with st.spinner("Тіркелу жүріп жатыр... (Идет регистрация)"):
                        log_registration(r_name, r_email, r_phone, r_org, r_pos)
                    st.session_state.is_registered = True
                    st.success(l["reg_success"])
                    st.rerun() 
                else:
                    st.error("Аты-жөні, Email және Телефонды толтырыңыз. / Пожалуйста, заполните Имя, Email и Телефон.")

# ------------ Төменгі колонтитул (Footer) ------------
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
    unsafe_allow_html=True)
