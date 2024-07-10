from flask import Blueprint


bp = Blueprint(name="core", import_name=__name__)

from app.core import routes