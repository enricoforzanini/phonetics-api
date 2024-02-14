import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'data.db')

limiter = Limiter(key_func=get_remote_address)
