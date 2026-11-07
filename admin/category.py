from admin import admin_bp
from flask import render_template, request, redirect, url_for, flash
from admin.auth import login_required
from extensions import db, limiter
from sqlalchemy import text
from models.category import Category
from models.product import Product


# Display all categories
@admin_bp.get('/category')
@login_required
@limiter.limit("10 per minute")
def categories():

    categories = Category.query.order_by(Category.id.desc()).all()

    total_categories = len(categories)

    categories_with_products = sum(
        1 for category in categories if category.products
    )

    empty_categories = total_categories - categories_with_products

    total_products = Product.query.count()

    return render_template(
        'admin/category/category.html',
        categories=categories,
        total_categories=total_categories,
        categories_with_products=categories_with_products,
        empty_categories=empty_categories,
        total_products=total_products,
        module='category'
    )


# Edit category page
@admin_bp.get('/category/edit/<int:category_id>')
@login_required
@limiter.limit("10 per minute")
def edit_category(category_id):
    module = 'category'

    sql = text("SELECT * FROM category WHERE id = :category_id")
    result = db.session.execute(
        sql,
        {'category_id': category_id}
    ).fetchone()

    category = None

    if result:
        category = dict(result._mapping)
    else:
        return redirect(url_for("admin_bp.categories"))

    return render_template(
        'admin/category/edit.html',
        module=module,
        category=category
    )


# Process category edit
@admin_bp.post('/category/edit')
@login_required
@limiter.limit("10 per minute")
def do_edit_category():
    form = request.form

    category = Category.query.get(form.get('category_id'))

    if not category:
        return redirect(url_for("admin_bp.categories"))

    category.name = form.get('name')
    category.description = form.get('description')

    db.session.commit()

    return redirect(url_for("admin_bp.categories"))


# Add category page
@admin_bp.get('/category/add')
@login_required
@limiter.limit("10 per minute")
def add_category():
    module = 'category'

    return render_template(
        'admin/category/add.html',
        module=module
    )


# Process category creation
@admin_bp.post('/category/add')
@login_required
@limiter.limit("10 per minute")
def do_add_category():
    form = request.form

    category = Category(
        name=form.get('name'),
        description=form.get('description')
    )

    db.session.add(category)
    db.session.commit()

    return redirect(url_for("admin_bp.categories"))


# Confirm category deletion
@admin_bp.get('/category/confirm-delete/<int:category_id>')
@login_required
@limiter.limit("10 per minute")
def confirm_delete_category(category_id):
    module = 'category'

    sql = text("SELECT * FROM category WHERE id = :category_id")
    result = db.session.execute(
        sql,
        {'category_id': category_id}
    ).fetchone()

    category = None

    if result:
        category = dict(result._mapping)
    else:
        return redirect(url_for("admin_bp.categories"))

    return render_template(
        'admin/category/confirm_delete.html',
        module=module,
        category=category
    )


# Process category deletion
@admin_bp.post('/category/delete')
@login_required
@limiter.limit("10 per minute")
def delete_category():
    form = request.form
    category_id = form.get('category_id')

    category = Category.query.get(category_id)

    if not category:
        return redirect(url_for("admin_bp.categories"))

    # Prevent deleting categories that still have products
    if category.products:
        flash(
            "Cannot delete this category because it contains products.",
            "warning"
        )
        return redirect(url_for("admin_bp.categories"))

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("admin_bp.categories"))