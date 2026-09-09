from front import front_bp
from flask import render_template
from product import products as pro
from helper import get_product_by_id, get_product_by_category

@front_bp.route('/products')
def products():
    return render_template('frontend/products.html', products=pro)


@front_bp.route('/product/<int:product_id>')
def product(product_id):
    product = get_product_by_id(product_id)
    related_product = get_product_by_category(product['category'])
    return render_template('frontend/product.html', product=product, related_product=related_product)