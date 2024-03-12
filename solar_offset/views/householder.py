from flask import Blueprint, render_template, flash, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from solar_offset.db import get_db
from solar_offset.util import calc_carbon_offset

from math import floor
from uuid import uuid4

bp = Blueprint("householder", __name__)


@bp.route("/")
def home():
    return render_template("householder/home.html")


@bp.route("/householder")
def dashboard():
    username = session.get('username')
    return render_template("householder/householderdashboard.html", username=username)


@bp.route("/about")
def about():
    return "Hello, About!"


@bp.route("/countries")
def country_list():
    db = get_db()
    countries = db.execute(
        "SELECT country.*, COUNT(donation_amount) AS donation_count, SUM(donation_amount) AS donation_sum \
            FROM country LEFT JOIN donation \
            ON (country.country_code == donation.country_code) \
            GROUP BY country.country_code \
            ORDER BY country.name ASC;"
    ).fetchall()

    country_dicts = []
    for c_row in countries:
        cd = dict(c_row)
        if not cd["donation_sum"]:
            cd["donation_sum"] = 0
        cd["carbon_offset"] = floor(calc_carbon_offset(c_row))
        country_dicts.append(cd)

    if "raw" in request.args:
        for cd in country_dicts:
            cd.pop("description")
            cd.pop("electricty_consumption")
            cd.pop("short_code")
        return country_dicts
    else:
        return render_template("householder/country_list.html", countries=country_dicts)
    
@bp.route("/countries/<country_code>")
def country(country_code):
    return country_code


@bp.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
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
            session.clear()
            session['user_id'] = user['id']
            if (user['display_name'] is not None):
                session['username'] = user['display_name']
            else:
                session['username'] = user['email_username']

            usertype = user["user_type"]

            if (usertype == "householder"):
                flash("User login succesfull!", "success")
                return redirect(url_for("householder.dashboard"))
            elif (usertype == "staff"):
                flash("Staff login succesfull!", "success")
                return redirect(url_for("staff.staff"))
            else:
                flash("Admin login succesfull!", "success")
                return redirect(url_for("admin.admin"))

        flash(error, "danger")
    return render_template("login.html")


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
                    (userid, email, generate_password_hash(password), "householder", username),
                )
            else:

                db.execute(
                    "INSERT INTO user (id, email_username, password_hash, user_type) VALUES (?,?,?,?)",
                    (userid, email, generate_password_hash(password), "householder"),
                )
            db.commit()
        except db.IntegrityError:
            error = f"Email ID: {email} is already registered."
        else:
            session.clear()
            session["user_id"] = userid
            if (username != ""):
                session["username"] = username
            else:
                session["username"] = email
            flash("User registered succesfully!", "success")
            return redirect(url_for("householder.dashboard"))

        print("Error", error)

    return render_template('./register.html')
