import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.DEBUG)

from app import app, init_db

try:
    init_db()
except Exception as e:
    logging.error(f"init_db failed: {e}")