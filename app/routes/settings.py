from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'profile':
            name = request.form.get('name', '').strip()
            household_size = request.form.get('household_size', '1').strip()
            daily_goal = request.form.get('daily_goal_kg', '5.5').strip()

            if not name:
                flash('Name cannot be empty.', 'error')
                return redirect(url_for('settings.index'))

            try:
                household_size = max(1, int(household_size))
            except ValueError:
                household_size = current_user.household_size or 1

            try:
                daily_goal = max(0.1, float(daily_goal))
            except ValueError:
                daily_goal = current_user.daily_goal_kg or 5.5

            current_user.name = name
            current_user.household_size = household_size
            current_user.daily_goal_kg = round(daily_goal, 1)
            db.session.commit()
            flash('Profile updated.', 'success')

        elif action == 'password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not current_user.check_password(current_pw):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Password changed successfully.', 'success')

        return redirect(url_for('settings.index'))

    return render_template('settings/index.html')
