import json
import os
from flask import (
    render_template, session, flash, redirect,
    url_for, request, jsonify, make_response
)
from front import front_bp
from extensions import db
from models.product import Product
from bakong_khqr import KHQR
from dotenv import load_dotenv
import requests
from models import Order, OrderItem

load_dotenv()


@front_bp.route('/payment')
def payment():

    checkout_info = session.get('checkout_info')
    total = session.get('checkout_total')

    if not checkout_info or total is None:
        flash('Please complete checkout first.', 'warning')
        return redirect(url_for('front_bp.checkout'))

    # Read the cart
    cart_cookie = request.cookies.get('cart_list')

    try:
        cart_list = json.loads(cart_cookie) if cart_cookie else []
    except (json.JSONDecodeError, TypeError):
        cart_list = []

    if not isinstance(cart_list, list) or not cart_list:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('front_bp.cart'))

    # Validate cart and check stock before generating QR
    payment_cart = []

    for item in cart_list:
        if not isinstance(item, dict):
            continue

        try:
            product_id = int(item.get('id'))
            qty = int(item.get('qty', 1))
        except (ValueError, TypeError):
            continue

        if qty < 1:
            continue

        product = db.session.get(Product, product_id)

        if not product:
            continue

        if product.qty < qty:
            flash(
                f'Not enough stock for {product.name}. Available: {product.qty}.',
                'danger'
            )
            return redirect(url_for('front_bp.cart'))

        payment_cart.append({
            'id': product.id,
            'qty': qty
        })

    if not payment_cart:
        flash('Your cart contains no valid products.', 'warning')
        return redirect(url_for('front_bp.cart'))

    # Save the exact quantities for payment verification
    session['payment_cart'] = payment_cart

    khqr = KHQR(os.getenv('BAKONG_TOKEN'))

    qr_string = khqr.create_qr(
        account_id=os.getenv('BAKONG_ACCOUNT_ID'),
        merchant_name="SETEC Market",
        merchant_city="Phnom Penh",
        amount=total,
        currency="USD",
        store_label="Cashier-01",
        phone_number="092161702",
        bill_number="TRX012345",
        terminal_label="POS-01",
        static=False,
        expiration=1
    )

    md5 = khqr.generate_md5(qr_string)
    session['payment_md5'] = md5

    # Reset the processed marker for this new payment
    session.pop('payment_processed_md5', None)

    qr_image = khqr.qr_image(qr_string, format="base64_uri")

    return render_template(
        'frontend/payment.html',
        qr_image=qr_image,
        amount=total,
        checkout_info=checkout_info
    )


@front_bp.get('/payment/check')
def check_payment():

    md5 = session.get('payment_md5')

    if not md5:
        return jsonify({
            'status': 'ERROR',
            'message': 'Payment reference not found.'
        }), 400

    # Prevent stock from being deducted more than once
    if session.get('payment_processed_md5') == md5:
        return jsonify({'status': 'PAID'})

    try:
        khqr = KHQR(os.getenv('BAKONG_TOKEN'))

        payment_status = khqr.check_payment(md5)

        # Some package versions may return a tuple
        if isinstance(payment_status, tuple):
            payment_status = payment_status[0]

        if payment_status != 'PAID':
            return jsonify({'status': payment_status})

        # Payment is confirmed. Now deduct stock.
        payment_cart = session.get('payment_cart', [])

        if not payment_cart:
            return jsonify({
                'status': 'PAID',
                'stock_updated': False,
                'message': 'Payment confirmed, but cart information is missing.'
            }), 400

        # Check all products before changing any stock
        products_to_update = []

        for item in payment_cart:
            product = db.session.get(Product, int(item['id']))
            qty = int(item['qty'])

            if not product:
                db.session.rollback()
                return jsonify({
                    'status': 'PAID',
                    'stock_updated': False,
                    'message': 'A product in this order no longer exists.'
                }), 409

            if product.qty < qty:
                db.session.rollback()
                return jsonify({
                    'status': 'PAID',
                    'stock_updated': False,
                    'message': f'Not enough remaining stock for {product.name}.'
                }), 409

            products_to_update.append((product, qty))

        new_order = Order(
            user_id=session.get('user_id'),
            total_amount=session.get('checkout_total'),
            status='paid'
        )

        db.session.add(new_order)
        db.session.flush()

        # Create order items and deduct stock
        for product, qty in products_to_update:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=qty,
                price=product.price
            )

            db.session.add(order_item)

            # Deduct stock
            product.qty -= qty

        # Save order, order items, and stock changes together
        db.session.commit()

        checkout_info = session.get('checkout_info', {})

        str_list = ""

        for product, qty in products_to_update:
            str_list += (
                f"<code>{product.name} ({qty} x ${product.price:.2f})</code>\n"
            )

        firstName = checkout_info.get('firstName', '')
        lastName = checkout_info.get('lastName', '')
        email = checkout_info.get('email', '')
        phone = checkout_info.get('phone', '')
        address = checkout_info.get('address', '')

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        message = ""
        message += "<code>===== ORDER RECEIPT =====</code>\n"
        message += "<code>- - - - - - - - - - - - -</code>\n"
        message += f"<code>🧑🏻 Name    : {firstName} {lastName}</code>\n"
        message += f"<code>📱 Phone   : {phone}</code>\n"
        message += f"<code>✉️ Email   : {email}</code>\n"
        message += f"<code>📍 Address : {address}</code>\n"
        message += "<code>- - - - - - - - - - - - -</code>\n"
        message += str_list
        message += "<code>- - - - - - - - - - - - -</code>\n"
        message += "<code>Payment Status: PAID</code>\n"

        payload = {
            "text": message,
            "parse_mode": "HTML",
            "chat_id": chat_id
        }

        try:
            telegram_response = requests.post(url, json=payload, timeout=10)
            telegram_response.raise_for_status()
        except requests.RequestException as e:
            print(f"Telegram notification failed: {e}")

        # Mark payment as processed
        session['payment_processed_md5'] = md5

        # Mark this payment as processed
        session['payment_processed_md5'] = md5

        # Clear the cart and checkout data
        session.pop('payment_cart', None)
        session.pop('checkout_info', None)
        session.pop('checkout_total', None)

        response = make_response(jsonify({
            'status': 'PAID',
            'stock_updated': True
        }))

        response.set_cookie(
            'cart_list',
            '',
            max_age=0,
            httponly=True,
            samesite='Lax'
        )

        return response

    except Exception as e:
        db.session.rollback()
        print(f'Payment verification error: {e}')

        return jsonify({
            'status': 'ERROR',
            'message': 'Could not verify payment. Please try again.'
        }), 500


@front_bp.route('/payment/success')
def payment_success():

    if not session.get('payment_processed_md5'):
        flash('No completed payment found.', 'warning')
        return redirect(url_for('front_bp.home'))

    return render_template('frontend/payment_success.html')