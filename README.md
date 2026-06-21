# Carbon Ledger

A web app that turns your daily transport, energy, food, and waste habits into
one clear carbon footprint number — and tells you exactly which change would
reduce it the most.

Built for the **10xthink — Carbon Footprint Awareness Platform** challenge.

## The problem

Most people have never seen their own carbon footprint as a number, let alone
know which single habit is driving it. Carbon Ledger makes the invisible
visible: log real activities, watch a daily "ledger" fill up against a
sustainable target, and get ranked, concrete suggestions — not vague advice.

## How it works

1. **Log** — record a transport trip, a meal, electricity use, or waste, picked
   from a categorized list of common activities.
2. **See** — every entry is converted to kg CO2e using published emission
   factors and shown on a 14-day ledger strip and a 30-day category breakdown.
3. **Act** — a rule-based insight engine looks at your last 7 days and surfaces
   the highest-impact, most specific change available to you, with an
   estimated kg CO2e/week saving.

## Tech stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
- **Database:** SQLite locally, PostgreSQL in production
- **Frontend:** Server-rendered Jinja2 templates, vanilla CSS/JS (no build step)
- **Deployment:** Render / Railway, via Gunicorn

## Emission factor sources

Factors are compiled from public, citable sources and rounded for clarity —
this is an awareness tool, not a regulatory carbon accounting system:

- UK DEFRA / BEIS greenhouse gas conversion factors (transport, energy)
- US EPA emission factors (waste)
- Our World in Data (food lifecycle emissions)
- IEA (global average grid electricity intensity)

See `app/utils/emission_data.py` for the full table and per-row source notes.

Benchmark figures used on the dashboard:
- Global average daily footprint: **12.9 kg CO2e/day** (~4.7 t/year)
- Sustainable 2050-pathway target: **5.5 kg CO2e/day** (~2 t/year)

## Project structure

```
carbon-tracker/
├── app/
│   ├── models/          # User, Activity, EmissionFactor
│   ├── routes/          # auth, main, activities, dashboard blueprints
│   ├── utils/           # emission_data, insights engine, stats aggregation
│   ├── templates/       # Jinja2 templates
│   └── static/css/      # design system stylesheet
├── config.py
├── run.py               # app entry point + CLI commands
├── seed.py              # DB init + emission factor seed + optional demo data
├── requirements.txt
├── Procfile             # for Render/Railway
└── runtime.txt
```

## Local setup

```bash
git clone <your-repo-url>
cd carbon-tracker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY if you want

python seed.py --demo           # creates tables + emission factors + a demo user
python run.py
```

Visit `http://localhost:5000`. Log in with the demo account:
- **Email:** `demo@example.com`
- **Password:** `demo1234`

Or sign up fresh and log your own activities from the "Log activity" page.

## Deploying (Render)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn run:app`
5. Add a PostgreSQL instance (Render → New → PostgreSQL) and copy its
   **Internal Database URL** into the web service's `DATABASE_URL` env var.
6. Set a `SECRET_KEY` env var to a long random string.
7. After first deploy, run `python seed.py` once from the Render shell to
   create tables and seed emission factors (add `--demo` for demo data).

## What's intentionally rule-based, not ML

The insight engine (`app/utils/insights.py`) uses transparent, auditable rules
rather than a black-box model or an external LLM call. For a tool whose whole
point is getting someone to trust a recommendation enough to change a habit,
explainability matters more than sophistication — and it means the demo never
depends on a third-party API being up.

## Possible next steps

- Household/multi-user comparison and leaderboards
- CSV export of activity history
- Push notifications / weekly email digest of the top insight
- Per-activity-type historical trend charts
