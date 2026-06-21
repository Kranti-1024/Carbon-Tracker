import os
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_DEFAULT = '200/hour'

    # Render/Railway provide DATABASE_URL for Postgres; fall back to local SQLite.
    raw_db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # Global average daily per-capita footprint benchmark (kg CO2e/day),
    # derived from ~4.7 tonnes/year global average (World Bank / Our World in Data, 2023 estimates).
    GLOBAL_AVG_DAILY_KG = 12.9
    # A "sustainable" target daily footprint consistent with 2-tonne/year pathway by 2050.
    TARGET_DAILY_KG = 5.5

# Warn if running with the default development secret key
if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
    logging.warning(
        'SECRET_KEY is set to the default development value. '
        'Set a strong SECRET_KEY environment variable for production.'
    )
