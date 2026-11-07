from admin import admin_bp
from flask import render_template, request, redirect, url_for, flash
from admin.auth import login_required
from extensions import db, limiter
from models.product import Product
from models.category import Category
from helper import PRODUCT_UPLOAD_DIR, ALLOWED_EXTENSIONS, save_product_image


@admin_bp.get('/product')
@login_required
@limiter.limit("10 per minute")
def products():

    products = db.session.query(
        Product,
        Category.name.label('category_name')
    ).join(
        Category,
        Product.category_id == Category.id
    ).order_by(Product.id.desc()).all()

    # Prepare product data for the template
    product_list = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'qty': product.qty,
            'image': product.image,
            'category_name': category_name
        }
        for product, category_name in products
    ]

    total_products = Product.query.count()

    total_categories = Category.query.count()

    average_price = db.session.query(
        db.func.avg(Product.price)
    ).scalar() or 0

    categorized_products = Product.query.filter(
        Product.category_id.isnot(None)
    ).count()

    return render_template(
        'admin/product/product.html',
        products=product_list,
        total_products=total_products,
        total_categories=total_categories,
        average_price=average_price,
        categorized_products=categorized_products,
        module='product'
    )
# Edit product page
@admin_bp.get('/product/edit/<int:product_id>')
@login_required
@limiter.limit("10 per minute")
def edit_product(product_id):
    module = 'product'

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("admin_bp.products"))

    categories = Category.query.all()

    return render_template(
        'admin/product/edit.html',
        module=module,
        product=product,
        categories=categories
    )


# Process product edit
@admin_bp.post('/product/edit')
@login_required
@limiter.limit("10 per minute")
def do_edit_product():
    form = request.form
    file = request.files.get('image')

    product = Product.query.get(form.get('product_id'))

    if not product:
        return redirect(url_for("admin_bp.products"))

    # NEW: Get and validate quantity
    qty = form.get('qty', type=int)

    if qty is None or qty < 0:
        flash("Please enter a valid quantity (0 or greater).", "warning")
        return redirect(url_for("admin_bp.edit_product", product_id=product.id))

    product.name = form.get('name')
    product.description = form.get('description')
    product.price = float(form.get('price'))
    product.category_id = int(form.get('category_id'))
    product.qty = qty  # NEW: Update quantity

    if file and file.filename:
        images = save_product_image(
            file,
            PRODUCT_UPLOAD_DIR,
            product.id,
            ALLOWED_EXTENSIONS
        )

        if images:
            product.image = images['original']
        else:
            flash("Invalid image format. Please upload PNG, JPG, JPEG, or GIF.", "warning")
            return redirect(url_for("admin_bp.edit_product", product_id=product.id))

    db.session.commit()

    return redirect(url_for("admin_bp.products"))


# Add product page
@admin_bp.get('/product/add')
@login_required
@limiter.limit("10 per minute")
def add_product():
    module = 'product'
    categories = Category.query.all()

    return render_template(
        'admin/product/add.html',
        module=module,
        categories=categories
    )

# Process product creation
@admin_bp.post('/product/add')
@login_required
@limiter.limit("10 per minute")
def do_add_product():
    form = request.form
    file = request.files.get('image')

    # NEW: Get and validate quantity
    qty = form.get('qty', type=int)

    if qty is None or qty < 0:
        flash("Please enter a valid quantity (0 or greater).", "warning")
        return redirect(url_for("admin_bp.add_product"))

    product = Product(
        name=form.get('name'),
        description=form.get('description'),
        price=float(form.get('price')),
        category_id=int(form.get('category_id')),
        qty=qty,  # NEW: Save quantity
        image=None
    )

    db.session.add(product)

    # Generate product ID before saving the image
    db.session.flush()

    # Save product image
    if file and file.filename:
        images = save_product_image(
            file,
            PRODUCT_UPLOAD_DIR,
            product.id,
            ALLOWED_EXTENSIONS
        )

        if images:
            product.image = images['original']
        else:
            flash("Invalid image format. Please upload PNG, JPG, JPEG, or GIF.", "warning")

    db.session.commit()

    return redirect(url_for("admin_bp.products"))

# Confirm product deletion
@admin_bp.get('/product/confirm-delete/<int:product_id>')
@login_required
@limiter.limit("10 per minute")
def confirm_delete_product(product_id):
    module = 'product'

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("admin_bp.products"))

    return render_template(
        'admin/product/confirm_delete.html',
        module=module,
        product=product
    )


# Process product deletion
@admin_bp.post('/product/delete')
@login_required
@limiter.limit("10 per minute")
def delete_product():
    form = request.form
    product_id = form.get('product_id')

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("admin_bp.products"))

    # Prevent deleting products referenced by cart or order items
    if product.cart_items or product.order_items:
        flash(
            "Cannot delete this product because it is used in a cart or order.",
            "warning"
        )
        return redirect(url_for("admin_bp.products"))

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("admin_bp.products"))