#! /usr/bin/env python
import _mypath
import os

from main import process_clients

clients_list = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/clients.xml'))
process_clients(clients_list)