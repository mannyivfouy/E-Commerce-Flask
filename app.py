from flask import Flask, render_template, request, make_response, redirect
from product import products as pro
from helper import  get_product_by_id, get_product_by_category
import json

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
	return render_template('frontend/index.html', products = pro)

@app.route('/products')
def products():
	return render_template('frontend/products.html', products = pro)

@app.route('/product/<int:product_id>')
def product(product_id):
	product = get_product_by_id(product_id)
	related_product = get_product_by_category(product['category'])
	return render_template('frontend/product.html', product=product, related_product=related_product)

@app.route('/cart')
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
@app.route('/checkout')
def checkout():
	cart_list = request.cookies.get('cart_list')
	cart_list = json.loads(cart_list) if cart_list else []

	if not cart_list:
		return redirect('/cart')
	#total price
	total = 0
	for item in cart_list:
		total += float(item['price']) * float(item['qty'])

	return render_template('frontend/checkout.html', cart_list = cart_list, total = total)

@app.post('/checkout')
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

	#send message
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
		"chat_id" : "@bot_flask_sv26shop",
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


@app.route('/login')
def login():
	return render_template('frontend/login.html')

@app.route('/create-account')
def create_account():
	return render_template('frontend/create-account.html')

@app.route('/forgot-password')
def forgot_password():
	return render_template('frontend/forgot-password.html')

@app.route('/account')
def account():
	return render_template('frontend/account.html')

@app.get('/admin/dashboard')
def dashboard():
	return render_template('admin/index.html')

@app.get('/admin/users')
def users():
	return render_template('admin/users.html')

if __name__ == '__main__':
	app.run()
