from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_wtf import CSRFProtect
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def get_rate_limit_key():
    user_id = session.get('user_id')

    if user_id:
        return f"user:{user_id}"

    return f"ip:{get_remote_address()}"

limiter = Limiter(
    default_limits=["10000 per day", "100 per minute"],
    key_func=get_rate_limit_key,
)

csrf = CSRFProtect()