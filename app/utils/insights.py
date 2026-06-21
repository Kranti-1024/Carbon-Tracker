"""
Rule-based insight engine.
Looks at a user's recent activity breakdown by category and surfaces
concrete, ranked suggestions with an estimated kg CO2e/week saving.
No ML needed here — transparent rules are more trustworthy for a tool
that's trying to change someone's daily behavior, and don't depend on
an external API being up during a demo.
"""

INSIGHT_RULES = [
    {
        "id": "swap_car_to_bus",
        "category": "transport",
        "condition": lambda stats: (
            stats["transport_kg"] - stats["flight_kg"] > stats["total_kg"] * 0.35
            and stats["car_km_week"] > 20
        ),
        "title": "Swap two car trips a week for the bus",
        "detail": "Your regular driving is the single biggest source of emissions right now. Replacing two average car trips a week with bus or rail cuts a meaningful chunk without changing your routine much.",
        "est_weekly_saving_kg": 6.5,
    },
    {
        "id": "reduce_red_meat",
        "category": "food",
        "condition": lambda stats: stats["food_kg"] > stats["total_kg"] * 0.30 and stats["beef_meals_week"] >= 3,
        "title": "Try 2 plant-based dinners this week",
        "detail": "Beef-heavy meals are roughly 8x more carbon-intensive than vegetarian ones. Swapping two dinners a week for a vegetarian option is one of the highest-leverage changes you can make.",
        "est_weekly_saving_kg": 11.5,
    },
    {
        "id": "flight_offset_awareness",
        "category": "transport",
        "condition": lambda stats: stats["flight_kg"] > 50,
        "title": "Flights are dominating your footprint this period",
        "detail": "A single long flight can outweigh weeks of everyday choices. Where possible, consolidate trips or consider rail for shorter routes — and know that no other change will move the needle as much as flying less.",
        "est_weekly_saving_kg": 0,  # informational, not a recurring weekly action
    },
    {
        "id": "standby_power",
        "category": "energy",
        "condition": lambda stats: stats["energy_kg"] > stats["total_kg"] * 0.30,
        "title": "Audit always-on appliances",
        "detail": "Energy use is a large share of your footprint. Unplugging devices on standby and switching to LED lighting typically shaves 5-10% off home electricity use.",
        "est_weekly_saving_kg": 2.8,
    },
    {
        "id": "recycle_more",
        "category": "waste",
        "condition": lambda stats: stats["landfill_kg"] > stats["recycled_kg"] * 2 and stats["landfill_kg"] > 1,
        "title": "Sort more waste for recycling",
        "detail": "Recycled waste produces roughly 80% less CO2e than the same material sent to landfill. Most of your logged waste is going to landfill — a quick sorting habit pays off fast.",
        "est_weekly_saving_kg": 1.4,
    },
    {
        "id": "bike_short_trips",
        "category": "transport",
        "condition": lambda stats: stats["car_km_week"] > 20 and stats["car_km_week"] < 80,
        "title": "Walk or bike short car trips under 3km",
        "detail": "A meaningful share of car trips are short enough to walk or bike. These add up fast in city driving and are the easiest to convert first.",
        "est_weekly_saving_kg": 3.2,
    },
    {
        "id": "plastic_reduction",
        "category": "waste",
        "condition": lambda stats: stats["plastic_bottles_week"] >= 5,
        "title": "Switch to a refillable bottle",
        "detail": "You're logging several single-use plastic bottles a week. A refillable bottle eliminates this entirely and is one of the simplest swaps on this list.",
        "est_weekly_saving_kg": 0.4,
    },
    {
        "id": "doing_great",
        "category": "general",
        "condition": lambda stats: stats["total_kg"] <= stats["target_daily_kg"] * 7,
        "title": "You're tracking below the sustainable target",
        "detail": "Your footprint this week is at or below the ~2-tonne/year pathway target. Keep logging consistently — small drifts are easiest to catch early.",
        "est_weekly_saving_kg": 0,
    },
]


def generate_insights(stats, max_results=4):
    """
    stats: dict with keys like total_kg, transport_kg, food_kg, energy_kg,
    waste_kg, beef_meals_week, car_km_week, flight_kg, landfill_kg,
    recycled_kg, plastic_bottles_week, target_daily_kg
    """
    matched = [rule for rule in INSIGHT_RULES if rule["condition"](stats)]
    # Rank by estimated impact, descending; informational ones (0 saving) sort last
    matched.sort(key=lambda r: r["est_weekly_saving_kg"], reverse=True)
    return matched[:max_results]
