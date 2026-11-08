
import json
import os
import requests

from front import front_bp
from flask import request, redirect, render_template, make_response, flash, session, url_for
from extensions import db
from models.product import Product


@front_bp.route('/checkout')
def checkout():

    if not session.get('user_id'):
        flash('Please login to continue purchasing.', 'warning')
        return redirect(url_for('front_bp.login', next=request.url))

    # Get cart from cookie
    cart_cookie = request.cookies.get('cart_list')

    try:
        cart_list = json.loads(cart_cookie) if cart_cookie else []
    except (json.JSONDecodeError, TypeError):
        cart_list = []

    if not isinstance(cart_list, list) or not cart_list:
        return redirect('/cart')

    # Get product IDs
    product_ids = []

    for item in cart_list:
        if isinstance(item, dict) and 'id' in item:
            try:
                product_ids.append(int(item['id']))
            except (ValueError, TypeError):
                continue

    # Get products from database
    products = Product.query.filter(
        Product.id.in_(product_ids)
    ).all() if product_ids else []

    product_map = {str(product.id): product for product in products}

    valid_cart = []
    total = 0

    for item in cart_list:

        product = product_map.get(str(item.get('id')))

        if not product:
            continue

        try:
            qty = max(1, int(item.get('qty', 1)))
        except (ValueError, TypeError):
            qty = 1

        price = float(product.price)

        valid_cart.append({
            'id': product.id,
            'title': product.name,
            'image': product.image,
            'price': price,
            'qty': qty
        })

        total += price * qty

    if not valid_cart:
        return redirect('/cart')

    return render_template(
        'frontend/checkout.html',
        cart_list=valid_cart,
        total=total
    )



@front_bp.post('/checkout')
def do_checkout():

    if not session.get('user_id'):
        flash('Please login to continue purchasing.', 'warning')
        return redirect(url_for('front_bp.login', next=url_for('front_bp.checkout')))

    # Get cart from cookie
    cart_cookie = request.cookies.get('cart_list')

    try:
        cart_list = json.loads(cart_cookie) if cart_cookie else []
    except (json.JSONDecodeError, TypeError):
        cart_list = []

    if not isinstance(cart_list, list) or not cart_list:
        flash('Your cart is empty.', 'warning')
        return redirect('/cart')

    # Get product IDs
    product_ids = []

    for item in cart_list:
        if isinstance(item, dict) and 'id' in item:
            try:
                product_ids.append(int(item['id']))
            except (ValueError, TypeError):
                continue

    products = Product.query.filter(
        Product.id.in_(product_ids)
    ).all() if product_ids else []

    product_map = {str(product.id): product for product in products}

    total = 0

    for item in cart_list:

        if not isinstance(item, dict):
            continue

        product = product_map.get(str(item.get('id')))

        if not product:
            continue

        try:
            qty = max(1, int(item.get('qty', 1)))
        except (ValueError, TypeError):
            qty = 1

        price = float(product.price)
        total += price * qty

    if total <= 0:
        flash('Your cart contains no valid products.', 'warning')
        return redirect('/cart')

    # Customer information
    firstName = request.form.get('firstName', '').strip()
    lastName = request.form.get('lastName', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not all([firstName, lastName, email, phone, address]):
        flash('Please complete all checkout fields.', 'danger')
        return redirect('/checkout')

    # Save customer information for payment
    session['checkout_info'] = {
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'phone': phone,
        'address': address
    }

    # Save calculated total
    session['checkout_total'] = round(total, 2)

    # Redirect to payment page
    return redirect(url_for('front_bp.payment'))

