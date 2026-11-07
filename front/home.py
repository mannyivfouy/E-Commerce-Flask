from front import front_bp
from flask import render_template

@front_bp.get('/')
def home():
    return render_template('frontend/index.html')