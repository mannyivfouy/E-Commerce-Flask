from flask import jsonify
from api import api_bp
from models.user import User


@api_bp.get('/users')
def get_users():
    users = User.query.all()
    result = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "profile": u.profile,
        }
        for u in users
    ]
    return jsonify(result)


@api_bp.get('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "profile": user.profile,
    })