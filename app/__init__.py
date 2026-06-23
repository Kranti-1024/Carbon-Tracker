from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

# Content-Security-Policy:
# - default-src 'self'          → only load resources from own origin by default
# - style-src allows Google Fonts stylesheet + inline styles (needed by Jinja flash)
# - font-src allows Google Fonts binary files
# - script-src 'self' only      → no inline scripts or external CDN JS
# - img-src 'self' data:        → allow data-URIs for embedded chart images
CSP = {
    'default-src': "'self'",
    'style-src': [
        "'self'",
        'https://fonts.googleapis.com',
        # Allow Talisman nonce-based inline styles if needed in future
    ],
    'font-src': [
        "'self'",
        'https://fonts.gstatic.com',
    ],
    'script-src': "'self'",
    'img-src': ["'self'", 'data:'],
    'object-src': "'none'",
    'base-uri': "'self'",
    'frame-ancestors': "'none'",
}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Security headers — force HTTPS only outside debug/test mode
    talisman.init_app(
        app,
        content_security_policy=CSP,
        content_security_policy_nonce_in=['script-src'],
        force_https=not app.debug,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
        },
    )

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.models.user import User
    from app.models.activity import Activity, EmissionFactor

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.activities import activities_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_globals():
        from datetime import datetime, timezone
        return {"current_year": datetime.now(timezone.utc).year}

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Serve static files in production via WhiteNoise
    from whitenoise import WhiteNoise
    import os
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_path, prefix='static/')

    return app
