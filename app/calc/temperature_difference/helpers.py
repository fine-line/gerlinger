import os

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import transform
from pyproj import Transformer
from jinja2 import Template
import folium

from app.calc.temperature_difference import bp
import app.calc.temperature_difference.sp_tables as sp_tables
import app.calc.temperature_difference.config as config


def geodesic_to_cartesian(projection: str):
    return Transformer.from_crs(
        crs_from="EPSG:4326", crs_to=projection, always_xy=True).transform

def cartesian_to_geodesic(projection: str):
     return Transformer.from_crs(
         crs_from=projection, crs_to="EPSG:4326", always_xy=True).transform

def gdf_from_json(path_to_json: str, json_crs: str):
    """Функция преобразует GeoJSON в геодатафрейм"""
    gdf = gpd.read_file(os.path.join(bp.root_path, path_to_json))
    gdf.geometry.set_crs(json_crs)
    return gdf

def inside_border(latitude: str, longitude: str):
    """Проверяет находится ли исследуемая точка внутри границы РФ"""
    # Исследуемая точка
    poi = Point(longitude, latitude)
    # Открываем файлы с геоданными, преобразуем в геодатафреймы
    # Граница РФ
    border_gdf = gdf_from_json("geodata/border.geojson", "EPSG:4326")
    projection = config.projection
    poi_cartesian = transform(geodesic_to_cartesian(projection), poi)
    # Находится ли точка внутри границы
    border_series_cartesian = border_gdf["geometry"].to_crs(projection)
    if border_series_cartesian.contains(poi_cartesian).sum() == 0:
        return False
    else:
        return True

def sp_20_map_temp_interpolation(
        point: Point, geodataframe: gpd.GeoDataFrame, projection: str):
    """Функция находит нормативную температуру по картам 4 и 5 СП20"""
    # Проекция на плоскость
    geoseries = geodataframe["geometry"].to_crs(projection)
    point_cartesian = transform(geodesic_to_cartesian(projection), point)
    # Если точка находится в одном из полигонов, то взять температуру полигона,
    # иначе взять среднее взвешенное между двумя ближайшими изолиниями
    polygons = geoseries[geoseries.geom_type=="Polygon"]
    polygons_containing_poi = polygons[polygons.contains(point_cartesian)]
    if not polygons_containing_poi.empty:
        index = polygons_containing_poi.index[0]
        return geodataframe.loc[index]["temperature"]
    else:
        # Находим кратчайшие отрезки от точки до каждой изолинии
        shortest_lines = geoseries.shortest_line(point_cartesian)
        # Рассчитываем их длину и сортируем
        shortest_lines_length_sorted = shortest_lines.length.sort_values()
        # Выбираем первый отрезок
        first_line_index = shortest_lines_length_sorted.index[0]
        # Выбираем второй отрезок из условия, 
        # что он не должен пересекаться с другими изолиниями
        second_line_index = first_line_index
        for index in shortest_lines_length_sorted.index[1:]:
            number_of_crosses = geoseries.crosses(shortest_lines.loc[index]).sum()
            if number_of_crosses == 0:
                second_line_index = index
                break
        # Вычисляем среднее взвешенное
        temp_1 = geodataframe.loc[first_line_index]["temperature"]
        temp_2 = geodataframe.loc[second_line_index]["temperature"]
        if shortest_lines_length_sorted.loc[first_line_index] == 0:
            return temp_1
        elif shortest_lines_length_sorted.loc[second_line_index] == 0:
            return temp_2
        else:
            len_1 = 1 / shortest_lines_length_sorted.loc[first_line_index]
            len_2 = 1 / shortest_lines_length_sorted.loc[second_line_index]
            weighted_average_temp = ((temp_1 * len_1 + temp_2 * len_2) 
                                     / (len_1 + len_2))
            return weighted_average_temp

