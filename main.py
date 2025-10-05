import os, time, urllib.parse, uuid, json
import requests
import streamlit as st

# ---------------------------
# SAFE secrets/env loader (prevents StreamlitSecretNotFoundError)
# ---------------------------
def secret_or_env(key: str):
    v = os.environ.get(key)
    if v:
        return v
    try:
        return st.secrets[key]  # will raise if secrets.toml isn’t present
    except Exception:
        return None

# Optional integrations (auto-detected)
SUPABASE_URL        = secret_or_env("SUPABASE_URL")
SUPABASE_KEY        = secret_or_env("SUPABASE_KEY")
OPENWEATHER_API_KEY = secret_or_env("OPENWEATHER_API_KEY")
MAPBOX_TOKEN        = secret_or_env("MAPBOX_TOKEN")

# Optional: Supabase persistence
SUPABASE = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        SUPABASE = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.sidebar.error(f"Supabase init failed: {e}")

st.set_page_config(page_title="CareCompanion", page_icon="💚", layout="wide")

# ---------------------------
# i18n (English/Spanish)
# ---------------------------
LANGS = {"en": "English", "es": "Español"}
T = {
  "en": {
    "title": "CareCompanion 💚",
    "tag": "Prevent • Manage • Thrive",
    "caregiver": "Caregiver Mode",
    "name": "Your name",
    "level": "Level",
    "xp": "XP",
    "diet": "🥗 Diet",
    "edu": "📘 Education",
    "ex": "🏃 Exercise",
    "res": "🔗 Resources",
    "share": "👪 Share",
    "conditions": "My Conditions",
    "prefs": "Dietary Preferences",
    "budgets": "Daily Budgets",
    "sodium": "Sodium (mg)",
    "sugar": "Added Sugar (g)",
    "endday": "End Day & Check Budget",
    "underbudgets": "Great job staying under budget! +30 XP 🎉",
    "overbudgets": "Budgets exceeded — tomorrow is a fresh start!",
    "recipes": "Recommended recipes",
    "video": "▶️ Video",
    "add_meal": "Add to Meal Plan (+15 XP)",
    "cook_along": "Cook-Along (10-min)",
    "save": "Save",
    "coach_cook": "👩‍🍳 Coach Cook",
    "step_done": "Step Done (+2 XP)",
    "cancel": "Cancel Cook-Along",
    "cook_done": "Cook-along complete! +10 XP",
    "quiz": "Daily Lesson & Quiz",
    "submit": "Submit",
    "next": "Next Question",
    "streak": "Quiz Streak",
    "boss": "Boss Level",
    "boss_unlock": "Get a 5-day quiz streak to unlock the Boss Level.",
    "boss_ready": "Unlocked! Scenario: Dining Out with Diabetes & Hypertension",
    "boss_submit": "Submit Boss Level",
    "boss_win": "Boss defeated! +100 XP — Badge unlocked: Restaurant Strategist",
    "boss_try": "Close! Review the Education tab and try again tomorrow.",
    "activity": "Daily Activity Tracker",
    "plus_steps": "+500 steps",
    "log_walk": "Log Walk (+8 XP)",
    "goal": "Daily Step Goal",
    "strava": "Link Strava (mock)",
    "gc2": "GeoChallenges 2.0",
    "adverse": "When weather/AQI is adverse, we suggest indoor routines to protect lungs & keep streaks alive.",
    "zip": "Enter ZIP code",
    "indoor": "Indoor Cardio Routine (8-min)",
    "start_indoor": "Start Indoor Routine (+12 XP)",
    "open_video": "Open Guided Video",
    "park_challenge": "Challenge: Walk 2 laps or jog 10 min.",
    "directions": "Directions",
    "hub": "Resource Hub",
    "not_med": "Educational links; not medical advice. Talk to your clinician for personal care.",
    "share_hdr": "Care Circle Sharing",
    "share_cap": "Generate a read-only URL for caregivers. Choose what to include:",
    "inc_act": "Include Activity",
    "inc_edu": "Include Education",
    "inc_diet": "Include Diet",
    "suffix": "URL Suffix",
    "privacy": "Privacy: You control caregiver access & data sharing settings.",
    "claim": "Claim Weekly Challenge (+50 XP)",
    "summary": "Caregiver Summary (7 days):",
    "avg_steps": "- Avg steps: 7,350",
    "lessons_done": "- Lessons completed: 5",
    "meals_logged": "- Healthy meals logged: 9",
    "simple": "Simple UI (High Contrast / Large Type)",
    "lang": "Language",
    "live_ctx": "Live Context",
    "weather": "Weather",
    "aqi": "Air Quality",
  },
  "es": {
    "title": "CareCompanion 💚",
    "tag": "Prevenir • Gestionar • Prosperar",
    "caregiver": "Modo cuidador",
    "name": "Tu nombre",
    "level": "Nivel",
    "xp": "XP",
    "diet": "🥗 Alimentación",
    "edu": "📘 Educación",
    "ex": "🏃 Ejercicio",
    "res": "🔗 Recursos",
    "share": "👪 Compartir",
    "conditions": "Mis condiciones",
    "prefs": "Preferencias alimentarias",
    "budgets": "Presupuestos diarios",
    "sodium": "Sodio (mg)",
    "sugar": "Azúcares añadidos (g)",
    "endday": "Terminar día y comprobar presupuesto",
    "underbudgets": "¡Excelente! Dentro del presupuesto. +30 XP 🎉",
    "overbudgets": "Presupuestos superados — ¡mañana es un nuevo comienzo!",
    "recipes": "Recetas recomendadas",
    "video": "▶️ Video",
    "add_meal": "Añadir al plan (+15 XP)",
    "cook_along": "Cocinar juntos (10 min)",
    "save": "Guardar",
    "coach_cook": "👩‍🍳 Coach Cook",
    "step_done": "Paso listo (+2 XP)",
    "cancel": "Cancelar",
    "cook_done": "¡Cocinado completo! +10 XP",
    "quiz": "Lección y cuestionario diarios",
    "submit": "Enviar",
    "next": "Siguiente pregunta",
    "streak": "Racha",
    "boss": "Nivel Jefe",
    "boss_unlock": "Consigue una racha de 5 días para desbloquear el Nivel Jefe.",
    "boss_ready": "¡Desbloqueado! Escenario: Cenar fuera con diabetes e hipertensión",
    "boss_submit": "Enviar Nivel Jefe",
    "boss_win": "¡Jefe vencido! +100 XP — Insignia: Estratega en restaurante",
    "boss_try": "¡Casi! Revisa la pestaña Educación e inténtalo mañana.",
    "activity": "Seguimiento de actividad diaria",
    "plus_steps": "+500 pasos",
    "log_walk": "Registrar caminata (+8 XP)",
    "goal": "Meta de pasos diaria",
    "strava": "Vincular Strava (demo)",
    "gc2": "GeoRetos 2.0",
    "adverse": "Con clima/calidad de aire adversos, sugerimos rutinas interiores para proteger los pulmones.",
    "zip": "Ingresa código postal",
    "indoor": "Rutina de cardio en casa (8 min)",
    "start_indoor": "Iniciar rutina (+12 XP)",
    "open_video": "Abrir video guiado",
    "park_challenge": "Reto: 2 vueltas caminando o trotar 10 min.",
    "directions": "Cómo llegar",
    "hub": "Centro de recursos",
    "not_med": "Enlaces educativos; no es consejo médico. Consulta a tu médico.",
    "share_hdr": "Compartir con círculo de cuidado",
    "share_cap": "Genera un enlace de solo lectura. Elige qué incluir:",
    "inc_act": "Incluir actividad",
    "inc_edu": "Incluir educación",
    "inc_diet": "Incluir alimentación",
    "suffix": "Sufijo de URL",
    "privacy": "Privacidad: tú decides qué compartir.",
    "claim": "Canjear reto semanal (+50 XP)",
    "summary": "Resumen para cuidadores (7 días):",
    "avg_steps": "- Pasos promedio: 7.350",
    "lessons_done": "- Lecciones completadas: 5",
    "meals_logged": "- Comidas saludables registradas: 9",
    "simple": "Interfaz simple (alto contraste / letra grande)",
    "lang": "Idioma",
    "live_ctx": "Contexto en vivo",
    "weather": "Clima",
    "aqi": "Calidad del aire",
  }
}
def t(key):
    lang = st.session_state.get("lang", "en")
    return T.get(lang, T["en"]).get(key, key)

