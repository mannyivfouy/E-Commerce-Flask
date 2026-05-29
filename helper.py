from product import products

def get_product_by_id(product_id):
	for product in products:
		if str(product['id']) == str(product_id):
			return product
	return None

def get_product_by_category(category):
	category_products = []
	for product in products:
		if str(product['category']) == str(category):
			category_products.append(product)
	return category_products