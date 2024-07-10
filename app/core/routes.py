from flask import render_template

from app.core import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("core/index.html", title="Home")

@bp.route("/calc")
def calculators():
    return render_template("core/calculators.html", title="Калькуляторы")

