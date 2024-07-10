from flask import render_template
import folium
# import branca

import app.calc.temperature_difference.sp_tables as sp_tables
from app.calc.temperature_difference import bp
from app.calc.temperature_difference.forms import TemperatureDifferenceForm
from app.calc.temperature_difference.helpers import (
    get_sp_map_temperatures, teta_calc, t_c_and_t_w_unprotected_calc,
    t_c_and_t_w_protected_calc, delta_t_calc, generate_map, GetLatLngPopup)


@bp.route("/", methods=["GET", "POST"])
def index():
    form = TemperatureDifferenceForm()

    # POST
    if form.validate_on_submit():
        # Собираем данные из формы, генерируем карту
        poi_latitude = float(form.latitude.data)
        poi_longitude = float(form.longitude.data)
        internal_temperatures = {
            "t_ic": float(form.t_ic.data) if form.t_ic.data is not None else None,
            "t_iw": float(form.t_iw.data) if form.t_iw.data is not None else None
            }
        internal_climate_type = form.internal_climate_type.data
        solar_protected = form.solar_protected.data
        sp_map_temperatures = get_sp_map_temperatures(poi_latitude, poi_longitude)
        map = generate_map(zoom_start=5, location=(poi_latitude, poi_longitude), show_layers=True)
        map.add_child(folium.Marker(location=[poi_latitude, poi_longitude]))
        map_iframe = folium.Figure(height=400).add_child(map)._repr_html_()
        if solar_protected:
            # Если конструкции защищены от солнечной радиации
            t_c_and_t_w = t_c_and_t_w_protected_calc(
                sp_map_temperatures, internal_temperatures, internal_climate_type)
            delta_t = delta_t_calc(sp_map_temperatures, t_c_and_t_w)
            return render_template("temperature_difference/result.html",
                                   latitude=float(form.latitude.data),
                                   longitude=float(form.longitude.data),
                                   sp_map_temperatures=sp_map_temperatures,
                                   internal_temperatures=internal_temperatures,
                                   internal_climate_type=internal_climate_type,
                                   solar_protected=solar_protected,
                                   t_c_and_t_w=t_c_and_t_w,
                                   delta_t=delta_t,
                                   map_iframe=map_iframe,
                                   title="Температурная нагрузка")
        else:
            # Если конструкции не защищены от солнечной радиации
            structure_type = form.structure_type.data
            structure_type_alias = sp_tables.temperature_increments[structure_type]["alias"]
            if form.input_ro.data is not None:
                ro = float(form.input_ro.data)
            else:
                ro = form.select_ro.data
            # Вычисление для каждой ориентации
            orientations = sp_tables.solar_radiation["orientations"].keys()
            t_c_and_t_w_orientation = {}
            delta_t_orientation = {}
            for orientation in orientations:
                tetas = teta_calc(poi_latitude, structure_type, ro, orientation)
                t_c_and_t_w = t_c_and_t_w_unprotected_calc(
                    sp_map_temperatures, internal_temperatures, 
                    internal_climate_type, tetas)
                t_c_and_t_w_orientation[orientation] = t_c_and_t_w
                delta_t = delta_t_calc(sp_map_temperatures, t_c_and_t_w)
                delta_t_orientation[orientation] = delta_t
            return render_template("temperature_difference/result.html",
                                   latitude=float(form.latitude.data),
                                   longitude=float(form.longitude.data),
                                   sp_map_temperatures=sp_map_temperatures,
                                   internal_temperatures=internal_temperatures,
                                   internal_climate_type=internal_climate_type,
                                   solar_protected=solar_protected,
                                   structure_type=structure_type_alias,
                                   ro=ro,
                                   orientations=orientations,
                                   t_c_and_t_w=t_c_and_t_w_orientation,
                                   delta_t=delta_t_orientation,
                                   map_iframe=map_iframe,
                                   title="Температурная нагрузка")

    # GET
    map = generate_map(zoom_start=3, location=(65.66, 95.99), show_layers=False)
    map.add_child(GetLatLngPopup())
    map_iframe = map.get_root()._repr_html_()
    return render_template("temperature_difference/index.html", 
                           title="Температурная нагрузка",
                           map_iframe=map_iframe,
                           form=form)


























    

