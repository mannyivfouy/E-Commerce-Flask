
from flask import Flask, render_template, request, make_response, redirect, url_for, request, session
from admin import admin_bp
from api import api_bp
from config import Config
from extensions import db, migrate

from front import front_bp

app = Flask(__name__)

# config
app.config.from_object(Config)

# extension
db.init_app(app)
migrate.init_app(app, db)

# Load model
import models

app.register_blueprint(front_bp, url_prefix="/")

app.register_blueprint(admin_bp, url_prefix="/admin")

app.register_blueprint(api_bp, url_prefix="/api")



if __name__ == '__main__':
    app.run()
