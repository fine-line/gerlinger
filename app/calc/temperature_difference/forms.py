from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, NumberRange, Optional

from app.calc.temperature_difference.helpers import inside_border
import app.calc.temperature_difference.sp_tables as sp_tables


def coerce_none(value):
    # Функция для преобразования значений поля SelectField
    if value == "None":
        return None
    return float(value)

def coerce_bool(value):
    if isinstance(value, str):
        return value == "True" if value != "None" else None
    else:
        return bool(value) if value is not None else None

class TemperatureDifferenceForm(FlaskForm):
    latitude = DecimalField(
        "Широта", validators=[DataRequired("Обязательное поле")])

    longitude = DecimalField(
        "Долгота", validators=[DataRequired("Обязательное поле")])
    
    t_iw = DecimalField(
        "Температура внутреннего воздуха в теплое время года (по ТЗ)", 
        validators=[Optional()])
    
    t_ic = DecimalField(
        "Температура внутреннего воздуха в холодное время года (по ТЗ)", 
        validators=[Optional()])
    
    internal_climate_type = RadioField(
        "Тип здания",
        choices=[
            ("unheated", "Неотапливаемые здания и открытые сооружения"),
            ("heated", "Отапливаемые здания"),
            ("heated_and_conditioned", "Здания с искусственным климатом")
            ],
        default="unheated")
    
    solar_protected = RadioField(
        "Тип конструкций",
        choices=[
            (True, "Защищенные от воздействия солнечной радиации"),
            (False, "Не защищенные от воздействия солнечной радиации")
            ],
        coerce=coerce_bool,
        default=True)
    
    materials = []
    for key, value in sp_tables.temperature_increments.items():
        materials.append((key, value["alias"]))
    structure_type = RadioField(
        "Материал конструкций", choices=materials, default="steel")
    
    ro = []
    for key, value in sp_tables.ro.items():
        ro.append((value, key))
    select_ro = SelectField(
        "Материал наружной поверхности ограждающих конструкций", 
        choices = ro + [("None", "Другой материал")], 
        coerce=coerce_none,
        default=0.45)
    input_ro = DecimalField(
        "Коэффициент поглощения солнечной радиации", 
        validators=[
            NumberRange(min=0.1, max=1.0, message="Введите число между 0,1 и 1,0"),
            Optional()
            ])

    submit = SubmitField("Рассчитать")

    # Дополнительные валидаторы
    def validate(self, **kwargs):
        errors_occured = False

        if not FlaskForm.validate(self):
            errors_occured = True
        if FlaskForm.validate(self) and not inside_border(self.latitude.data, self.longitude.data):
            self.submit.errors.append("Точка должна находиться в пределах сухопутной границы РФ")
            errors_occured = True
        if (self.internal_climate_type.data == "heated") and (self.t_ic.data is None):
            self.t_ic.errors.append("Обязательное поле")
            errors_occured = True
        if (self.internal_climate_type.data == "heated_and_conditioned") and (self.t_ic.data is None):
            self.t_ic.errors.append("Обязательное поле")
            errors_occured = True
        if (self.internal_climate_type.data == "heated_and_conditioned") and (self.t_iw.data is None):
            self.t_iw.errors.append("Обязательное поле")
            errors_occured = True
        if (self.solar_protected.data == False) and (self.select_ro.data is None) and (self.input_ro.data is None):
            self.input_ro.errors.append("Введите значение или выберите из списка")
            errors_occured = True

        if errors_occured:
            return False
        else:
            return True

