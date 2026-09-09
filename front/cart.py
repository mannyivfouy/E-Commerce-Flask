import json
from front import front_bp
from flask import render_template, request, make_response
from helper import get_product_by_id

@front_bp.route('/cart')
def cart():
    product_id = request.args.get('product_id')
    action = request.args.get('action')

    cart_list = request.cookies.get('cart_list')
    cart_list = json.loads(cart_list) if cart_list else []

    if product_id:
        duplicated_product_id = [item['id'] for item in cart_list]

        if action == 'remove':
            cart_list = [item for item in cart_list if item['id'] != product_id]

        elif action == 'increase':
            for item in cart_list:
                if item['id'] == product_id:
                    item['qty'] += 1
                    break

        elif action == 'decrease':
            for item in cart_list:
                if item['id'] == product_id:
                    if item['qty'] > 1:
                        item['qty'] -= 1
                    else:
                        item['qty'] = 1

        else:
            if product_id in duplicated_product_id:
                for item in cart_list:
                    if item['id'] == product_id:
                        item['qty'] += 1
            else:
                cart_list.append({'id': product_id, 'qty': 1})

    elif not product_id or product_id == '':
        pass

    # map data
    for item in cart_list:
        item['image'] = get_product_by_id(item['id'])['image']
        item['title'] = get_product_by_id(item['id'])['title']
        item['price'] = get_product_by_id(item['id'])['price']
        item['category'] = get_product_by_id(item['id'])['category']
        item['description'] = get_product_by_id(item['id'])['description']

    total = 0
    for item in cart_list:
        total += float(item['price']) * float(item['qty'])

    response = make_response(render_template('frontend/cart.html', cart_list=cart_list, total=total))
    response.set_cookie('cart_list', json.dumps(cart_list))
    return response