# ---------------------------
# Data
# ---------------------------
CONDITIONS = [
    {"key": "hypertension", "label": {"en":"High Blood Pressure","es":"Hipertensión"}},
    {"key": "diabetes", "label": {"en":"Diabetes","es":"Diabetes"}},
    {"key": "cholesterol", "label": {"en":"High Cholesterol","es":"Colesterol alto"}},
    {"key": "asthma", "label": {"en":"Asthma","es":"Asma"}},
    {"key": "copd", "label": {"en":"COPD","es":"EPOC"}},
]

DIETARY_FLAGS = ["Low Sodium","Low Sugar","Low Carb","High Fiber","DASH Diet","Mediterranean","Plant-forward"]

RECIPES = [
    {"id":"r1","title":"Sheet-Pan Lemon Herb Salmon & Veggies","tags":["Low Carb","Mediterranean","High Fiber","cholesterol"],"video":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","minutes":25,"cals":420,"sodium_mg":280,"added_sugar_g":2,
     "blurb":"Omega-3 rich salmon with crisp broccoli and tomatoes. Heart-friendly & weeknight easy.",
     "cook":[("Preheat & Prep (2m)",120,"Preheat oven 425°F. Trim broccoli, halve tomatoes; pat salmon dry."),("Season (1m)",60,"Toss veg with olive oil, pepper, herbs. Add lemon slices; no added salt."),("Roast (7m)",420,"Roast veggies 7m. Add salmon; brush with lemon & herbs."),("Finish (3m)",180,"Roast 3–5m until salmon flakes. Plate & enjoy.")]
    },
    {"id":"r2","title":"DASH Bowl: Quinoa, Roasted Veg, Citrus Vinaigrette","tags":["DASH Diet","High Fiber","hypertension","Plant-forward"],"video":"https://www.youtube.com/watch?v=UxxajLWwzqY","minutes":30,"cals":480,"sodium_mg":190,"added_sugar_g":3,
     "blurb":"Low-sodium, potassium-rich power bowl aligned with DASH guidelines.",
     "cook":[("Quinoa (2m)",120,"Rinse quinoa; add 2:1 water; bring to boil."),("Simmer (6m)",360,"Reduce heat; simmer 12-15m total; fluff."),("Roast Veg (5m)",300,"Roast mixed veg at 425°F with olive oil & pepper."),("Vinaigrette (2m)",120,"Whisk citrus + oil + mustard; no salt add."),("Assemble (2m)",120,"Quinoa + veg + vinaigrette; top with herbs.")]
    },
    {"id":"r3","title":"Chicken & Veggie Stir-Fry (No Added Sugar Sauce)","tags":["Low Sugar","diabetes","High Fiber"],"video":"https://www.youtube.com/watch?v=3GwjfUFy6M","minutes":20,"cals":390,"sodium_mg":320,"added_sugar_g":0,
     "blurb":"Quick skillet stir-fry with balanced carbs and smart protein—diabetes-friendly.",
     "cook":[("Prep (2m)",120,"Slice chicken; chop veg."),("Sear (3m)",180,"Sear chicken; remove. Stir-fry veg 2–3m."),("Sauce (2m)",120,"Soy-lite + ginger + garlic + lemon; no sugar."),("Combine (2m)",120,"Return chicken; toss; serve with brown rice (optional).")]
    },
]

