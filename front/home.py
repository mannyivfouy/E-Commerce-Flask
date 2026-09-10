from front import front_bp
from flask import render_template
from product import products as pro

@front_bp.get('/')
def home():
    return render_template('frontend/index.html', products=pro)