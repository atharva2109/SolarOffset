from flask import Blueprint, render_template, request, session, redirect
from solar_offset.utils.statistics_util import calculate_statistics

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    # Fetching the statistics
    stats = calculate_statistics()
    # Return the stats to the home.html
    return render_template("./home/home.html", statistics=stats)


@bp.route("/contact-us")
def contact():
    return render_template("./home/contact-us.html")


@bp.route("/faqs")
def faqs():
    return render_template("./home/faqs.html")

@bp.route("/about")
def about():
    return render_template("./home/about.html")