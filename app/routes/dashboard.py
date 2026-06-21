from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.utils.stats import get_period_stats, get_category_breakdown, get_daily_series
from app.utils.insights import generate_insights

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    stats = get_period_stats(current_user, days=7)
    breakdown = get_category_breakdown(current_user, days=30)
    daily_series = get_daily_series(current_user, days=14)
    insights = generate_insights(stats)

    week_total = round(stats["total_kg"], 2)
    week_avg_daily = round(stats["total_kg"] / 7, 2)
    global_avg_daily = current_app.config["GLOBAL_AVG_DAILY_KG"]
    target_daily = stats["target_daily_kg"]

    vs_global_pct = None
    if week_total == 0:
        week_avg_daily = 0.0
        vs_global_pct = None
    elif global_avg_daily:
        vs_global_pct = round(((week_avg_daily - global_avg_daily) / global_avg_daily) * 100, 1)

    return render_template(
        "dashboard/index.html",
        stats=stats,
        breakdown=breakdown,
        daily_series=daily_series,
        insights=insights,
        week_total=week_total,
        week_avg_daily=week_avg_daily,
        global_avg_daily=global_avg_daily,
        target_daily=target_daily,
        vs_global_pct=vs_global_pct,
    )
