from flask import Blueprint, render_template

web = Blueprint("web", __name__)


@web.get("/")
def landing_page():
    return render_template("pages/landing.html")


@web.get("/inicio")
def prototype_home_page():
    return render_template("pages/prototype_home.html")
