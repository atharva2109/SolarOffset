import functools
from flask import Blueprint, abort, app, g, render_template, flash, request, session, redirect, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from solar_offset.db import get_db
from solar_offset.utils.carbon_offset_util import calc_carbon_offset
from solar_offset.utils.statistics_util import calculate_statistics

from math import floor
from uuid import uuid4

bp = Blueprint("auth", __name__, url_prefix="/auth")

# This function is called before every request is processed by a view
# Assigns the record of the currently logged in user to g.user
# Otherwise g.user is None
# g is a variable that can be used in templates
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id', None)

    if user_id is None:
        g.user = None
    else:
        user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            g.user = None
        else:
            user = dict(user)
            if user['display_name']:
                user['name'] = user['display_name']
            else:
                user['name'] = user['email_username']
            g.user = user


# Decorator that can be used to force user to be logged in for a page
# Optionally, specify which user types are allowed and which not
def login_required(allowed_user_types=None):
    set_allowed_user_types = set(allowed_user_types)
    def _wrapper(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("You must log in to view this page", "danger")
                return redirect(url_for('auth.login'))
            else:
                set_user_types = set(g.user.user_type.replace("_", ""))
                if not set_user_types.intersection(set_allowed_user_types):
                    flash("You don't have permission to view this page", "danger")
                    return redirect(url_for('auth.login'))
            return view(**kwargs)

        return wrapped_view
    return _wrapper


@bp.route("/logout", methods=["GET"])
def logout():
    # Remove user_id from session object
    # This essentially logs the user out
    session.pop("user_id", None)

    # Redirect to homepage
    return redirect(url_for("home.home"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form["emailusrname"]
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE email_username = ?', (username,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username!!'
        elif check_password_hash(user['password_hash'], password) == False:
            error = 'Incorrect password!!'
        if error is None:
            session['user_id'] = user['id']
        else:
            flash(error, "danger")
        return redirect(url_for("auth.login"))
    else:
        if g.user:
            usertype = g.user['user_type']
            flash("Login successful!", "success")
            if 'h' in usertype:
                return redirect(url_for("householder.dashboard"))
            elif 's' in usertype:
                return redirect(url_for("staff.staff"))
            elif 'a' in usertype:
                return redirect(url_for("admin.admin"))
            else:
                abort(400, "Your account has incorrect privileges. Please contact a system administrator.")
            
        return render_template("./auth-engine/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        if (request.form['username'] != ""):
            username = request.form['username']
        email = request.form['emailaddress']
        password = request.form['password']
        db = get_db()
        error = None
        userid = str(uuid4())
        try:
            if (username != ""):
                db.execute(
                    "INSERT INTO user (id, email_username, password_hash, user_type,display_name) VALUES (?,?,?,?,?)",
                    (userid, email, generate_password_hash(password), "h__", username),
                )
            else:

                db.execute(
                    "INSERT INTO user (id, email_username, password_hash, user_type) VALUES (?,?,?,?)",
                    (userid, email, generate_password_hash(password), "h__"),
                )
            db.commit()
        except db.IntegrityError:
            error = f"Email ID: {email} is already registered."
        else:
            session["user_id"] = userid
            flash("Registration Successful!", "success")
            return redirect(url_for("auth.login"))

        print("Error", error)

    return render_template('./auth-engine/register.html')