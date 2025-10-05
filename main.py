
import streamlit as st
import time, urllib.parse
from typing import List, Dict

st.set_page_config(page_title="CareCompanion", page_icon="💚", layout="wide")

# ---------------------------
# Mock Data
# ---------------------------
CONDITIONS = [
    {"key": "hypertension", "label": "High Blood Pressure"},
    {"key": "diabetes", "label": "Diabetes"},
    {"key": "cholesterol", "label": "High Cholesterol"},
    {"key": "asthma", "label": "Asthma"},
    {"key": "copd", "label": "COPD"},
]

DIETARY_FLAGS = [
    "Low Sodium",
    "Low Sugar",
    "Low Carb",
    "High Fiber",
    "DASH Diet",
    "Mediterranean",
    "Plant-forward",
]

# Nutrition added: sodium_mg, added_sugar_g; plus optional macros for future
RECIPES = [
    {
        "id": "r1",
        "title": "Sheet-Pan Lemon Herb Salmon & Veggies",
        "tags": ["Low Carb", "Mediterranean", "High Fiber", "cholesterol"],
        "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "minutes": 25,
        "cals": 420,
        "sodium_mg": 280,
        "added_sugar_g": 2,
        "blurb": "Omega-3 rich salmon with crisp broccoli and tomatoes. Heart-friendly & weeknight easy.",
        "cook": [
            ("Preheat & Prep (2m)", 120, "Preheat oven 425°F. Trim broccoli, halve tomatoes; pat salmon dry."),
            ("Season (1m)", 60, "Toss veg with olive oil, pepper, herbs. Add lemon slices; no added salt."),
            ("Roast (7m)", 420, "Roast veggies 7m. Add salmon on top; brush with lemon & herbs."),
            ("Finish (3m)", 180, "Roast 3–5m more until salmon flakes. Plate & enjoy."),
        ],
    },
    {
        "id": "r2",
        "title": "DASH Bowl: Quinoa, Roasted Veg, Citrus Vinaigrette",
        "tags": ["DASH Diet", "High Fiber", "hypertension", "Plant-forward"],
        "video": "https://www.youtube.com/watch?v=UxxajLWwzqY",
        "minutes": 30,
        "cals": 480,
        "sodium_mg": 190,
        "added_sugar_g": 3,
        "blurb": "Low-sodium, potassium-rich power bowl aligned with DASH guidelines.",
        "cook": [
            ("Quinoa (2m)", 120, "Rinse quinoa; add 2:1 water; bring to boil."),
            ("Simmer (6m)", 360, "Reduce heat; simmer 12-15m total; fluff."),
            ("Roast Veg (5m)", 300, "Roast mixed veg at 425°F with olive oil & pepper."),
            ("Vinaigrette (2m)", 120, "Whisk citrus juice, olive oil, mustard; no salt add."),
            ("Assemble (2m)", 120, "Quinoa + veg + vinaigrette; top with herbs."),
        ],
    },
    {
        "id": "r3",
        "title": "Chicken & Veggie Stir-Fry (No Added Sugar Sauce)",
        "tags": ["Low Sugar", "diabetes", "High Fiber"],
        "video": "https://www.youtube.com/watch?v=3GwjfUFyY6M",
        "minutes": 20,
        "cals": 390,
        "sodium_mg": 320,
        "added_sugar_g": 0,
        "blurb": "Quick skillet stir-fry with balanced carbs and smart protein—diabetes-friendly.",
        "cook": [
            ("Prep (2m)", 120, "Slice chicken thin; chop veg (broccoli, peppers)."),
            ("Sear (3m)", 180, "Sear chicken; remove. Stir-fry veg 2–3m."),
            ("Sauce (2m)", 120, "Soy-lite + ginger + garlic + lemon; no sugar added."),
            ("Combine (2m)", 120, "Return chicken; toss; serve with brown rice (optional)."),
        ],
    },
    {
        "id": "r4",
        "title": "Mediterranean Bean Salad",
        "tags": ["Plant-forward", "High Fiber", "cholesterol", "hypertension"],
        "video": "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        "minutes": 15,
        "cals": 350,
        "sodium_mg": 260,
        "added_sugar_g": 1,
        "blurb": "Beans, cucumber, olives, herbs—a fiber-packed, heart-healthy staple.",
        "cook": [
            ("Rinse & Chop (2m)", 120, "Rinse beans; chop cucumbers, tomatoes, herbs."),
            ("Dress (1m)", 60, "Olive oil + lemon + pepper; avoid extra salt."),
            ("Toss (1m)", 60, "Combine; adjust with vinegar/lemon for brightness."),
        ],
    },
    {
        "id": "r5",
        "title": "Low-Sodium Turkey Chili",
        "tags": ["Low Sodium", "hypertension", "High Fiber"],
        "video": "https://www.youtube.com/watch?v=SQZyXH5ORXk",
        "minutes": 45,
        "cals": 510,
        "sodium_mg": 330,
        "added_sugar_g": 3,
        "blurb": "Comforting and bold without the salt overload. Great for BP management.",
        "cook": [
            ("Sauté (3m)", 180, "Onion/pepper/garlic in olive oil."),
            ("Brown (4m)", 240, "Ground turkey; spices (no-salt chili mix)."),
            ("Simmer (10m)", 600, "Tomatoes & beans; simmer; finish with lime."),
        ],
    },
    {
        "id": "r6",
        "title": "Power Oats with Chia & Berries",
        "tags": ["Low Sugar", "diabetes", "High Fiber", "Plant-forward"],
        "video": "https://www.youtube.com/watch?v=fLexgOxsZu0",
        "minutes": 10,
        "cals": 320,
        "sodium_mg": 120,
        "added_sugar_g": 4,
        "blurb": "Steady-energy breakfast with fiber & healthy fats to tame glucose spikes.",
        "cook": [
            ("Simmer (3m)", 180, "Oats in water/milk; pinch cinnamon (no added sugar)."),
            ("Boost (1m)", 60, "Stir chia; top berries & nuts."),
        ],
    },
]

