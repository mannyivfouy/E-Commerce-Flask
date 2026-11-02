from admin import admin_bp
from flask import render_template, session, redirect, url_for
from admin.auth import login_required
from extensions import limiter


@admin_bp.get('/')
@login_required
@limiter.limit("10 per minute")
def dashboard():
    print("SESSION:", session)
    module = 'dashboard'
    if not session.get('is_login'):
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard/dashboard.html', module=module)
