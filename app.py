from flask import Flask, render_template
from admin import admin_bp
from api import api_bp
from config import Config
from extensions import db, migrate, limiter
from front import front_bp
from dotenv import load_dotenv
import os, requests
from flask import request

load_dotenv()
app = Flask(__name__)

# config
app.config.from_object(Config)

# extension
db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)

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
