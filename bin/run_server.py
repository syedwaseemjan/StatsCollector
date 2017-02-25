#! /usr/bin/env python

from __future__ import absolute_import

import os
import _mypath  # noqa

if __name__ == "__main__":
    from app.main import Main

    clients_list = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../app/clients.xml")
    )
    Main().process_clients(clients_list)
