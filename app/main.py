# -*- coding: utf-8 -*-

# Copyright (C) 2003-2007  Waseem Ullah <syedwaseemjan@gmail.com>
#
# This is the entry point for our application. User is supposed to run 
# 	 $ python server.py
# inside app folder to start the whole process.
#
# Server.py is free script; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Server.py is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Server.py; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

import os, logging
import paramiko
import config
import xml.etree.ElementTree as ET
from models import get_or_create, save
from tasks import upload_collector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('app/server.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
paramiko.util.log_to_file('ssh.log')

def parse_client(client):
	"""Parse the XML Element object and returns back dictionary.

	Attributes:
		client (XMLELement): Client information from clients.xml
	"""
	logger.info('IP: %s, Port: %s, Username: %s, Password: %s',
				client.get('ip'), client.get('port'), client.get('username'), client.get('password'))
	ip = client.get('ip')
	port = int(client.get('port'))
	email = client.get('mail')
	username = client.get('username')
	password = client.get('password')
	cpu_threshold =client.find("alert[@type='memory']").attrib["limit"]
	mem_threshold =client.find("alert[@type='cpu']").attrib["limit"]

	return {
		"ip": ip,
		"port": port,
		"username" : username,
		"password" : password,
		"cpu_threshold": float(cpu_threshold[:-1]),
		"mem_threshold": float(mem_threshold[:-1]),
		"email" : email
	}

def process_clients(file_path):
	"""This method is used to parse the clients.xml and provides the IP, 
	PORT, USERNAME, PASSWORD and EMAIL to upload_collector

	Attributes:
		config (dict): application configurations
		file_path (str): path for clients.xml
	"""
	logger.info('Config file path: %s' % file_path)

	logger.info('Start parsing clients file')
	try:
		tree = ET.parse(file_path)
		root = tree.getroot()
		for client in root.findall('client'):
			data = parse_client(client)
			stats = get_or_create(**data)
			save(stats, "Stats record for ip: %s successfully added." % data["ip"])
			upload_collector.delay(data["ip"], data["port"], data["username"], data["password"])
	except IOError as e:
		logger.exception(e)
		raise e
	except ET.ParseError as e:
		logger.exception(e)
		raise e

if __name__ == '__main__':
	clients_list = os.path.join(os.path.dirname(__file__), 'clients.xml')
	process_clients(clients_list)






