"""
One-shot setup script: creates tables, seeds emission factors, and
optionally creates a demo user with realistic activity history so the
dashboard looks populated immediately (useful for judges/demos).

Usage:
    python seed.py            # tables + emission factors only
    python seed.py --demo     # also creates demo@example.com / demo1234
"""
import sys
import random
from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.activity import Activity, EmissionFactor
from app.utils.emission_data import seed_emission_factors

app = create_app()


def create_demo_user():
    existing = User.query.filter_by(email="demo@example.com").first()
    if existing:
        print("Demo user already exists — skipping creation, reusing it.")
        return existing

    user = User(name="Demo User", email="demo@example.com", daily_goal_kg=5.5)
    user.set_password("demo1234")
    db.session.add(user)
    db.session.commit()
    print("Created demo user: demo@example.com / demo1234")
    return user


def seed_demo_activities(user):
    random.seed(42)
    if Activity.query.filter_by(user_id=user.id).first():
        print("Demo user already has activities — skipping.")
        return

    factors = {f.key: f for f in EmissionFactor.query.all()}

    # A realistic-ish 21 day pattern mixing transport, food, energy, waste
    patterns = [
        ("car_petrol_km", (4, 18)),
        ("bus_km", (0, 10)),
        ("electricity_kwh", (3, 9)),
        ("meal_beef", (0, 1)),
        ("meal_chicken", (0, 2)),
        ("meal_vegetarian", (0, 2)),
        ("waste_landfill_kg", (0.5, 2)),
        ("waste_recycled_kg", (0.2, 1)),
        ("plastic_bottle", (0, 2)),
    ]

    today = date.today()
    count = 0
    for days_ago in range(21, -1, -1):
        day = today - timedelta(days=days_ago)
        for key, (low, high) in patterns:
            if random.random() < 0.7:  # not every activity every day
                factor = factors[key]
                qty = round(random.uniform(low, high), 1) if isinstance(low, float) or isinstance(high, float) else random.randint(int(low), int(high))
                if qty <= 0:
                    continue
                co2e = round(qty * factor.kg_co2e_per_unit, 3)
                db.session.add(Activity(
                    user_id=user.id, factor_key=key, quantity=qty,
                    co2e_kg=co2e, logged_date=day
                ))
                count += 1

    # One long-haul flight 10 days ago to demonstrate the flight-awareness insight
    flight_factor = factors["flight_long_km"]
    flight_day = today - timedelta(days=10)
    db.session.add(Activity(
        user_id=user.id, factor_key="flight_long_km", quantity=3500,
        co2e_kg=round(3500 * flight_factor.kg_co2e_per_unit, 3),
        logged_date=flight_day, note="Round trip flight"
    ))
    count += 1

    db.session.commit()
    print(f"Seeded {count} demo activities across the last 22 days.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        added = seed_emission_factors(db, EmissionFactor)
        print(f"Database ready. Added {added} new emission factors.")

        if "--demo" in sys.argv:
            user = create_demo_user()
            seed_demo_activities(user)
