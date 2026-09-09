from product import products
import os
from PIL import Image

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



UPLOAD_DIR = os.path.join("static", "uploads")
USER_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "users")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename, allowed_extension):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


def save_user_image(file, upload_folder, user_id, allowed_extension, thumb_size=(300, 300)):
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename, allowed_extension):
        return None

    extension = file.filename.rsplit('.', 1)[1].lower()
    original_filename = f"{user_id}_org_user.{extension}"
    original_path = os.path.join(upload_folder, original_filename)
    file.save(original_path)

    image = Image.open(original_path)
    thumbnail = image.copy()
    thumbnail.thumbnail(thumb_size)
    thumbnail_filename = f"{user_id}_thum_user.{extension}"
    thumbnail_path = os.path.join(upload_folder, thumbnail_filename)

    if extension in ("jpg", "jpeg"):
        thumbnail.save(
            thumbnail_path,
            quality=75,
            optimize=True
        )
    else:
        thumbnail.save(
            thumbnail_path,
            optimize=True
        )
    return {
        "original": original_filename,
        "thumbnail": thumbnail_filename
    }
