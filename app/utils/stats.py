from datetime import date, timedelta
from sqlalchemy import func
from app import db
from app.models.activity import Activity, EmissionFactor


def get_period_stats(user, days=7):
    """Aggregate a user's activities over the last `days` days into the
    stats dict consumed by the dashboard and insight engine."""
    start = date.today() - timedelta(days=days - 1)

    rows = (
        db.session.query(Activity, EmissionFactor)
        .join(EmissionFactor, Activity.factor_key == EmissionFactor.key)
        .filter(Activity.user_id == user.id, Activity.logged_date >= start)
        .all()
    )

    stats = {
        "total_kg": 0.0,
        "transport_kg": 0.0,
        "energy_kg": 0.0,
        "food_kg": 0.0,
        "waste_kg": 0.0,
        "beef_meals_week": 0,
        "car_km_week": 0.0,
        "flight_kg": 0.0,
        "landfill_kg": 0.0,
        "recycled_kg": 0.0,
        "plastic_bottles_week": 0,
        "target_daily_kg": user.daily_goal_kg or 5.5,
        "by_day": {},  # date -> kg
    }

    for activity, factor in rows:
        stats["total_kg"] += activity.co2e_kg
        cat_key = f"{factor.category}_kg"
        if cat_key in stats:
            stats[cat_key] += activity.co2e_kg

        day_key = activity.logged_date.isoformat()
        stats["by_day"][day_key] = stats["by_day"].get(day_key, 0) + activity.co2e_kg

        if factor.key == "meal_beef":
            stats["beef_meals_week"] += activity.quantity
        if factor.key in ("car_petrol_km", "car_diesel_km", "car_ev_km"):
            stats["car_km_week"] += activity.quantity
        if factor.key in ("flight_short_km", "flight_long_km"):
            stats["flight_kg"] += activity.co2e_kg
        if factor.key == "waste_landfill_kg":
            stats["landfill_kg"] += activity.co2e_kg
        if factor.key == "waste_recycled_kg":
            stats["recycled_kg"] += activity.co2e_kg
        if factor.key == "plastic_bottle":
            stats["plastic_bottles_week"] += activity.quantity

    return stats


def get_category_breakdown(user, days=30):
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.session.query(EmissionFactor.category, func.sum(Activity.co2e_kg))
        .join(EmissionFactor, Activity.factor_key == EmissionFactor.key)
        .filter(Activity.user_id == user.id, Activity.logged_date >= start)
        .group_by(EmissionFactor.category)
        .all()
    )
    return {category: round(total, 2) for category, total in rows}


def get_daily_series(user, days=14):
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.session.query(Activity.logged_date, func.sum(Activity.co2e_kg))
        .filter(Activity.user_id == user.id, Activity.logged_date >= start)
        .group_by(Activity.logged_date)
        .order_by(Activity.logged_date)
        .all()
    )
    totals_by_date = {d.isoformat(): round(v, 2) for d, v in rows}

    series = []
    for i in range(days):
        d = start + timedelta(days=i)
        series.append({"date": d.isoformat(), "kg": totals_by_date.get(d.isoformat(), 0)})
    return series
