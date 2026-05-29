from flask import Flask, render_template
from product import products as pro
from helper import  get_product_by_id, get_product_by_category

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
	return render_template('frontend/cart.html')

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
