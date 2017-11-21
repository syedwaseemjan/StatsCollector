# -*- coding: utf-8 -*-
"""
    tests
    ~~~~~
    tests package
"""
from unittest import TestCase

from app import settings
settings.load_settings(env="test")


class StatsCollectorAppTestCase(TestCase):
    """ StatsCollectorAppTestCase is not doing anything special
    but we can place any common functionality in it in future
    if we want to add more tests.
    """

    def setUp(self):
        super(StatsCollectorAppTestCase, self).setUp()

    def tearDown(self):
        super(StatsCollectorAppTestCase, self).tearDown()
