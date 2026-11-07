from admin import admin_bp
from flask import render_template, request, redirect, url_for, flash
from admin.auth import login_required
from extensions import db, limiter
from models.order import Order
from models.user import User


# Display all orders
@admin_bp.get('/order')
@login_required
@limiter.limit("10 per minute")
def orders():
    module = 'order'

    result = (
        db.session.query(
            Order,
            User.username.label('username')
        )
        .join(User, Order.user_id == User.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    rows = [
        {
            'order': order,
            'username': username
        }
        for order, username in result
    ]

    return render_template(
        'admin/order/order.html',
        module=module,
        orders=rows
    )


# Display order details
@admin_bp.get('/order/detail/<int:order_id>')
@login_required
@limiter.limit("10 per minute")
def order_details(order_id):
    module = 'order'

    order = Order.query.get(order_id)

    if not order:
        return redirect(url_for("admin_bp.orders"))

    user = User.query.get(order.user_id)

    return render_template(
        'admin/order/detail.html',
        module=module,
        order=order,
        user=user
    )


# Update order status
@admin_bp.post('/order/update-status')
@login_required
@limiter.limit("10 per minute")
def update_order_status():
    form = request.form

    order_id = form.get('order_id')
    status = form.get('status')

    order = Order.query.get(order_id)

    if not order:
        return redirect(url_for("admin_bp.orders"))

    # Allowed order statuses
    allowed_statuses = [
        'pending',
        'processing',
        'completed',
        'cancelled'
    ]

    if status not in allowed_statuses:
        flash("Invalid order status.", "danger")
        return redirect(
            url_for("admin_bp.order_details", order_id=order.id)
        )

    order.status = status

    db.session.commit()

    flash("Order status updated successfully.", "success")

    return redirect(
        url_for("admin_bp.order_details", order_id=order.id)
    )