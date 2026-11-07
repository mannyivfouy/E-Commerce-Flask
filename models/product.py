from extensions import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(255), nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)