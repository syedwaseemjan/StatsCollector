import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_DIR)
sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, "app")))
