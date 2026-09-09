from admin import admin_bp
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from functools import wraps

from extensions import db
from sqlalchemy import text


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_login'):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.get('/login')
def admin_login():
    module = 'login'
    return render_template('admin/login.html', module=module)


@admin_bp.post('/login')
def admin_do_login():
    module = 'login'
    form = request.form
    username = form.get('username').strip()
    password = form.get('password')

    sql = text("SELECT * FROM user WHERE username = :username")
    user = db.session.execute(sql, {'username': username}).fetchone()

    if user:
        if check_password_hash(user[3], password):
            session.clear()
            session['is_login'] = True
            session['user_id'] = user[0]
            session['profile'] = user[1]
            session['username'] = user[2]
            session['password'] = user[3]
            session['email'] = user[4]
            session['role'] = user[5]
            return redirect(url_for("admin_bp.dashboard"))
    else:
        return redirect(url_for("admin_login"))

    return redirect(url_for("admin_bp.dashboard"))