def get_sp_map_temperatures(latitude: str, longitude: str):
    """Находит величины нормативных температур по картам СП20 и СП131"""
    # Исследуемая точка
    poi = Point(longitude, latitude)
    # Открываем файлы с геоданными, преобразуем в геодатафреймы
    # Карта нормативных отрицательных температур
    sp_20_map_4_gdf = gdf_from_json("geodata/sp_20_map_4.geojson", "EPSG:4326")
    # Карта нормативных положительных температур
    sp_20_map_5_gdf = gdf_from_json("geodata/sp_20_map_5.geojson", "EPSG:4326")
    # Карта метеостанций из СП 131
    sp_131_gdf = gdf_from_json("geodata/sp_131_tables_for_sp_20.geojson", 
                               "EPSG:4326")
    projection = config.projection
    poi_cartesian = transform(geodesic_to_cartesian(projection), poi)
    # Находим ближайшую метеостанцию по СП 131
    sp_131_series_cartesian = sp_131_gdf["geometry"].to_crs(projection)
    index = sp_131_series_cartesian.distance(poi_cartesian).idxmin()
    nearest_meteostation = sp_131_gdf.loc[index]
    A_i = nearest_meteostation["average daily air temperature range of the coldest month"]
    A_vii = nearest_meteostation["average daily air temperature range of the warmest month"]
    t_i = nearest_meteostation["average monthly temperature in January"]
    t_vii = nearest_meteostation["average monthly temperature in July"]
    # Интерполируем значения температуры по картам СП 20
    t_min = sp_20_map_temp_interpolation(poi, sp_20_map_4_gdf, projection)
    t_max = sp_20_map_temp_interpolation(poi, sp_20_map_5_gdf, projection)

    return {"A_i": A_i, 
            "A_vii": A_vii, 
            "t_i": t_i, 
            "t_vii": t_vii,
            "t_min": t_min,
            "t_max": t_max
            }

def t_ec_calc(t_min, A_i):
    t_ec = t_min + 0.5 * A_i
    return t_ec

def t_ew_calc(t_max, A_vii):
    t_ew = t_max - 0.5 * A_vii
    return t_ew

def t_c_and_t_w_protected_calc(sp_map_temperatures: dict, 
                               internal_temperatures: dict,
                               internal_climate_type: str):
    """Рассчитывает значения нормативных температур 
    для теплого и холодного времени года для конструкций, 
    защищиенных от солнечной радиации
    """
    t_min = sp_map_temperatures["t_min"]
    t_max = sp_map_temperatures["t_max"]
    A_i = sp_map_temperatures["A_i"]
    A_vii = sp_map_temperatures["A_vii"]
    t_ic = internal_temperatures["t_ic"]
    t_iw = internal_temperatures["t_iw"]
    t_ec = t_ec_calc(t_min, A_i)
    t_ew = t_ew_calc(t_max, A_vii)
    if internal_climate_type == "unheated":
        t_c = t_ec
        t_w = t_ew
    elif internal_climate_type == "heated":
        t_c = t_ic
        t_w = t_ew
    else:
        t_c = t_ic
        t_w = t_iw
    return {"t_ec": t_ec, "t_ew": t_ew, "t_c": t_c, "t_w": t_w}

def teta_calc(latitude: float, structure_type: str, ro: float, orientation: str):
    """Рассчитывает значения приращений температуры тета"""
    teta_1 = sp_tables.temperature_increments[structure_type]["teta_1"]
    teta_2 = sp_tables.temperature_increments[structure_type]["teta_2"]
    teta_3 = sp_tables.temperature_increments[structure_type]["teta_3"]
    k = sp_tables.temperature_increments[structure_type]["k"]
    S_max = np.interp(latitude, sp_tables.solar_radiation["latitude"], 
                      sp_tables.solar_radiation["orientations"][orientation]).item()
    teta_4 = 0.05 * ro * S_max * k
    teta_5 = 0.05 * ro * S_max * (1 - k)
    return {"teta_1": teta_1, 
            "teta_2": teta_2, 
            "teta_3": teta_3, 
            "teta_4": teta_4, 
            "teta_5": teta_5
            }

