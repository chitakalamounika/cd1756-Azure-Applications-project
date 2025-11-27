import os
import uuid
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash

from FlaskWebProject import app, db, login
from FlaskWebProject.models import User, Article  # adjust if your model names differ

# MSAL
import msal
from config import Config

# ---------- Helpers ----------
def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache,
    )

def _build_auth_url(scopes=None, state=None):
    return _build_msal_app().get_authorization_request_url(
        scopes or Config.SCOPE,
        state=state or str(uuid.uuid4()),
        redirect_uri=request.url_root.rstrip("/") + Config.REDIRECT_PATH,
    )

# ---------- Routes ----------
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template("index.html", articles=articles)

# ---- Local username/password form login (if present) ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if not user:
            app.logger.warning("Invalid login attempt (unknown user) for '%s'", username)
            flash("Invalid username or password", "danger")
            return render_template("login.html")

        # If you store hashed passwords, use check_password_hash
        if hasattr(user, "password_hash") and user.password_hash:
            ok = check_password_hash(user.password_hash, password)
        else:
            # demo fallback (NOT for production)
            ok = (password == "admin")

        if not ok:
            app.logger.warning("Invalid login attempt (bad password) for '%s'", username)
            flash("Invalid username or password", "danger")
            return render_template("login.html")

        # Successful local login
        from flask_login import login_user
        login_user(user)
        app.logger.info("User '%s' logged in successfully (local)", username)
        return redirect(url_for("index"))

    return render_template("login.html")

# ---- Microsoft Sign-in button handler ----
@app.route("/login-microsoft")
def login_microsoft():
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(state=session["state"])
    app.logger.info("Redirecting to Microsoft login; state=%s", session["state"])
    return redirect(auth_url)

# ---- MSAL redirect/callback ----
@app.route(Config.REDIRECT_PATH)
def authorized():
    if request.args.get("state") != session.get("state"):
        app.logger.warning("MS login failed: state mismatch")
        return redirect(url_for("index"))

    if "error" in request.args:
        app.logger.warning("MS login error: %s - %s", request.args["error"], request.args.get("error_description"))
        flash("Microsoft sign-in failed.", "danger")
        return redirect(url_for("login"))

    if "code" not in request.args:
        app.logger.warning("MS login failed: no code in callback")
        return redirect(url_for("login"))

    cache = msal.SerializableTokenCache()
    result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
        request.args["code"],
        scopes=Config.SCOPE,
        redirect_uri=request.url_root.rstrip("/") + Config.REDIRECT_PATH,
    )

    if "id_token_claims" not in result:
        app.logger.warning("MS login failed: token acquisition error: %s", result.get("error_description"))
        flash("Microsoft sign-in failed.", "danger")
        return redirect(url_for("login"))

    claims = result["id_token_claims"]
    upn = claims.get("preferred_username") or claims.get("email") or "unknown"
    name = claims.get("name") or upn
    app.logger.info("MS login successful for '%s'", upn)

    # Map/auto-provision to your User table if necessary
    user = User.query.filter_by(username=upn).first()
    if not user:
        # Create a minimal user record; adjust fields to your model
        user = User(username=upn, is_admin=True if "admin" in upn else False, password_hash="")
        db.session.add(user)
        db.session.commit()
        app.logger.info("Provisioned new user from MS login: '%s'", upn)

    from flask_login import login_user
    login_user(user)
    flash(f"Welcome, {name}!", "success")
    return redirect(url_for("index"))

# Example create article (ensure template/form names match)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        body = request.form.get("body", "").strip()

        # Minimal server-side validation
        if not title or not author or not body:
            flash("All fields are required.", "warning")
            return render_template("create.html")

        # Optional image upload to Blob (if your template uses 'image' input)
        image_file = request.files.get("image")
        image_url = None
        if image_file and image_file.filename:
            from AzureStorage import upload_image  # if your repo has a helper; else implement
            filename = secure_filename(image_file.filename)
            image_url = upload_image(image_file.stream, filename)  # return public URL

        a = Article(title=title, author=author, body=body, image_url=image_url, created_at=datetime.utcnow(), user_id=getattr(current_user, "id", 1))
        db.session.add(a)
        db.session.commit()
        app.logger.info("Article created by '%s': %s", current_user.username, title)
        return redirect(url_for("index"))

    return render_template("create.html")
