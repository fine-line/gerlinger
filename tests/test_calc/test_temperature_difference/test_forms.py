import unittest

from app import create_app
from config import Config
from app.calc.temperature_difference.forms import TemperatureDifferenceForm


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

class TestFormCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_form_default_validate(self):
        form_1 = TemperatureDifferenceForm(latitude=60, longitude=60)
        self.assertTrue(form_1.validate())
        self.assertEqual(form_1.internal_climate_type.data, "unheated")
        self.assertEqual(form_1.t_ic.data, None)
        self.assertEqual(form_1.t_iw.data, None)
        self.assertEqual(form_1.solar_protected.data, True)
        self.assertEqual(form_1.structure_type.data, "steel")
        self.assertEqual(form_1.select_ro.data, 0.45)
        self.assertEqual(form_1.input_ro.data, None)

        form_2 = TemperatureDifferenceForm()
        self.assertFalse(form_2.validate())

    def test_form_inside_border_validate(self):
        form_1 = TemperatureDifferenceForm(latitude=53.2525, longitude=67.3420)
        self.assertFalse(form_1.validate())
        form_2 = TemperatureDifferenceForm(latitude=44.4384, longitude=134.2271)
        self.assertTrue(form_2.validate())
        form_3 = TemperatureDifferenceForm(latitude=80.6139, longitude=60.6961)
        self.assertTrue(form_3.validate())
        form_4 = TemperatureDifferenceForm(latitude=54.7610, longitude=21.3368)
        self.assertTrue(form_4.validate())

    def test_form_internal_climate_validate(self):
        form_1 = TemperatureDifferenceForm(latitude=60, longitude=60, internal_climate_type="heated")
        self.assertFalse(form_1.validate())
        form_2 = TemperatureDifferenceForm(latitude=60, longitude=60, internal_climate_type="heated", t_ic=19)
        self.assertTrue(form_2.validate())
        form_3 = TemperatureDifferenceForm(latitude=60, longitude=60, internal_climate_type="heated_and_conditioned", t_ic=19)
        self.assertFalse(form_3.validate())
        form_4 = TemperatureDifferenceForm(latitude=60, longitude=60, internal_climate_type="heated_and_conditioned", t_ic=19, t_iw=21)
        self.assertTrue(form_4.validate())

    def test_form_ro_validate(self):
        form_1 = TemperatureDifferenceForm(latitude=60, longitude=60, solar_protected=False, select_ro=None, input_ro=None)
        self.assertFalse(form_1.validate())
        form_2 = TemperatureDifferenceForm(latitude=60, longitude=60, solar_protected=False, select_ro=None, input_ro=0.5)
        self.assertTrue(form_2.validate())