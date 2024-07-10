import unittest

from app import create_app
from config import Config
from app.calc.temperature_difference.forms import TemperatureDifferenceForm


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

class TemperatueDifferenceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_temperature_difference_get(self):
        response = self.client.get("/calc/temperature-difference/")
        self.assertEqual(response.status_code, 200)

    def test_temperature_difference_post(self):
        # Валидная форма
        response_1 = self.client.post("/calc/temperature-difference/", data={
            "latitude": 60,
            "longitude": 60,
        })
        self.assertEqual(response_1.status_code, 200)
        # Не валидная форма (за пределами границы)
        response_2 = self.client.post("/calc/temperature-difference/", data={
            "latitude": 53.2525,
            "longitude": 67.3420,
        })
        self.assertEqual(response_2.status_code, 200)
        # Валидная форма (с отоплением и кондиционированием)
        response_3 = self.client.post("/calc/temperature-difference/", data={
            "latitude": 60,
            "longitude": 60,
            "internal_climate_type": "heated_and_conditioned",
            "t_ic": 19,
            "t_iw": 21,
        })
        self.assertEqual(response_3.status_code, 200)
        # Валидная форма (не защищенные от солнечной радиации)
        response_4 = self.client.post("/calc/temperature-difference/", data={
            "latitude": 60,
            "longitude": 60,
            "internal_climate_type": "heated_and_conditioned",
            "t_ic": 19,
            "t_iw": 21,
            "solar_protected": False,
            "input_ro": 0.5,
        })
        self.assertEqual(response_4.status_code, 200)


