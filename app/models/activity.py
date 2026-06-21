from datetime import date, datetime, timezone
from app import db


class EmissionFactor(db.Model):
    """
    Lookup table mapping a specific activity type to its emission factor.
    kg_co2e_per_unit is the multiplier applied to the quantity the user logs.
    """
    __tablename__ = "emission_factors"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), nullable=False)       # transport, energy, food, waste
    key = db.Column(db.String(60), unique=True, nullable=False)  # e.g. "car_petrol_km"
    label = db.Column(db.String(120), nullable=False)         # "Car (petrol) - km driven"
    unit = db.Column(db.String(30), nullable=False)           # km, kWh, kg, meal, item
    kg_co2e_per_unit = db.Column(db.Float, nullable=False)
    source_note = db.Column(db.String(255))

    def __repr__(self):
        return f"<EmissionFactor {self.key}>"


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    factor_key = db.Column(db.String(60), db.ForeignKey("emission_factors.key"), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    co2e_kg = db.Column(db.Float, nullable=False)  # computed at log-time, stored for fast querying
    logged_date = db.Column(db.Date, default=date.today, index=True)
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    factor = db.relationship("EmissionFactor")

    def __repr__(self):
        return f"<Activity {self.factor_key} {self.co2e_kg}kg on {self.logged_date}>"
