"""Core configuration module"""

import os 

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:userpassword@db/fastapi_db")