from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import sessionmaker
from .config import settings
import psycopg2
import time


SQLALCHEMY_DATABASE_URL = (
    f'postgresql://{settings.database_user}:'
    f'{settings.database_password}@'
    f'{settings.database_host}:'
    f'{settings.database_port}/'
    f'{settings.database_name}'
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


while True:
    try:
        connection = psycopg2.connect(
            host = 'localhost', 
            database = 'fastapi', 
            user = 'postgres', 
            password = 'MA7MOUD7EFNY.',
            cursor_factory = RealDictCursor
        )
        cursor = connection.cursor()
        print("Connected successfully")
        break
    
    except Exception as error:
        print("Unable to connect")
        print("Error: ", error)
        time.sleep(2)
