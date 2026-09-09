from front import front_bp
from flask import render_template

@front_bp.route('/login')
def login():
    return render_template('frontend/login.html')


@front_bp.route('/create-account')
def create_account():
    return render_template('frontend/create-account.html')


@front_bp.route('/forgot-password')
def forgot_password():
    return render_template('frontend/forgot-password.html')


@front_bp.route('/account')
def account():
    return render_template('frontend/account.html')