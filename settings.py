import aiohttp
import psycopg2
import os
from dotenv import load_dotenv

def init(**kwargs):
    global CORE_URL
    global DB_DSN
    global conn
    global http_client
    
    load_dotenv()
    
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PORT = os.getenv("DB_PORT")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    DB_DSN = (f"host='{DB_HOST}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASSWORD}' port={DB_PORT}")
    CORE_URL = os.getenv("CORE_URL")

    conn = psycopg2.connect(DB_DSN)
    http_client = aiohttp.ClientSession()
    