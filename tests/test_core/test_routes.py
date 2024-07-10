import unittest

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True

class TestCoreCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_index_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_calc_endpoint(self):
        response = self.client.get("/calc")
        self.assertEqual(response.status_code, 200)
