from extensions import db

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')