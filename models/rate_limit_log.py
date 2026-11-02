# models/rate_limit_log.py  # NEW

from datetime import datetime
from extensions import db


class RateLimitLog(db.Model):
    __tablename__ = "rate_limit_log"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    limit = db.Column(db.String(50), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )