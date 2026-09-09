from front import front_bp
from flask import request, redirect, render_template, make_response
from product import  products as pro
import json

@front_bp.route('/checkout')
def checkout():
    cart_list = request.cookies.get('cart_list')
    cart_list = json.loads(cart_list) if cart_list else []

    if not cart_list:
        return redirect('/cart')
    # total price
    total = 0
    for item in cart_list:
        total += float(item['price']) * float(item['qty'])

    return render_template('frontend/checkout.html', cart_list=cart_list, total=total)


@front_bp.post('/checkout')
def do_checkout():
    cart_list = request.cookies.get('cart_list')
    cart_list = json.loads(cart_list) if cart_list else []
    str_list = ""
    for item in cart_list:
        str_list += f"<code>{item['title']} ({item['qty']} x ${item['price']})</code> \n"

    form = request.form
    firstName = form['firstName']
    lastName = form['lastName']
    email = form['email']
    phone = form['phone']
    address = form['address']

    # send message
    import requests

    bot_token = "8652371918:AAHNgxYKUcMicPDq1BDPnJr7tqWkPNKLxBU"
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

    payload = {
        "text": f"{message}",
        "parse_mode": "HTML",
        "chat_id": "@bot_flask_sv26shop",
        "disable_web_page_preview": False,
        "disable_notification": False,
        "reply_to_message_id": None
    }
    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    response = make_response(
        render_template('frontend/index.html', products=pro)
    )

    response.set_cookie('cart_list', '')

    return response