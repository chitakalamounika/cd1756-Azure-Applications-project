"""
The flask application package.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)

# -----------------------------
# Logging: file + console
# -----------------------------
# You can change this to somewhere your app user can write, e.g. /opt/articlecms/logs
LOG_DIR = os.environ.get("APP_LOG_DIR", "/var/log/articlecms")
LOG_PATH = os.path.join(LOG_DIR, "app.log")

# Make sure the folder exists at runtime (harmless if it already exists)
os.makedirs(LOG_DIR, exist_ok=True)

# File handler (rotating)
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
))

# Console handler (for journalctl)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.addHandler(console)
app.logger.propagate = False

app.logger.info("Application startup")

# -----------------------------
# Extensions
# -----------------------------
Session(app)               # server-side sessions (required by MSAL sample)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'  # default login endpoint

# Late import to avoid circulars
import FlaskWebProject.views  # noqa: E402,F401
