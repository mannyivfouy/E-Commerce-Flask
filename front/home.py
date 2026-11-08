from front import front_bp
from flask import render_template
from models import Product

@front_bp.get('/')
def home():
    products = Product.query.limit(8).all()

    return render_template(
        'frontend/index.html',
        products=products
    )