def t_c_and_t_w_unprotected_calc(sp_map_temperatures: dict, 
                                 internal_temperatures: dict,
                                 internal_climate_type: str,
                                 tetas: dict):
    """Рассчитывает значения нормативных температур 
    для теплого и холодного времени года для конструкций, 
    не защищиенных от солнечной радиации
    """
    t_min = sp_map_temperatures["t_min"]
    t_max = sp_map_temperatures["t_max"]
    A_i = sp_map_temperatures["A_i"]
    A_vii = sp_map_temperatures["A_vii"]
    t_ic = internal_temperatures["t_ic"]
    t_iw = internal_temperatures["t_iw"]
    t_ec = t_ec_calc(t_min, A_i)
    t_ew = t_ew_calc(t_max, A_vii)
    teta_1 = tetas["teta_1"]
    teta_2 = tetas["teta_2"]
    teta_3 = tetas["teta_3"]
    teta_4 = tetas["teta_4"]
    teta_5 = tetas["teta_5"]
    if internal_climate_type == "unheated":
        t_c = t_ec - 0.5 * teta_1
        t_w = t_ew + teta_1 + teta_4
    elif internal_climate_type == "heated":
        t_c = t_ic + 0.6 * (t_ec - t_ic) - 0.5 * teta_2
        t_w = t_ew + teta_1 + teta_4
    else:
        t_c = t_ic + 0.6 * (t_ec - t_ic) - 0.5 * teta_2
        t_w = t_iw + 0.6 * (t_ew - t_iw) + teta_2 + teta_4
    return {"t_ec": t_ec, "t_ew": t_ew, "t_c": t_c, "t_w": t_w}

def delta_t_calc(sp_map_temperatures: dict,
                 t_c_and_t_w: dict,):
    """Рассчитывает нормативные значения температурной нагрузки"""
    t_i = sp_map_temperatures["t_i"]
    t_vii = sp_map_temperatures["t_vii"]
    t_c = t_c_and_t_w["t_c"]
    t_w = t_c_and_t_w["t_w"]
    t_0c = 0.2 * t_vii + 0.8 * t_i
    t_0w = 0.8 * t_vii + 0.2 * t_i
    delta_t_c = t_c - t_0w
    delta_t_w = t_w - t_0c
    return {"t_0c": t_0c, 
            "t_0w": t_0w, 
            "delta_t_c": delta_t_c, 
            "delta_t_w": delta_t_w
            }

def generate_map(zoom_start: int, location: tuple, show_layers: bool):
    # Карта нормативных отрицательных температур
    sp_20_map_4_gdf = gdf_from_json("geodata/sp_20_map_4.geojson", "EPSG:4326")
    # Карта нормативных положительных температур
    sp_20_map_5_gdf = gdf_from_json("geodata/sp_20_map_5.geojson", "EPSG:4326")
    # Карта метеостанций из СП 131
    sp_131_gdf = gdf_from_json("geodata/sp_131_tables_for_sp_20.geojson", 
                               "EPSG:4326")
    map = folium.Map(
        location=location, zoom_start=zoom_start, min_zoom=2, zoom_control=False)
    sp_20_map_4_gdf.explore(
        m=map, column="temperature", legend=False, tooltip="temperature", 
        name="Карта 4", show=show_layers, style_kwds={"fillOpacity": 0.1})
    sp_20_map_5_gdf.explore(
        m=map, column="temperature", legend=False, tooltip="temperature", 
        name="Карта 5", show=show_layers, style_kwds={"fillOpacity": 0.1})
    sp_131_gdf.explore(
        m=map, column="average monthly temperature in July", legend=False, 
        name="СП 131", show=show_layers)
    folium.LayerControl().add_to(map)
    return map

class GetLatLngPopup(folium.LatLngPopup):
    """Кастомный класс для извлечения широты и долготы с folium карты
    Добавлены 2 строки "parent.document.getElementById.....
    Увеличена точность до 6 знаков (вместо 4)
    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Широта: " + e.latlng.lat.toFixed(4) +
                                    "<br>Долгота: " + e.latlng.lng.toFixed(4))
                        .openOn({{this._parent.get_name()}});
                        parent.document.getElementById("longitude").value = e.latlng.lng.toFixed(6);
                        parent.document.getElementById("latitude").value = e.latlng.lat.toFixed(6);
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)

    def __init__(self):
        super(GetLatLngPopup, self).__init__()
        self._name = "GetLatLngPopup"





















