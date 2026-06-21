"""
Emission factors used to convert logged activity quantities into kg CO2e.
Values are reasonable approximations compiled from widely-cited public sources:
EPA, DEFRA/BEIS UK conversion factors, and Our World in Data — rounded for
clarity and intended for personal awareness tracking, not regulatory accounting.
"""

EMISSION_FACTORS = [
    # category, key, label, unit, kg_co2e_per_unit, source_note
    ("transport", "car_petrol_km", "Car (petrol) - per km", "km", 0.192, "DEFRA avg petrol car"),
    ("transport", "car_diesel_km", "Car (diesel) - per km", "km", 0.171, "DEFRA avg diesel car"),
    ("transport", "car_ev_km", "Electric car - per km", "km", 0.053, "DEFRA EV, grid-avg electricity"),
    ("transport", "bus_km", "Bus - per km", "km", 0.105, "DEFRA local bus avg"),
    ("transport", "train_km", "Train - per km", "km", 0.041, "DEFRA national rail avg"),
    ("transport", "motorbike_km", "Motorbike - per km", "km", 0.103, "DEFRA avg motorcycle"),
    ("transport", "flight_short_km", "Flight (short-haul) - per km", "km", 0.151, "DEFRA short-haul, incl. radiative forcing"),
    ("transport", "flight_long_km", "Flight (long-haul) - per km", "km", 0.110, "DEFRA long-haul, incl. radiative forcing"),
    ("transport", "bicycle_walk_km", "Bicycle / Walking - per km", "km", 0.0, "Zero direct emissions"),

    ("energy", "electricity_kwh", "Electricity used - per kWh", "kWh", 0.475, "Global grid avg, IEA"),
    ("energy", "lpg_kg", "LPG cooking gas - per kg", "kg", 2.983, "DEFRA LPG combustion"),
    ("energy", "natural_gas_kwh", "Natural gas (heating) - per kWh", "kWh", 0.182, "DEFRA natural gas"),

    ("food", "meal_beef", "Meal with beef", "meal", 6.61, "Our World in Data, beef-heavy meal"),
    ("food", "meal_chicken", "Meal with chicken/poultry", "meal", 1.57, "Our World in Data, poultry meal"),
    ("food", "meal_vegetarian", "Vegetarian meal", "meal", 0.84, "Our World in Data, veg meal"),
    ("food", "meal_vegan", "Vegan meal", "meal", 0.57, "Our World in Data, vegan meal"),
    ("food", "dairy_serving", "Dairy serving (milk/cheese)", "serving", 0.6, "Our World in Data dairy avg"),
    ("food", "food_delivery", "Food delivery order (packaging + transport)", "order", 1.1, "Estimated packaging + last-mile delivery"),

    ("waste", "waste_landfill_kg", "General waste to landfill - per kg", "kg", 0.467, "EPA landfill waste factor"),
    ("waste", "waste_recycled_kg", "Recycled waste - per kg", "kg", 0.089, "EPA recycling factor, avg material"),
    ("waste", "plastic_bottle", "Single-use plastic bottle", "item", 0.082, "Lifecycle estimate, 500ml PET bottle"),
]


def seed_emission_factors(db, EmissionFactor):
    existing_keys = {f.key for f in EmissionFactor.query.all()}
    added = 0
    for category, key, label, unit, factor, source in EMISSION_FACTORS:
        if key in existing_keys:
            continue
        db.session.add(EmissionFactor(
            category=category, key=key, label=label, unit=unit,
            kg_co2e_per_unit=factor, source_note=source
        ))
        added += 1
    db.session.commit()
    return added
