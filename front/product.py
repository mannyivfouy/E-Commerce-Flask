from front import front_bp
from flask import render_template, abort
from models import Product, Category
from extensions import db

@front_bp.route('/products')
def products():
    products = db.session.query(Product).all()

    return render_template(
        'frontend/products.html',
        products=products
    )


@front_bp.route('/product/<int:product_id>')
def product(product_id):
    # Find the product by ID
    product = db.session.get(Product, product_id)

    # Return 404 if the product does not exist
    if product is None:
        abort(404)

    # Get products from the same category, excluding current product
    related_product = (
        db.session.query(Product)
        .filter(
            Product.category_id == product.category_id,
            Product.id != product.id
        )
        .all()
    )

    return render_template(
        'frontend/product.html',
        product=product,
        related_product=related_product
    )