QUIZ_BANK = [
    {"id":"q1","condition":"hypertension","prompt":"Which habit most effectively lowers blood pressure over time?","options":["Adding more table salt","Regular brisk walking and a low-sodium diet","Drinking only fruit juice","Taking double meds on weekends"],"answer":1,"fact":"Aerobic activity + DASH/low-sodium pattern are first-line lifestyle strategies for BP management."},
    {"id":"q2","condition":"diabetes","prompt":"For type 2 diabetes, what helps stabilize post-meal glucose most?","options":["Skipping breakfast","Balancing protein/fiber with carbs and portion awareness","Only eating fruit","Eliminating all carbs"],"answer":1,"fact":"Protein and fiber slow glucose absorption. Portion and carb quality matter more than total avoidance."},
]

GEO_PARKS = {
  "01610": ["Elm Park Loop", "Institute Park Track", "Green Hill Park"],
  "02139": ["Charles River Path", "Dana Park Loop", "LM Fields Track"],
  "10001": ["High Line North Loop", "Chelsea Park Track", "Hudson Yards Walk"],
}

RESOURCE_LINKS = [
    ("CDC – Chronic Disease", "https://www.cdc.gov/chronic-disease/prevention/index.html"),
    ("American Heart Association – Hypertension", "https://www.heart.org/"),
    ("American Diabetes Association", "https://diabetes.org/"),
    ("NIH – COPD & Asthma", "https://www.nhlbi.nih.gov/"),
]