QUIZ_BANK = [
    {
        "id": "q1",
        "condition": "hypertension",
        "prompt": "Which habit most effectively lowers blood pressure over time?",
        "options": [
            "Adding more table salt for electrolyte balance",
            "Regular brisk walking and a low-sodium diet",
            "Drinking only fruit juice instead of soda",
            "Taking double your meds on weekends",
        ],
        "answer": 1,
        "fact": "Aerobic activity + DASH/low-sodium pattern are first‑line lifestyle strategies for BP management.",
    },
    {
        "id": "q2",
        "condition": "diabetes",
        "prompt": "For type 2 diabetes, what helps stabilize post‑meal glucose most?",
        "options": [
            "Skipping breakfast",
            "Balancing protein/fiber with carbs and portion awareness",
            "Only eating fruit",
            "Eliminating all carbs permanently",
        ],
        "answer": 1,
        "fact": "Protein and fiber slow glucose absorption. Portion and carb quality matter more than total avoidance.",
    },
    {
        "id": "q3",
        "condition": "cholesterol",
        "prompt": "Which fats best support healthy LDL levels?",
        "options": [
            "Trans fats",
            "Saturated fats",
            "Unsaturated fats from nuts, seeds, olive oil, and fish",
            "No fats at all",
        ],
        "answer": 2,
        "fact": "Unsaturated fats can improve lipid profile; trans fats worsen it; overall pattern still matters.",
    },
    {
        "id": "q4",
        "condition": "copd",
        "prompt": "Helpful daily habit for COPD symptom control?",
        "options": [
            "Avoid prescribed inhalers on good days",
            "Pursed‑lip breathing and gentle walking as tolerated",
            "No activity to save energy",
            "Only exercise at high intensity",
        ],
        "answer": 1,
        "fact": "Breathing techniques + light activity improve ventilation and endurance.",
    },
    {
        "id": "q5",
        "condition": "asthma",
        "prompt": "Which action supports fewer asthma flares?",
        "options": [
            "Stop all controller meds after a few good days",
            "Know triggers, use spacers, follow action plan",
            "Only use quick‑relief inhaler before bed",
            "High pollen exposure for tolerance",
        ],
        "answer": 1,
        "fact": "Trigger management and consistent controller use reduce exacerbations.",
    },
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
# State
# ---------------------------
def _init_state():
    d = st.session_state
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
    # Diet budgets + log
    d.setdefault("sodium_budget_mg", 1500)
    d.setdefault("sugar_budget_g", 25)
    d.setdefault("meals_today", [])  # list of recipe ids
    # Coach Cook
    d.setdefault("cook_recipe_id", None)
    d.setdefault("cook_step_idx", 0)
    # Geo context (simulated)
    d.setdefault("ctx_weather_rain", False)
    d.setdefault("ctx_aqi_high", False)

_init_state()

def level_from_xp(xp: int) -> int:
    return 1 + xp // 200

def add_xp(n: int):
    st.session_state.xp += n

def get_recipe(rid: str):
    for r in RECIPES:
        if r["id"] == rid:
            return r
    return None

# ---------------------------
# Care Circle view parsing
# ---------------------------
params = st.query_params
is_care_view = params.get("care", ["0"])[0] == "1"
share_include_steps = params.get("s", ["1"])[0] == "1"
share_include_lessons = params.get("l", ["1"])[0] == "1"
share_include_meals = params.get("m", ["0"])[0] == "1"

# ---------------------------
# Header
# ---------------------------
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    st.title("CareCompanion 💚")
    st.caption("Prevent • Manage • Thrive")

with col2:
    if not is_care_view:
        st.toggle("Caregiver Mode", key="caregiver")
        st.text_input("Your name", key="name")
    else:
        st.info("Care Circle View — read‑only summary")

with col3:
    st.metric("Level", level_from_xp(st.session_state.xp))
    st.metric("XP", st.session_state.xp)

st.divider()

# ---------------------------
# Care Circle only view
# ---------------------------
if is_care_view:
    st.header("Shared Weekly Summary")
    if share_include_steps:
        st.subheader("Activity")
        pct = min(100, round(100*st.session_state.steps/max(1, st.session_state.goal)))
        st.progress(pct/100, text=f"{st.session_state.steps:,} / {st.session_state.goal:,} steps today")
        st.caption("7‑day avg steps: 7,350 (demo)")
    if share_include_lessons:
        st.subheader("Education")
        st.write("Lessons completed this week: 5 (demo)")
        st.write("Quiz streak:", st.session_state.quiz_streak)
    if share_include_meals:
        st.subheader("Diet")
        total_sodium = sum(get_recipe(r)["sodium_mg"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0
        total_sugar = sum(get_recipe(r)["added_sugar_g"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0
        st.write(f"Meals logged today: {len(st.session_state.meals_today)}")
        st.write(f"Sodium used: {total_sodium} mg / {st.session_state.sodium_budget_mg} mg")
        st.write(f"Added sugar: {total_sugar} g / {st.session_state.sugar_budget_g} g")
    st.stop()

# ---------------------------
# Tabs
# ---------------------------
tab_diet, tab_edu, tab_ex, tab_resources, tab_share = st.tabs(["🥗 Diet", "📘 Education", "🏃 Exercise", "🔗 Resources", "👪 Share"])

with tab_diet:
    st.subheader("Smart Meal Plans & Cookbooks")
    colA, colB = st.columns(2)
    with colA:
        st.caption("My Conditions")
        cond_keys = [c["key"] for c in CONDITIONS]
        labels = [c["label"] for c in CONDITIONS]
        selected = st.multiselect("Select conditions", labels, default=[c["label"] for c in CONDITIONS if c["key"] in st.session_state.conditions], label_visibility="collapsed")
        st.session_state.conditions = [cond_keys[labels.index(lbl)] for lbl in selected] if selected else []

    with colB:
        st.caption("Dietary Preferences")
        st.session_state.flags = st.multiselect("Choose dietary flags", DIETARY_FLAGS, default=st.session_state.flags, label_visibility="collapsed")

    # Budgets
    st.markdown("### Daily Budgets")
    b1, b2, b3 = st.columns([1,1,1])
    with b1:
        st.number_input("Sodium (mg)", key="sodium_budget_mg", min_value=500, max_value=4000, step=50)
    with b2:
        st.number_input("Added Sugar (g)", key="sugar_budget_g", min_value=0, max_value=100, step=1)
    with b3:
        if st.button("End Day & Check Budget"):
            total_sodium = sum(get_recipe(r)["sodium_mg"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0
            total_sugar = sum(get_recipe(r)["added_sugar_g"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0
            ok_sodium = total_sodium <= st.session_state.sodium_budget_mg
            ok_sugar = total_sugar <= st.session_state.sugar_budget_g
            if ok_sodium and ok_sugar:
                add_xp(30)
                st.success("Great job staying under budget! +30 XP 🎉")
            else:
                st.info("Budgets exceeded — tomorrow is a fresh start!")
            st.session_state.meals_today = []

    total_sodium = sum(get_recipe(r)["sodium_mg"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0
    total_sugar = sum(get_recipe(r)["added_sugar_g"] for r in st.session_state.meals_today) if st.session_state.meals_today else 0

    pb1, pb2 = st.columns(2)
    with pb1:
        s_pct = min(1.0, total_sodium / max(1, st.session_state.sodium_budget_mg))
        st.progress(s_pct, text=f"Sodium: {total_sodium} / {st.session_state.sodium_budget_mg} mg")
    with pb2:
        su_pct = min(1.0, total_sugar / max(1, st.session_state.sugar_budget_g))
        st.progress(su_pct, text=f"Added sugar: {total_sugar} / {st.session_state.sugar_budget_g} g")

    # Filter recipes
    cond_set = set(st.session_state.conditions)
    flag_set = set(st.session_state.flags)

    filtered = [r for r in RECIPES if cond_set.intersection(set(r["tags"])) or flag_set.intersection(set(r["tags"]))]
    st.write(f"**Recommended recipes:** {len(filtered)}")

    for r in filtered:
        with st.container(border=True):
            st.markdown(f"**{r['title']}**  \n{r['blurb']}")
            col1, col2, col3, col4 = st.columns([1,1,4,2])
            with col1: st.caption(f"{r['minutes']} min")
            with col2: st.caption(f"{r['cals']} cal")
            with col3: st.caption(" • ".join(r["tags"]))
            with col4:
                st.link_button("▶️ Video", r["video"])
            colN, colM, colK = st.columns([2,2,2])
            with colN:
                if st.button(f"Add to Meal Plan (+15 XP) — {r['id']}", use_container_width=True):
                    st.session_state.meals_today.append(r["id"])
                    add_xp(15)
                    st.success(f"Added! (+15 XP) Sodium {r['sodium_mg']} mg • Sugar {r['added_sugar_g']} g")
            with colM:
                if st.button(f"Cook‑Along (10‑min) — {r['id']}", use_container_width=True):
                    st.session_state.cook_recipe_id = r["id"]
                    st.session_state.cook_step_idx = 0
                    st.toast("Coach Cook started — follow the steps!", icon="👩‍🍳")
            with colK:
                st.button("Save", use_container_width=True)

    # Coach Cook Stepper
    if st.session_state.cook_recipe_id:
        rec = get_recipe(st.session_state.cook_recipe_id)
        st.markdown(f"### 👩‍🍳 Coach Cook: **{rec['title']}**")
        steps = rec.get("cook", [])
        idx = st.session_state.cook_step_idx
        if idx < len(steps):
            title, secs, note = steps[idx]
            st.write(f"**Step {idx+1} of {len(steps)} — {title}**")
            st.info(note)
            colA, colB, colC = st.columns([1,1,2])
            if colA.button("Step Done (+2 XP)"):
                add_xp(2)
                st.session_state.cook_step_idx += 1
                st.rerun()
            if colB.button("Cancel Cook‑Along"):
                st.session_state.cook_recipe_id = None
                st.session_state.cook_step_idx = 0
            with colC:
                st.caption("Tip: Keep sodium low—use acids, herbs, and spices for flavor.")
        else:
            st.success("Cook‑along complete! +10 XP")
            add_xp(10)
            st.session_state.cook_recipe_id = None
            st.session_state.cook_step_idx = 0

with tab_edu:
    st.subheader("Daily Lesson & Quiz")
    q = QUIZ_BANK[st.session_state.quiz_idx % len(QUIZ_BANK)]
    st.caption(f"Topic: **{q['condition'].capitalize()}**")
    st.write(q["prompt"])
    choice = st.radio("Select an answer", q["options"], index=None)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Submit"):
            if choice is None:
                st.warning("Pick an option to submit.")
            else:
                correct = q["options"].index(choice) == q["answer"]
                if correct:
                    add_xp(20)
                    st.success("Correct! +20 XP")
                else:
                    add_xp(5)
                    st.info("Good try — +5 XP for learning.")
                st.info(q["fact"])
                # Streak logic — counts submissions on this demo
                st.session_state.quiz_streak += 1 if correct else 0
                if st.session_state.quiz_streak >= 5:
                    st.session_state.boss_unlocked = True
    with col2:
        if st.button("Next Question"):
            st.session_state.quiz_idx += 1
            st.rerun()
    with col3:
        st.metric("Quiz Streak", st.session_state.quiz_streak)

    # Boss Level
    st.divider()
    st.subheader("Boss Level")
    if st.session_state.boss_unlocked and not st.session_state.boss_cleared:
        st.info("Unlocked! Scenario: **Dining Out with Diabetes & Hypertension**")
        boss_q = "You’re at a restaurant. Which order best balances sodium + post‑meal glucose?"
        boss_opts = [
            "Soup of the day + white rice + soda",
            "Grilled salmon, steamed veg, brown rice, water with lemon",
            "Fried chicken sandwich + fries + sweet tea",
            "Pasta Alfredo + garlic bread + lemonade",
        ]
        b_choice = st.radio(boss_q, boss_opts, index=None, key="boss_radio")
        if st.button("Submit Boss Level"):
            if b_choice is None:
                st.warning("Pick an option.")
            else:
                if b_choice == boss_opts[1]:
                    st.session_state.boss_cleared = True
                    add_xp(100)
                    st.success("Boss defeated! +100 XP — Badge unlocked: **Restaurant Strategist**")
                else:
                    st.info("Close! Review the Education tab and try again tomorrow.")
    elif st.session_state.boss_cleared:
        st.success("Boss Level complete — Badge: Restaurant Strategist ✅")
    else:
        st.caption("Get a 5‑day quiz streak to unlock the Boss Level.")

with tab_ex:
    st.subheader("Daily Activity Tracker")
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        pct = min(100, round(100*st.session_state.steps/max(1, st.session_state.goal)))
        st.progress(pct/100, text=f"{st.session_state.steps:,} / {st.session_state.goal:,} steps ({pct}%)")
    with col2:
        if st.button("+500 steps"):
            st.session_state.steps += 500
    with col3:
        if st.button("Log Walk (+8 XP)"):
            add_xp(8)
            st.success("Walk logged! +8 XP")

    st.number_input("Daily Step Goal", value=st.session_state.goal, step=500, key="goal")
    st.toggle("Link Strava (mock)", key="strava")
    if st.session_state.strava:
        st.caption("Strava linked (demo). Wire OAuth later with FastAPI + Secrets.")

    st.divider()
    st.subheader("GeoChallenges 2.0")
    # Context-aware toggles (simulate live APIs)
    gc_a, gc_b, gc_c = st.columns([1,1,2])
    with gc_a:
        st.toggle("Rainy/Cold Weather", key="ctx_weather_rain")
    with gc_b:
        st.toggle("High AQI (smoke/pollen)", key="ctx_aqi_high")
    with gc_c:
        st.caption("When weather/AQI is adverse, we suggest indoor routines to protect lungs & keep streaks alive.")

    st.text_input("Enter ZIP code", key="zip")
    parks = GEO_PARKS.get(st.session_state.zip, ["Community Park Loop", "City Track", "Waterfront Path"])

    if st.session_state.ctx_weather_rain or st.session_state.ctx_aqi_high:
        with st.container(border=True):
            st.markdown("**Indoor Cardio Routine (8‑min)**  \nLow‑impact sequence suitable for hypertension/COPD: marching in place, sit‑to‑stands, wall pushups, slow step‑touch.")
            c1, c2 = st.columns(2)
            if c1.button("Start Indoor Routine (+12 XP)"):
                add_xp(12)
                st.success("Indoor routine started — +12 XP!")
            c2.link_button("Open Guided Video", "https://www.youtube.com/results?search_query=low+impact+indoor+cardio", help="Example search; replace with your own video.")
    else:
        for p in parks:
            with st.container(border=True):
                st.markdown(f"**{p}**  \nChallenge: Walk 2 laps or jog 10 min.")
                c1, c2 = st.columns(2)
                if c1.button(f"Start (+12 XP) — {p}"):
                    add_xp(12)
                    st.success("Challenge started — +12 XP!")
                c2.link_button("Directions", "https://maps.google.com", help="Opens Maps")

with tab_resources:
    st.subheader("Resource Hub")
    for name, href in RESOURCE_LINKS:
        st.link_button(name, href, use_container_width=True)
    st.caption("Educational links; not medical advice. Talk to your clinician for personal care.")

with tab_share:
    st.subheader("Care Circle Sharing")
    st.caption("Generate a read‑only URL for caregivers. Choose what to include:")
    inc_steps = st.checkbox("Include Activity", value=True)
    inc_lessons = st.checkbox("Include Education", value=True)
    inc_meals = st.checkbox("Include Diet", value=False)
    q = {"care": "1", "s": "1" if inc_steps else "0", "l": "1" if inc_lessons else "0", "m": "1" if inc_meals else "0"}
    share_suffix = "?" + urllib.parse.urlencode(q)
    st.code(share_suffix, language="text")
    st.caption("Append this to your app URL after deployment to share a read‑only view (e.g., https://yourapp.healthuniverse.com/APP" + share_suffix + ")")

st.divider()
colL, colR = st.columns([2,2])
with colL:
    st.write("**Caregiver Summary (7 days):**")
    st.write("- Avg steps: 7,350")
    st.write("- Lessons completed: 5")
    st.write("- Healthy meals logged: 9")
with colR:
    st.write("**Privacy**: You control caregiver access & data sharing settings.")
    if st.button("Claim Weekly Challenge (+50 XP)"):
        add_xp(50)
        st.success("Weekly challenge claimed! +50 XP")
