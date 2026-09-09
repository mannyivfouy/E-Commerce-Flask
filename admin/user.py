import allowed

from admin import admin_bp
from flask import render_template, request, redirect, url_for
from admin.auth import login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from extensions import db
from sqlalchemy import text
import os
from models.user import User
from helper import allowed_file, save_user_image, UPLOAD_DIR, USER_UPLOAD_DIR, ALLOWED_EXTENSIONS

@admin_bp.get('/user')
@login_required
def users():
    module = 'users'
    sql = text("select * from user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]
    return render_template('admin/user/user.html', module=module, users=rows)


@admin_bp.get('/user/edit/<int:user_id>')
@login_required
def edit_user(user_id):
    module = 'users'
    sql = text("select * from user where id = :user_id")
    result = db.session.execute(sql, {'user_id': user_id}).fetchone();
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for("users"));
    return render_template('admin/user/edit.html', module=module, user=user)


@admin_bp.post('/user/edit')
@login_required
def do_edit_user():
    module = 'users'
    form = request.form
    file = request.files.get('profile')

    user = User.query.get(form.get('user_id'))

    if not user:
        return redirect(url_for("users"))

    user.username = form.get('username')
    user.email = form.get('email')
    user.role = form.get('role')

    # Only update profile if a new image was uploaded
    if file and file.filename and allowed(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_DIR, filename))
        user.profile = filename

    # Only update password if user entered a new one
    password = form.get('password')

    if password:
        user.password = generate_password_hash(password)

    db.session.commit()

    return redirect(url_for("admin_bp.users"))


@admin_bp.get('/user/add')
@login_required
def add_user():
    module = 'users'

    return render_template(
        'admin/user/add.html',
        module=module
    )


@admin_bp.post('/user/add')
@login_required
def do_add_user():
    module = 'users'
    form = request.form
    file = request.files.get('profile')

    password = generate_password_hash(form['password'])

    # Create user first
    user = User(
        username=form.get('username'),
        email=form.get('email'),
        password=password,
        role=form.get('role'),
        profile=None
    )

    db.session.add(user)

    # Generate user ID
    db.session.flush()

    # Save profile image
    if file and file.filename:
        images = save_user_image(
            file,
            USER_UPLOAD_DIR,
            user.id,
            ALLOWED_EXTENSIONS
        )

        if images:
            user.profile = images['original']

    db.session.commit()

    return redirect(url_for("admin_bp.users"))


@admin_bp.get('/user/confirm-delete/<int:user_id>')
@login_required
def confirm_delete_user(user_id):
    module = 'users'
    sql = text("select * from user where id = :user_id")
    result = db.session.execute(sql, {'user_id': user_id}).fetchone();
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for("users"));
    return render_template('admin/user/confirm_delete.html', module=module, user=user)


@admin_bp.post('/user/delete')
@login_required
def delete_user():
    module = 'users'
    form = request.form
    user_id = form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("admin_bp.users"));
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_bp.users"));