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
from errors import *

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

error_handlers(app)

if __name__ == '__main__':
    app.run()
