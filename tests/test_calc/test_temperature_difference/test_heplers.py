import unittest

import folium

from app.calc.temperature_difference.helpers import (
    get_sp_map_temperatures, t_c_and_t_w_protected_calc, teta_calc, 
    t_c_and_t_w_unprotected_calc, delta_t_calc, generate_map)


class TemperatueDifferenceCase(unittest.TestCase):

    def test_get_sp_map_temperatures(self):
        temperatures_1 = get_sp_map_temperatures(45.5, 44)
        self.assertTrue(-30 < temperatures_1["t_min"] < -25)
        self.assertTrue(38 < temperatures_1["t_max"] < 40)
        self.assertTrue(temperatures_1["A_i"] == 6.6)
        # Внутри полигона
        temperatures_2 = get_sp_map_temperatures(68, 111)
        self.assertTrue(temperatures_2["t_min"] == -55)
        self.assertTrue(30 < temperatures_2["t_max"] < 32)
        self.assertTrue(temperatures_2["A_i"] == 7)
        # Проверка выбора изолиний
        temperatures_3 = get_sp_map_temperatures(56, 47)
        self.assertTrue(-45 < temperatures_3["t_min"] < -40)
        self.assertTrue(32 < temperatures_3["t_max"] < 34)
        self.assertTrue(temperatures_3["A_i"] == 6.9)
        temperatures_4 = get_sp_map_temperatures(66.2, 39.5)
        self.assertTrue(temperatures_4["t_min"] == -30)
        self.assertTrue(temperatures_4["t_max"] == 26)
        self.assertTrue(temperatures_4["A_i"] == 7.3)

    def test_teta_calc(self):
        tetas_1 = teta_calc(45, "steel", 0.5, "horizontal")
        self.assertTrue(15.9775 < tetas_1["teta_4"] < 16.2925)
        tetas_2 = teta_calc(68, "steel", 0.5, "horizontal")
        self.assertAlmostEqual(tetas_2["teta_4"], 12.4425, 4)
        tetas_3 = teta_calc(75, "steel", 0.5, "horizontal")
        self.assertAlmostEqual(tetas_3["teta_4"], 12.4425, 4)
        tetas_4 = teta_calc(38, "steel", 0.5, "horizontal")
        self.assertAlmostEqual(tetas_4["teta_4"], 17.2725, 4)
        tetas_5 = teta_calc(30, "steel", 0.5, "horizontal")
        self.assertAlmostEqual(tetas_5["teta_4"], 17.2725, 4)

    def test_t_c_and_t_w_protected_calc(self):
        sp_map_temperatures = {"A_i": 6, "A_vii": 10.1, "t_i": -7.8, "t_vii": 19.1, "t_min": -35.5, "t_max": 32}
        internal_temperatures = {"t_ic": 19, "t_iw": 21}
        t_c_and_t_w_protected_1 = t_c_and_t_w_protected_calc(sp_map_temperatures, internal_temperatures, "unheated")
        self.assertEqual(t_c_and_t_w_protected_1["t_c"], -32.5)
        self.assertEqual(t_c_and_t_w_protected_1["t_w"], 26.95)
        t_c_and_t_w_protected_2 = t_c_and_t_w_protected_calc(sp_map_temperatures, internal_temperatures, "heated")
        self.assertEqual(t_c_and_t_w_protected_2["t_c"], 19)
        self.assertEqual(t_c_and_t_w_protected_2["t_w"], 26.95)
        t_c_and_t_w_protected_3 = t_c_and_t_w_protected_calc(sp_map_temperatures, internal_temperatures, "heated_and_conditioned")
        self.assertEqual(t_c_and_t_w_protected_3["t_c"], 19)
        self.assertEqual(t_c_and_t_w_protected_3["t_w"], 21)

    def test_t_c_and_t_w_unprotected_calc(self):
        sp_map_temperatures = {"A_i": 6, "A_vii": 10.1, "t_i": -7.8, "t_vii": 19.1, "t_min": -35.5, "t_max": 32}
        internal_temperatures = {"t_ic": 19, "t_iw": 21}
        tetas = teta_calc(48, "steel", 0.5, "west_east")
        t_c_and_t_w_unprotected_1 = t_c_and_t_w_unprotected_calc(sp_map_temperatures, internal_temperatures, "unheated", tetas)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_1["t_c"], -36.5, 2)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_1["t_w"], 48.25, 2)
        t_c_and_t_w_unprotected_2 = t_c_and_t_w_unprotected_calc(sp_map_temperatures, internal_temperatures, "heated", tetas)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_2["t_c"], -14.9, 2)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_2["t_w"], 48.25, 2)
        t_c_and_t_w_unprotected_3 = t_c_and_t_w_unprotected_calc(sp_map_temperatures, internal_temperatures, "heated_and_conditioned", tetas)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_3["t_c"], -14.9, 2)
        self.assertAlmostEqual(t_c_and_t_w_unprotected_3["t_w"], 43.87, 2)

    def test_delta_t_calc(self):
        sp_map_temperatures = {"A_i": 6, "A_vii": 10.1, "t_i": -7.8, "t_vii": 19.1, "t_min": -35.5, "t_max": 32}
        t_c_and_t_w = {"t_c": -32.5, "t_w": 26.95}
        delta_t_1 = delta_t_calc(sp_map_temperatures, t_c_and_t_w)
        self.assertAlmostEqual(delta_t_1["delta_t_c"], -46.22, 2)
        self.assertAlmostEqual(delta_t_1["delta_t_w"], 29.37, 2)

    def test_generate_map(self):
        map_1 = generate_map(zoom_start=5, location=(60, 60), show_layers=True)
        self.assertIsInstance(map_1, folium.Map)


