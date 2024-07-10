'''Это приложение предназначено для рассчета температурной нагрузки согласно 
СП 20.13330.2016 (изм. 5) и СП 131.13330.2020 (изм.2).
'''

from flask import Blueprint


bp = Blueprint(name="temperature_difference", import_name=__name__)

from app.calc.temperature_difference import routes