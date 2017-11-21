#! /usr/bin/env python
import os
import _mypath
from app.main import Main

clients_list = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../app/clients.xml'))
Main().process_clients(clients_list)
