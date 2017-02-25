import os
import xml.etree.ElementTree as ET
from unittest.mock import patch

from app.main import Main
from app.models import Stats
from app.tasks import check_threshold, get_message_text, get_subject_text

from . import StatsCollectorAppTestCase


class ServerTestCase(StatsCollectorAppTestCase):
    """
    ServerTestCase constains all unit tests for StatsCollector App.
    """

    def setUp(self):
        super(ServerTestCase, self).setUp()

    def get_client_nodes(self):
        clients_list = os.path.join(os.path.dirname(__file__), "clients.xml")
        tree = ET.parse(clients_list)
        root = tree.getroot()
        return root.findall("client")

    def test_process_clients_wrong_file_path(self):
        self.assertFalse(Main().process_clients("wrong_path"))

    def test_process_clients_file_incorrect_syntax(self):
        clients_list = os.path.join(os.path.dirname(__file__), "clients_incorrect.xml")
        self.assertFalse(Main().process_clients(clients_list))

    def test_parse_client(self):
        clients = self.get_client_nodes()
        self.assertEqual(1, len(clients))
        data = Main().parse_client(clients[0])
        self.assertEqual(type({}), type(data))
        self.assertEqual(data["ip"], "11.11.11.11")
        self.assertEqual(data["port"], 22)
        self.assertEqual(data["username"], "test_username")
        self.assertEqual(data["password"], "test_password")
        self.assertEqual(data["email"], "test_email")
        self.assertEqual(data["cpu_threshold"], 50.0)
        self.assertEqual(data["mem_threshold"], 20.0)

    def test_get_or_create(self):
        clients = self.get_client_nodes()
        data = Main().parse_client(clients[0])
        stats = Stats.get_or_create(**data)
        self.assertEqual(stats.ip, "11.11.11.11")

    def test_get_subject_text(self):
        text = get_subject_text("CPU")
        self.assertEqual("Alert for your instance's CPU usage", text)

    def test_get_message_text(self):
        text = get_message_text("CPU", 50, 32)
        self.assertIn("CPU threshold: 50%", text)

    def test_check_threshold(self):
        clients = self.get_client_nodes()
        data = Main().parse_client(clients[0])
        stats = Stats.get_or_create(**data)

        with patch("app.tasks.send_email.delay"):
            data = Main().parse_client(clients[0])
            stats.cpu_usage = 18
            stats.mem_usage = 55
            cpu_alert, mem_alert = check_threshold(stats)

        self.assertEqual(cpu_alert, False)
        self.assertEqual(mem_alert, True)
