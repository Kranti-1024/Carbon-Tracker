import csv
import io
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_required, current_user
from app import db, limiter
from app.models.activity import Activity, EmissionFactor

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")


@activities_bp.route("/log", methods=["GET", "POST"])
@login_required
def log_activity():
    factors = EmissionFactor.query.order_by(EmissionFactor.category, EmissionFactor.label).all()
    grouped = {}
    for f in factors:
        grouped.setdefault(f.category, []).append(f)

    if request.method == "POST":
        factor_key = request.form.get("factor_key")
        quantity_raw = request.form.get("quantity", "").strip()
        logged_date_raw = request.form.get("logged_date", "").strip()
        note = request.form.get("note", "").strip()[:255]  # cap at DB column length

        factor = EmissionFactor.query.filter_by(key=factor_key).first()
        if factor is None:
            flash("Please choose a valid activity type.", "error")
            return render_template("activities/log.html", grouped=grouped, today=date.today().isoformat())

        try:
            quantity = float(quantity_raw)
            if quantity < 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive number.", "error")
            return render_template("activities/log.html", grouped=grouped, today=date.today().isoformat())

        try:
            logged_date = datetime.strptime(logged_date_raw, "%Y-%m-%d").date() if logged_date_raw else date.today()
        except ValueError:
            logged_date = date.today()

        co2e = round(quantity * factor.kg_co2e_per_unit, 3)

        activity = Activity(
            user_id=current_user.id,
            factor_key=factor.key,
            quantity=quantity,
            co2e_kg=co2e,
            logged_date=logged_date,
            note=note or None,
        )
        db.session.add(activity)
        db.session.commit()

        flash(f"Logged {factor.label} — {co2e} kg CO2e added.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("activities/log.html", grouped=grouped, today=date.today().isoformat())


@activities_bp.route("/history")
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.logged_date.desc(), Activity.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template("activities/history.html", activities=pagination.items, pagination=pagination)

@activities_bp.route("/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id, user_id=current_user.id).first_or_404()
    factors = EmissionFactor.query.order_by(EmissionFactor.category, EmissionFactor.label).all()
    grouped = {}
    for f in factors:
        grouped.setdefault(f.category, []).append(f)

    if request.method == 'POST':
        factor_key = request.form.get('factor_key')
        quantity_raw = request.form.get('quantity', '').strip()
        logged_date_raw = request.form.get('logged_date', '').strip()
        note = request.form.get('note', '').strip()[:255]  # cap at DB column length

        factor = EmissionFactor.query.filter_by(key=factor_key).first()
        if factor is None:
            flash('Please choose a valid activity type.', 'error')
            return render_template('activities/edit.html', activity=activity, grouped=grouped, today=date.today().isoformat())

        try:
            quantity = float(quantity_raw)
            if quantity < 0:
                raise ValueError
        except ValueError:
            flash('Quantity must be a positive number.', 'error')
            return render_template('activities/edit.html', activity=activity, grouped=grouped, today=date.today().isoformat())

        try:
            logged_date = datetime.strptime(logged_date_raw, '%Y-%m-%d').date() if logged_date_raw else activity.logged_date
        except ValueError:
            logged_date = activity.logged_date

        activity.factor_key = factor.key
        activity.quantity = quantity
        activity.co2e_kg = round(quantity * factor.kg_co2e_per_unit, 3)
        activity.logged_date = logged_date
        activity.note = note or None
        db.session.commit()

        flash(f'Updated — {factor.label}: {activity.co2e_kg} kg CO2e.', 'success')
        return redirect(url_for('activities.history'))

    return render_template('activities/edit.html', activity=activity, grouped=grouped, today=date.today().isoformat())

@activities_bp.route('/export/csv')
@login_required
@limiter.limit('10/minute')
def export_csv():
    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.logged_date.desc(), Activity.created_at.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Activity', 'Quantity', 'Unit', 'CO2e (kg)', 'Note'])
    for a in activities:
        writer.writerow([
            a.logged_date.isoformat(),
            a.factor.category,
            a.factor.label,
            a.quantity,
            a.factor.unit,
            a.co2e_kg,
            a.note or ''
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=carbon-ledger-export.csv'}
    )


@activities_bp.route("/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id, user_id=current_user.id).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()
        flash("Entry removed.", "info")
    return redirect(url_for("activities.history"))