# ---------------------------
# Persistence helpers
# ---------------------------
def get_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def supabase_upsert_state():
    if not SUPABASE:
        return
    user_id = get_user_id()
    SUPABASE.table("cc_users").upsert({"user_id": user_id, "name": st.session_state.get("name","Alex")}).execute()
    payload = {
        "user_id": user_id,
        "xp": st.session_state.get("xp",0),
        "quiz_streak": st.session_state.get("quiz_streak",0),
        "boss_unlocked": st.session_state.get("boss_unlocked",False),
        "boss_cleared": st.session_state.get("boss_cleared",False),
        "sodium_budget_mg": st.session_state.get("sodium_budget_mg",1500),
        "sugar_budget_g": st.session_state.get("sugar_budget_g",25),
        "steps": st.session_state.get("steps",0),
        "goal": st.session_state.get("goal",8000),
        "zip": st.session_state.get("zip",""),
        "conditions": json.dumps(st.session_state.get("conditions",[])),
        "flags": json.dumps(st.session_state.get("flags",[])),
        "meals_today": json.dumps(st.session_state.get("meals_today",[])),
    }
    SUPABASE.table("cc_state").upsert(payload).execute()

def supabase_load_state():
    if not SUPABASE:
        return
    user_id = get_user_id()
    try:
        res = SUPABASE.table("cc_state").select("*").eq("user_id", user_id).execute()
        if res.data:
            row = res.data[0]
            st.session_state.xp = row.get("xp", st.session_state.xp)
            st.session_state.quiz_streak = row.get("quiz_streak", st.session_state.quiz_streak)
            st.session_state.boss_unlocked = row.get("boss_unlocked", st.session_state.boss_unlocked)
            st.session_state.boss_cleared = row.get("boss_cleared", st.session_state.boss_cleared)
            st.session_state.sodium_budget_mg = row.get("sodium_budget_mg", st.session_state.sodium_budget_mg)
            st.session_state.sugar_budget_g = row.get("sugar_budget_g", st.session_state.sugar_budget_g)
            st.session_state.steps = row.get("steps", st.session_state.steps)
            st.session_state.goal = row.get("goal", st.session_state.goal)
            st.session_state.zip = row.get("zip", st.session_state.zip)
            st.session_state.conditions = json.loads(row.get("conditions", json.dumps(st.session_state.conditions)))
            st.session_state.flags = json.loads(row.get("flags", json.dumps(st.session_state.flags)))
            st.session_state.meals_today = json.loads(row.get("meals_today", json.dumps(st.session_state.meals_today)))
    except Exception as e:
        st.sidebar.warning(f"Load failed: {e}")

# ---------------------------
# Live context (OpenWeather/Mapbox)
# ---------------------------
def geocode_zip(zip_code: str):
    if not OPENWEATHER_API_KEY:
        return None
    try:
        url = f"https://api.openweathermap.org/geo/1.0/zip?zip={zip_code},US&appid={OPENWEATHER_API_KEY}"
        r = requests.get(url, timeout=8)
        if r.ok:
            d = r.json()
            return {"lat": d.get("lat"), "lon": d.get("lon"), "name": d.get("name")}
    except Exception:
        return None

def fetch_weather_aqi(lat: float, lon: float):
    if not OPENWEATHER_API_KEY:
        return None, None
    weather = None
    aqi = None
    try:
        w = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={OPENWEATHER_API_KEY}", timeout=8)
        if w.ok: weather = w.json()
        a = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}", timeout=8)
        if a.ok: aqi = a.json()
    except Exception:
        pass
    return weather, aqi

def mapbox_static(lat, lon):
    if not MAPBOX_TOKEN:
        return None
    return f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-s+f30({lon},{lat})/{lon},{lat},14/600x300?access_token={MAPBOX_TOKEN}"

