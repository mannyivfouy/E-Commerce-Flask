from fcntl import FASYNC

from flask import Flask, render_template, request, make_response, redirect, url_for, request, session
from product import products as pro
from helper import get_product_by_id, get_product_by_category
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps
from PIL import Image

from config import Config
from extensions import db, migrate

from front import front_bp

app = Flask(__name__)

# config
app.config.from_object(Config)

# extension
db.init_app(app)
migrate.init_app(app, db)

# Load model
import models

# helper
UPLOAD_DIR = os.path.join("static", "uploads")
USER_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "users")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_login'):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped

app.register_blueprint(front_bp, url_prefix="/")




# Admin Panel

@app.get('/admin')
@login_required
def dashboard():
    module = 'dashboard'
    # if not session.get('is_login'):
    # 	return redirect(url_for('admin_login'))
    return render_template('admin/dashboard/dashboard.html', module=module)


@app.get('/admin/user')
@login_required
def users():
    module = 'users'
    sql = text("select * from user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]
    return render_template('admin/user/user.html', module=module, users=rows)


@app.get('/admin/user/edit/<int:user_id>')
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


@app.post('/admin/user/edit')
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

    return redirect(url_for("users"))


@app.get('/admin/user/add')
@login_required
def add_user():
    module = 'users'

    return render_template(
        'admin/user/add.html',
        module=module
    )


@app.post('/admin/user/add')
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

    return redirect(url_for("users"))


@app.get('/admin/user/confirm-delete/<int:user_id>')
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


@app.post('/admin/user/delete')
@login_required
def delete_user():
    module = 'users'
    form = request.form
    user_id = form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("users"));
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("users"));


@app.get('/admin/login')
def admin_login():
    module = 'login'
    return render_template('admin/login.html', module=module)


@app.post('/admin/login')
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
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("admin_login"))

    return redirect(url_for("dashboard"))


def allowed_file(filename, allowed_extension):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


def save_user_image(file, upload_folder, user_id, allowed_extension, thumb_size=(300, 300)):
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename, allowed_extension):
        return None

    extension = file.filename.rsplit('.', 1)[1].lower()
    original_filename = f"{user_id}_org_user.{extension}"
    original_path = os.path.join(upload_folder, original_filename)
    file.save(original_path)

    image = Image.open(original_path)
    thumbnail = image.copy()
    thumbnail.thumbnail(thumb_size)
    thumbnail_filename = f"{user_id}_thum_user.{extension}"
    thumbnail_path = os.path.join(upload_folder, thumbnail_filename)

    if extension in ("jpg", "jpeg"):
        thumbnail.save(
            thumbnail_path,
            quality=75,
            optimize=True
        )
    else:
        thumbnail.save(
            thumbnail_path,
            optimize=True
        )
    return {
        "original": original_filename,
        "thumbnail": thumbnail_filename
    }

# @app.before_request
# def before_request():
# 	path = request.path
# 	if 'admin' in path:
# 		if session.get('is_login'):
# 			return redirect(url_for('dashboard'))
# 		else:
# 			return redirect(url_for('admin_login'))
# 	return None


if __name__ == '__main__':
    app.run()
