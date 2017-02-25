import logging
import socket
import xml.etree.ElementTree as ET

from models import Stats

from app.tasks import upload_collector

logger = logging.getLogger()


class Main(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        # create a file handler
        handler = logging.FileHandler("server.log")
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter(
            "[%(asctime)s: %(levelname)s/%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(handler)
        logging.getLogger("paramiko").addHandler(handler)

    def parse_client(self, client):
        """Parse the XML Element object and returns back dictionary.

        Attributes:
                client (XMLELement): Client information from clients.xml
        """
        logger.info(
            "IP: %s, Port: %s, Username: %s",
            client.get("ip"),
            client.get("port"),
            client.get("username"),
        )
        ip = client.get("ip")
        port = int(client.get("port"))
        email = client.get("mail")
        username = client.get("username")
        password = client.get("password")
        cpu_threshold = client.find("alert[@type='memory']").attrib["limit"]
        mem_threshold = client.find("alert[@type='cpu']").attrib["limit"]

        return {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password,
            "cpu_threshold": float(cpu_threshold[:-1]),
            "mem_threshold": float(mem_threshold[:-1]),
            "email": email,
        }

    def process_clients(self, file_path):
        """This method is used to parse the clients.xml and provides the IP,
        PORT, USERNAME, PASSWORD and EMAIL to upload_collector

        Attributes:
                file_path (str): path for clients.xml
        """
        logger.info(f"Clients file path: {file_path}")

        logger.info("Started parsing clients file")
        try:
            tree = ET.parse(file_path)
        except (ET.ParseError, FileNotFoundError) as exe:
            logger.exception(exe)
            return False

        try:
            root = tree.getroot()
            for client in root.findall("client"):
                data = self.parse_client(client)
                stats = Stats.get_or_create(**data)
                Stats.save(stats)
                upload_collector.delay(
                    data["ip"], data["port"], data["username"], data["password"]
                )
        except socket.error as e:
            logger.exception(f"Rabbitmq is not accessible. {e}")
            return False