# ---------------------------
# Init state
# ---------------------------
def _init_state():
    d = st.session_state
    d.setdefault("lang", "en")
    d.setdefault("simple", False)
    d.setdefault("xp", 120)
    d.setdefault("name", "Alex")
    d.setdefault("caregiver", False)
    d.setdefault("strava", False)
    d.setdefault("steps", 4200)
    d.setdefault("goal", 8000)
    d.setdefault("conditions", ["hypertension", "diabetes"])
    d.setdefault("flags", ["DASH Diet", "Low Sugar", "High Fiber"])
    d.setdefault("zip", "01610")
    d.setdefault("quiz_idx", 0)
    d.setdefault("quiz_streak", 0)
    d.setdefault("boss_unlocked", False)
    d.setdefault("boss_cleared", False)
    d.setdefault("sodium_budget_mg", 1500)
    d.setdefault("sugar_budget_g", 25)
    d.setdefault("meals_today", [])
    d.setdefault("cook_recipe_id", None)
    d.setdefault("cook_step_idx", 0)

_init_state()
if SUPABASE:
    supabase_load_state()

# Styling for Simple UI
if st.session_state.simple:
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  { font-size: 18px !important; }
        .stButton>button { padding: 0.9rem 1.1rem; font-size: 1.05rem; }
        .stRadio>div>label { padding: 0.2rem 0; }
        .st-emotion-cache-1dp5vir { filter: contrast(1.2); }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Helpers
def level_from_xp(xp: int) -> int:
    return 1 + xp // 200
def add_xp(n: int):
    st.session_state.xp += n
    if SUPABASE:
        supabase_upsert_state()

# Care Circle query params
params = st.query_params
is_care_view = params.get("care", ["0"])[0] == "1"
share_include_steps = params.get("s", ["1"])[0] == "1"
share_include_lessons = params.get("l", ["1"])[0] == "1"
share_include_meals = params.get("m", ["0"])[0] == "1"

# Sidebar
with st.sidebar:
    st.toggle(T[st.session_state.get("lang","en")]["simple"], key="simple")
    st.selectbox(T[st.session_state.get("lang","en")]["lang"], options=list(LANGS.keys()), format_func=lambda k: LANGS[k], key="lang")
    if SUPABASE:
        st.success("Supabase: connected")
    else:
        st.info("Supabase: off (session-only)")
    if OPENWEATHER_API_KEY:
        st.success("OpenWeather: on")
    else:
        st.info("OpenWeather: demo toggles")
    if MAPBOX_TOKEN:
        st.success("Mapbox: on")
    else:
        st.info("Mapbox: off")

# Header
col1, col2, col3 = st.columns([2,2,2])
with col1:
    st.title(t("title"))
    st.caption(t("tag"))
with col2:
    if not is_care_view:
        st.toggle(t("caregiver"), key="caregiver")
        st.text_input(t("name"), key="name")
    else:
        st.info("Care Circle View — read-only summary")
with col3:
    st.metric(t("level"), level_from_xp(st.session_state.xp))
    st.metric(t("xp"), st.session_state.xp)

st.divider()

