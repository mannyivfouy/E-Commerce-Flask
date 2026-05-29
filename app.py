from flask import Flask, render_template, request, make_response
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
	cart_list = request.cookies.get('cart_list')
	cart_list = json.loads(cart_list) if cart_list else []

	if product_id:
		duplicated_product_id = [item['id'] for item in cart_list]
		if product_id in duplicated_product_id:
			for item in cart_list:
				if item['id'] == product_id:
					item['qty'] += 1
		else:
			cart_list.append({"id": product_id, "qty": 1})
	elif not product_id or product_id == '':
		pass

	# map data
	for item in cart_list:
		item['image'] = get_product_by_id(item['id'])['image']
		item['title'] = get_product_by_id(item['id'])['title']
		item['price'] = get_product_by_id(item['id'])['price']
		item['category'] = get_product_by_id(item['id'])['category']
		item['description'] = get_product_by_id(item['id'])['description']

	response = make_response(render_template('frontend/cart.html', cart_list=cart_list))
	response.set_cookie('cart_list', json.dumps(cart_list))
	return response




@app.route('/checkout')
def checkout():
	return render_template('frontend/checkout.html')

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

if __name__ == '__main__':
	app.run()
