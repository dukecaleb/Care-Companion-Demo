# CareCompanion – Health Universe MVP (Streamlit)

This build fixes **StreamlitDuplicateElementId** by adding unique keys to all looped widgets.
It also includes:
- Daily **sodium/sugar budgets** with XP
- **Coach Cook** stepper (10‑min) with XP
- **Boss Level** after 5‑day quiz streak
- **Care Circle** read‑only sharing via query params
- **GeoChallenges 2.0** with live **weather/AQI** (OpenWeather) and **Mapbox** map preview
- **Supabase** persistence (optional)
- **Spanish mode** and **Simple UI** (accessibility)

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Health Universe Deploy
1. Push these files to a GitHub repo.
2. Create a **Streamlit** app in Health Universe; set entrypoint to `app.py`.
3. In **Secrets**, set any of (optional):
```
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "service_or_anon_key"
OPENWEATHER_API_KEY = "owm_key"
MAPBOX_TOKEN = "mapbox_pk"
```
4. Deploy.

### Supabase schema (suggested)
```sql
create table if not exists cc_users (
  user_id uuid primary key,
  name text,
  created_at timestamptz default now()
);
create table if not exists cc_state (
  user_id uuid primary key references cc_users(user_id) on delete cascade,
  xp int, quiz_streak int, boss_unlocked boolean, boss_cleared boolean,
  sodium_budget_mg int, sugar_budget_g int, steps int, goal int, zip text,
  conditions jsonb, flags jsonb, meals_today jsonb, updated_at timestamptz default now()
);
create table if not exists cc_shares (
  user_id uuid references cc_users(user_id) on delete cascade,
  created_at timestamptz default now(),
  include_steps boolean, include_lessons boolean, include_meals boolean
);
```