# Care Circle only
if is_care_view:
    st.header("Shared Weekly Summary")
    if share_include_steps:
        st.subheader("Activity")
        pct = min(100, round(100*st.session_state.steps/max(1, st.session_state.goal)))
        st.progress(pct/100, text=f"{st.session_state.steps:,} / {st.session_state.goal:,} steps today")
        st.caption("7-day avg steps: 7,350 (demo)")
    if share_include_lessons:
        st.subheader("Education")
        st.write("Lessons completed this week: 5 (demo)")
        st.write("Quiz streak:", st.session_state.quiz_streak)
    if share_include_meals:
        st.subheader("Diet")
        total_sodium = sum(r["sodium_mg"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0
        total_sugar  = sum(r["added_sugar_g"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0
        st.write(f"Meals logged today: {len(st.session_state.meals_today)}")
        st.write(f"Sodium used: {total_sodium} mg / {st.session_state.sodium_budget_mg} mg")
        st.write(f"Added sugar: {total_sugar} g / {st.session_state.sugar_budget_g} g")
    st.stop()

# Tabs
tab_diet, tab_edu, tab_ex, tab_resources, tab_share = st.tabs([t("diet"), t("edu"), t("ex"), t("res"), t("share")])

with tab_diet:
    st.subheader("Smart Meal Plans & Cookbooks")
    colA, colB = st.columns(2)
    with colA:
        st.caption(t("conditions"))
        labels = [c["label"][st.session_state.lang] for c in CONDITIONS]
        keys = [c["key"] for c in CONDITIONS]
        default_labels = [c["label"][st.session_state.lang] for c in CONDITIONS if c["key"] in st.session_state.conditions]
        selected = st.multiselect("Select conditions", labels, default=default_labels, label_visibility="collapsed", key="conds_select")
        st.session_state.conditions = [keys[labels.index(lbl)] for lbl in selected] if selected else []
    with colB:
        st.caption(t("prefs"))
        st.session_state.flags = st.multiselect("Choose dietary flags", DIETARY_FLAGS, default=st.session_state.flags, label_visibility="collapsed", key="flags_select")

    st.markdown(f"### {t('budgets')}")
    b1, b2, b3 = st.columns([1,1,1])
    with b1:
        st.number_input(t("sodium"), key="sodium_budget_mg", min_value=500, max_value=4000, step=50)
    with b2:
        st.number_input(t("sugar"), key="sugar_budget_g", min_value=0, max_value=100, step=1)
    with b3:
        if st.button(t("endday"), key="endday_btn"):
            total_sodium = sum(r["sodium_mg"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0
            total_sugar  = sum(r["added_sugar_g"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0
            ok_sodium = total_sodium <= st.session_state.sodium_budget_mg
            ok_sugar = total_sugar <= st.session_state.sugar_budget_g
            if ok_sodium and ok_sugar:
                add_xp(30)
                st.success(t("underbudgets"))
            else:
                st.info(t("overbudgets"))
            st.session_state.meals_today = []

    total_sodium = sum(r["sodium_mg"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0
    total_sugar  = sum(r["added_sugar_g"] for r in [x for x in RECIPES if x["id"] in st.session_state.meals_today]) if st.session_state.meals_today else 0

    pb1, pb2 = st.columns(2)
    with pb1:
        s_pct = min(1.0, total_sodium / max(1, st.session_state.sodium_budget_mg))
        st.progress(s_pct, text=f"Sodium: {total_sodium} / {st.session_state.sodium_budget_mg} mg")
    with pb2:
        su_pct = min(1.0, total_sugar / max(1, st.session_state.sugar_budget_g))
        st.progress(su_pct, text=f"Added sugar: {total_sugar} / {st.session_state.sugar_budget_g} g")

    cond_set = set(st.session_state.conditions)
    flag_set = set(st.session_state.flags)
    filtered = [r for r in RECIPES if cond_set.intersection(set(r["tags"])) or flag_set.intersection(set(r["tags"]))]
    st.write(f"**{t('recipes')}:** {len(filtered)}")

    def add_meal(r):
        st.session_state.meals_today.append(r["id"])
        add_xp(15)
        st.success(f"Added! (+15 XP) Sodium {r['sodium_mg']} mg • Sugar {r['added_sugar_g']} g")

    for idx, r in enumerate(filtered):
        with st.container(border=True):
            st.markdown(f"**{r['title']}**  \n{r['blurb']}")
            col1, col2, col3, col4 = st.columns([1,1,4,2])
            with col1: st.caption(f"{r['minutes']} min")
            with col2: st.caption(f"{r['cals']} cal")
            with col3: st.caption(" • ".join(r["tags"]))
            # NOTE: link_button does not accept key -> removed
            with col4: st.link_button(t("video"), r["video"])
            colN, colM, colK = st.columns([2,2,2])
            with colN:
                if st.button(f"{t('add_meal')} — {r['id']}", key=f"add_{r['id']}", use_container_width=True):
                    add_meal(r)
            with colM:
                if st.button(f"{t('cook_along')} — {r['id']}", key=f"cook_{r['id']}", use_container_width=True):
                    st.session_state.cook_recipe_id = r["id"]
                    st.session_state.cook_step_idx = 0
                    st.toast("Coach Cook started — follow the steps!", icon="👩‍🍳")
            with colK:
                st.button(t("save"), key=f"save_{r['id']}", use_container_width=True)

    if st.session_state.cook_recipe_id:
        rec = next((x for x in RECIPES if x["id"]==st.session_state.cook_recipe_id), None)
        st.markdown(f"### {t('coach_cook')}: **{rec['title']}**")
        steps = rec.get("cook", [])
        idx = st.session_state.cook_step_idx
        if idx < len(steps):
            title, secs, note = steps[idx]
            st.write(f"**Step {idx+1} of {len(steps)} — {title}**")
            st.info(note)
            colA, colB, colC = st.columns([1,1,2])
            if colA.button(t("step_done"), key=f"cook_step_{idx}"):
                add_xp(2)
                st.session_state.cook_step_idx += 1
                if SUPABASE:
                    supabase_upsert_state()
                st.rerun()
            if colB.button(t("cancel"), key="cook_cancel"):
                st.session_state.cook_recipe_id = None
                st.session_state.cook_step_idx = 0
            with colC:
                st.caption("Tip: Use acids, herbs, and spices to replace salt.")
        else:
            st.success(t("cook_done"))
            add_xp(10)
            st.session_state.cook_recipe_id = None
            st.session_state.cook_step_idx = 0

with tab_edu:
    st.subheader(t("quiz"))
    q = QUIZ_BANK[st.session_state.quiz_idx % len(QUIZ_BANK)]
    st.caption(f"Topic: **{q['condition'].capitalize()}**")
    st.write(q["prompt"])
    choice = st.radio("Select an answer", q["options"], index=None, key=f"quiz_choice_{st.session_state.quiz_idx}")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("submit"), key=f"quiz_submit_{st.session_state.quiz_idx}"):
            if choice is None:
                st.warning("Pick an option to submit.")
            else:
                correct = q["options"].index(choice) == q["answer"]
                if correct:
                    add_xp(20)
                    st.success("Correct! +20 XP")
                    st.session_state.quiz_streak += 1
                else:
                    add_xp(5)
                    st.info("Good try — +5 XP for learning.")
                    st.session_state.quiz_streak = 0
                if st.session_state.quiz_streak >= 5:
                    st.session_state.boss_unlocked = True
                if SUPABASE:
                    supabase_upsert_state()
    with col2:
        if st.button(t("next"), key=f"quiz_next_{st.session_state.quiz_idx}"):
            st.session_state.quiz_idx += 1
            st.rerun()
    with col3:
        st.metric(t("streak"), st.session_state.quiz_streak)

    st.divider()
    st.subheader(t("boss"))
    if st.session_state.boss_unlocked and not st.session_state.boss_cleared:
        st.info(t("boss_ready"))
        boss_q = "You're at a restaurant. Which order best balances sodium + post-meal glucose?"
        boss_opts = [
            "Soup of the day + white rice + soda",
            "Grilled salmon, steamed veg, brown rice, water with lemon",
            "Fried chicken sandwich + fries + sweet tea",
            "Pasta Alfredo + garlic bread + lemonade",
        ]
        b_choice = st.radio(boss_q, boss_opts, index=None, key="boss_radio")
        if st.button(t("boss_submit"), key="boss_submit_btn"):
            if b_choice is None:
                st.warning("Pick an option.")
            else:
                if b_choice == boss_opts[1]:
                    st.session_state.boss_cleared = True
                    add_xp(100)
                    st.success(t("boss_win"))
                else:
                    st.info(t("boss_try"))
                if SUPABASE:
                    supabase_upsert_state()
    elif st.session_state.boss_cleared:
        st.success("Boss Level complete — Badge: Restaurant Strategist ✅")
    else:
        st.caption(t("boss_unlock"))

with tab_ex:
    st.subheader(t("activity"))
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        pct = min(100, round(100*st.session_state.steps/max(1, st.session_state.goal)))
        st.progress(pct/100, text=f"{st.session_state.steps:,} / {st.session_state.goal:,} steps ({pct}%)")
    with col2:
        if st.button(t("plus_steps"), key="plus_steps_btn"):
            st.session_state.steps += 500
            if SUPABASE:
                supabase_upsert_state()
    with col3:
        if st.button(t("log_walk"), key="log_walk_btn"):
            add_xp(8)
            st.success("Walk logged! +8 XP")

    st.number_input(t("goal"), value=st.session_state.goal, step=500, key="goal")
    st.toggle(t("strava"), key="strava")

    st.divider()
    st.subheader(t("gc2"))

    ctx_col, map_col = st.columns([1,1])
    lat = lon = None
    loc_name = None
    if OPENWEATHER_API_KEY:
        st.caption(t("live_ctx"))
        geo = geocode_zip(st.session_state.zip)
        if geo and geo.get("lat"):
            lat, lon, loc_name = geo["lat"], geo["lon"], geo.get("name", "")
            weather, aqi = fetch_weather_aqi(lat, lon)
            if weather:
                w_main = weather.get("weather", [{}])[0].get("main", "")
                w_temp = weather.get("main", {}).get("temp")
                st.write(f"{t('weather')}: {w_main}, {w_temp}°F in {loc_name}")
            if aqi:
                aqi_val = aqi.get("list", [{}])[0].get("main", {}).get("aqi")
                aqi_text = {1:"Good",2:"Fair",3:"Moderate",4:"Poor",5:"Very Poor"}.get(aqi_val, "Unknown")
                st.write(f"{t('aqi')}: {aqi_text}")
            adverse = False
            if weather and weather.get("weather"):
                cond = weather["weather"][0].get("main","")
                adverse = cond in ("Rain","Snow","Thunderstorm")
            if aqi:
                aqi_val = aqi.get("list", [{}])[0].get("main", {}).get("aqi")
                adverse = adverse or (aqi_val and aqi_val >= 4)
            suggest_indoor = adverse
        else:
            suggest_indoor = False
    else:
        st.caption("Demo context toggles (weather/AQI)")
        st.toggle("Rainy/Cold Weather", key="ctx_weather_rain")
        st.toggle("High AQI (smoke/pollen)", key="ctx_aqi_high")
        suggest_indoor = st.session_state.get("ctx_weather_rain") or st.session_state.get("ctx_aqi_high")

    st.text_input(t("zip"), key="zip")
    if MAPBOX_TOKEN and lat and lon:
        url = mapbox_static(lat, lon)
        if url:
            map_col.image(url, caption=f"{loc_name or 'Location'}")

    parks = GEO_PARKS.get(st.session_state.zip, ["Community Park Loop", "City Track", "Waterfront Path"])

    if suggest_indoor:
        with st.container(border=True):
            st.markdown(f"**{t('indoor')}**  \nLow-impact sequence suitable for hypertension/COPD: marching in place, sit-to-stands, wall pushups, slow step-touch.")
            c1, c2 = st.columns(2)
            if c1.button(t("start_indoor"), key="start_indoor_btn"):
                add_xp(12)
                st.success("Indoor routine started — +12 XP!")
            # NOTE: link_button does not accept key -> removed
            c2.link_button(t("open_video"), "https://www.youtube.com/results?search_query=low+impact+indoor+cardio")
    else:
        for i, p in enumerate(parks):
            with st.container(border=True):
                st.markdown(f"**{p}**  \n{t('park_challenge')}")
                c1, c2 = st.columns(2)
                if c1.button(f"Start (+12 XP) — {p}", key=f"start_{i}"):
                    add_xp(12)
                    st.success("Challenge started — +12 XP!")
                # Make URL unique per park (no key; link_button doesn't support it)
                c2.link_button(t("directions"), f"https://www.google.com/maps/search/{urllib.parse.quote(p)}")

with tab_resources:
    st.subheader(t("hub"))
    for i, (name, href) in enumerate(RESOURCE_LINKS):
        # NOTE: link_button does not accept key -> removed
        st.link_button(name, href, use_container_width=True)
    st.caption(t("not_med"))

with tab_share:
    st.subheader(t("share_hdr"))
    st.caption(t("share_cap"))
    inc_steps = st.checkbox(t("inc_act"), value=True, key="share_steps")
    inc_lessons = st.checkbox(t("inc_edu"), value=True, key="share_lessons")
    inc_meals = st.checkbox(t("inc_diet"), value=False, key="share_meals")
    q = {"care":"1","s":"1" if inc_steps else "0","l":"1" if inc_lessons else "0","m":"1" if inc_meals else "0"}
    share_suffix = "?" + urllib.parse.urlencode(q)
    st.code(share_suffix, language="text")
    st.caption("Append this to your deployed app URL to share a read-only view.")
    if SUPABASE and st.button("Save Share Prefs", key="save_share_prefs"):
        SUPABASE.table("cc_shares").insert({
            "user_id": get_user_id(),
            "include_steps": inc_steps,
            "include_lessons": inc_lessons,
            "include_meals": inc_meals,
        }).execute()
        st.success("Share preferences saved.")

st.divider()
colL, colR = st.columns([2,2])
with colL:
    st.write(t("summary"))
    st.write(t("avg_steps"))
    st.write(t("lessons_done"))
    st.write(t("meals_logged"))
with colR:
    st.write(t("privacy"))
    if st.button(t("claim"), key="claim_weekly"):
        add_xp(50)
        st.success("Weekly challenge claimed! +50 XP")
