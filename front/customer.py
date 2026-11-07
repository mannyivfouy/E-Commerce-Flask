from front import front_bp
from flask import render_template
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models.user import User
from extensions import db


@front_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if session.get('user_id'):
        return redirect(url_for('front_bp.account'))

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == '1'

        # Validate inputs
        if not username or not password:
            flash('Please enter your username and password.', 'danger')
            return redirect(url_for('front_bp.login'))

        # Find user by username
        user = User.query.filter_by(username=username).first()

        # Verify password
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('front_bp.login'))

        # Create session
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = remember

        flash('Login successful. Welcome back!', 'success')

        return redirect(url_for('front_bp.account'))

    return render_template('frontend/login.html')


@front_bp.route('/create-account', methods=['GET', 'POST'])
def create_account():
    # Redirect if already logged in
    if session.get('user_id'):
        return redirect(url_for('front_bp.account'))

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate required fields
        if not username or not email or not password or not confirm_password:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Validate username length
        if len(username) > 80:
            flash('Username cannot exceed 80 characters.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Validate email length
        if len(email) > 120:
            flash('Email cannot exceed 120 characters.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Check existing username
        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash('This username is already taken.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Check existing email
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash('This email is already registered.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Validate password length
        if len(password) < 8:
            flash('Password must contain at least 8 characters.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Confirm password
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            profile=None,
            role='User'
        )

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('This email is already registered.', 'danger')
            return redirect(url_for('front_bp.create_account'))

        flash('Account created successfully. You can now log in.', 'success')

        return redirect(url_for('front_bp.login'))

    return render_template('frontend/create-account.html')


@front_bp.route('/forgot-password')
def forgot_password():
    return render_template('frontend/forgot-password.html')


@front_bp.route('/account')
def account():
    if not session.get('user_id'):
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('front_bp.login'))

    user = db.session.get(User, session['user_id'])

    if not user:
        session.clear()
        flash('Your account could not be found. Please log in again.', 'danger')
        return redirect(url_for('front_bp.login'))

    return render_template('frontend/account.html', user=user)


@front_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()

    flash('You have been logged out successfully.', 'success')

    return redirect(url_for('front_bp.login'))
