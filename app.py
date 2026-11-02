from flask import Flask, render_template, session
from admin import admin_bp
from api import api_bp
from config import Config
from extensions import db, migrate, limiter, csrf, cors
from front import front_bp
from dotenv import load_dotenv
import os, requests
from flask import request
from models.rate_limit_log import RateLimitLog

load_dotenv()
app = Flask(__name__)

# config
app.config.from_object(Config)

# extension
db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
csrf.init_app(app)
csrf.exempt(api_bp)
cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

# Load model
import models

app.register_blueprint(front_bp, url_prefix="/")

app.register_blueprint(admin_bp, url_prefix="/admin")

app.register_blueprint(api_bp, url_prefix="/api")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500
@app.errorhandler(429)
def too_many_requests(e):
    user_id = session.get('user_id')

    rate_limit_log = RateLimitLog(
        user_id=user_id,
        ip_address=request.remote_addr,
        endpoint=request.path,
        method=request.method,
        limit=str(e.description),
    )

    db.session.add(rate_limit_log)
    db.session.commit()

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    message = (
        "<code>⚠️ RATE LIMIT EXCEEDED</code>\n"
        "<code>- - - - - - - - - - - - -</code>\n"
        f"<code>IP     : {request.remote_addr}</code>\n"
        f"<code>Method : {request.method}</code>\n"
        f"<code>Path   : {request.path}</code>\n"
        f"<code>Limit  : {e.description}</code>\n"
        "<code>- - - - - - - - - - - - -</code>\n"
        "<code>Someone exceeded a rate limit.</code>"
    )

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)
    return render_template('error/429.html'), 429


if __name__ == '__main__':
    app.run()
