from extensions import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    items = db.relationship('OrderItem', backref='order', lazy=True)