import os
from dotenv import load_dotenv

# Load .env for local development. In production (Railway/Render) env vars are
# injected directly by the platform so this is a no-op if .env doesn't exist.
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.activity import Activity, EmissionFactor
from app.utils.emission_data import seed_emission_factors

app = create_app()


@app.cli.command("seed-factors")
def seed_factors_command():
    """Seed the emission factors lookup table. Safe to run multiple times."""
    with app.app_context():
        added = seed_emission_factors(db, EmissionFactor)
        print(f"Added {added} new emission factors.")


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Activity": Activity, "EmissionFactor": EmissionFactor}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
