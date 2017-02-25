import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_DIR)
sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, "app")))


from unittest import TestCase  # noqa
from app import settings  # noqa

settings.load_settings(env="test")


class StatsCollectorAppTestCase(TestCase):
    """StatsCollectorAppTestCase is not doing anything special
    but we can place any common functionality in it in future
    if we want to add more tests.
    """

    def setUp(self):
        super(StatsCollectorAppTestCase, self).setUp()

    def tearDown(self):
        super(StatsCollectorAppTestCase, self).tearDown()
