from flask import Blueprint, g, render_template, flash, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from solar_offset.db import get_db
from solar_offset.utils.carbon_offset_util import calc_carbon_offset
from solar_offset.utils.statistics_util import calculate_statistics

from math import floor
from uuid import uuid4

bp = Blueprint("householder", __name__)


@bp.route("/householder")
def dashboard():
    username = session.get('username')
    stats = calculate_statistics()
    is_logged_in = True if username else False
    if is_logged_in == False:
        return redirect("/login")
    return render_template("./users/householder/householderdashboard.html", username=username,
                           is_logged_in=is_logged_in,statistics=stats)


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
        return render_template("./users/householder/country_list.html", countries=country_dicts)


@bp.route("/countries/<country_code>")
def country(country_code):
    country_code = str(country_code).upper()

    db = get_db()
    country = db.execute("SELECT * FROM country WHERE country_code == ?", [country_code]).fetchone()
    country = dict(country)
    country["descriptions"] = [d.strip() for d in country["description"].split(r"\n")]

    # If country doesn't exist in database, redirect to countries view
    if country is None:
        return redirect(url_for('householder.country_list'))

    lst_orga = db.execute("SELECT * FROM organization WHERE country_code == ?", [country_code]).fetchall()
    lst_orga = [dict(orga) for orga in lst_orga]
    for orga in lst_orga:
        orga["descriptions"] = [d.strip() for d in orga["description"].split(r"\n")]

    return render_template(
        "./users/householder/projects.html",
        country=country,
        organizations=lst_orga)
