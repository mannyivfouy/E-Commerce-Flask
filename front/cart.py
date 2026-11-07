import json
from front import front_bp
from flask import render_template, request, make_response
from extensions import db
from models.product import Product


@front_bp.route('/cart')
def cart():
    product_id = request.args.get('product_id')
    action = request.args.get('action')

    # Get cart from cookie
    cart_cookie = request.cookies.get('cart_list')

    try:
        cart_list = json.loads(cart_cookie) if cart_cookie else []
    except (json.JSONDecodeError, TypeError):
        cart_list = []

    if not isinstance(cart_list, list):
        cart_list = []

    # Add, remove, increase, decrease
    if product_id:
        duplicated_product_id = [
            str(item['id']) for item in cart_list
            if isinstance(item, dict) and 'id' in item
        ]

        if action == 'remove':
            cart_list = [
                item for item in cart_list
                if str(item.get('id')) != product_id
            ]

        elif action == 'increase':
            for item in cart_list:
                if str(item.get('id')) == product_id:
                    item['qty'] = int(item['qty']) + 1
                    break

        elif action == 'decrease':
            for item in cart_list:
                if str(item.get('id')) == product_id:
                    item['qty'] = max(1, int(item['qty']) - 1)
                    break

        else:
            if product_id in duplicated_product_id:
                for item in cart_list:
                    if str(item['id']) == product_id:
                        item['qty'] = int(item['qty']) + 1
                        break
            else:
                # Verify product exists in database
                product = db.session.get(Product, int(product_id))

                if product:
                    cart_list.append({
                        'id': str(product.id),
                        'qty': 1
                    })

    # Map product data from database
    product_ids = []

    for item in cart_list:
        try:
            product_ids.append(int(item['id']))
        except (ValueError, TypeError, KeyError):
            continue

    products = db.session.query(Product).filter(
        Product.id.in_(product_ids)
    ).all() if product_ids else []

    product_map = {str(product.id): product for product in products}

    valid_cart = []
    total = 0

    for item in cart_list:
        product = product_map.get(str(item.get('id')))

        if not product:
            continue

        qty = max(1, int(item.get('qty', 1)))

        valid_cart.append({
            'id': str(product.id),
            'qty': qty,
            'image': product.image,
            'name': product.name,
            'price': product.price,
            'category': product.category.name if product.category else '',
            'description': product.description
        })

        total += float(product.price) * qty

    cart_list = valid_cart

    response = make_response(
        render_template(
            'frontend/cart.html',
            cart_list=cart_list,
            total=total
        )
    )

    response.set_cookie(
        'cart_list',
        json.dumps([
            {'id': item['id'], 'qty': item['qty']}
            for item in cart_list
        ]),
        httponly=True,
        samesite='Lax'
    )

    return response
