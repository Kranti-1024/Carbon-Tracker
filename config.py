import os
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# True when running locally with FLASK_DEBUG=1, False in production.
_dev_mode = os.environ.get("FLASK_DEBUG", "0") == "1"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # ---------------------------------------------------------------------------
    # CSRF
    # ---------------------------------------------------------------------------
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ---------------------------------------------------------------------------
    # Session & cookie security
    # ---------------------------------------------------------------------------
    # Secure=True means the cookie is only sent over HTTPS.
    # Disabled in dev mode so plain HTTP on localhost works.
    SESSION_COOKIE_SECURE = not _dev_mode
    # Prevent JavaScript from reading the session cookie (mitigates XSS impact).
    SESSION_COOKIE_HTTPONLY = True
    # Restrict cross-site cookie sending (CSRF mitigation).
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Remember-me cookie hardening
    REMEMBER_COOKIE_SECURE = not _dev_mode
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # ---------------------------------------------------------------------------
    # Request size limit — prevents memory-exhaustion via oversized form bodies
    # ---------------------------------------------------------------------------
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB

    # ---------------------------------------------------------------------------
    # Rate limiting
    # ---------------------------------------------------------------------------
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_DEFAULT = '200/hour'

    # ---------------------------------------------------------------------------
    # Database
    # ---------------------------------------------------------------------------
    # Render/Railway provide DATABASE_URL for Postgres; fall back to local SQLite.
    raw_db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------------------------------------------------------------------------
    # Carbon benchmarks
    # ---------------------------------------------------------------------------
    # Global average daily per-capita footprint benchmark (kg CO2e/day),
    # derived from ~4.7 tonnes/year global average (World Bank / Our World in Data, 2023 estimates).
    GLOBAL_AVG_DAILY_KG = 12.9
    # A "sustainable" target daily footprint consistent with 2-tonne/year pathway by 2050.
    TARGET_DAILY_KG = 5.5


# ---------------------------------------------------------------------------
# Startup security warnings
# ---------------------------------------------------------------------------
if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
    logging.warning(
        'SECRET_KEY is set to the default development value. '
        'Set a strong SECRET_KEY environment variable for production.'
    )

if Config.RATELIMIT_STORAGE_URI == 'memory://':
    logging.warning(
        'RATELIMIT_STORAGE_URI is using in-memory storage. '
        'With multiple gunicorn workers each worker tracks limits independently, '
        'making rate limiting ineffective. '
        'Set RATELIMIT_STORAGE_URI to a Redis URL (e.g. redis://...) in production.'
    )
