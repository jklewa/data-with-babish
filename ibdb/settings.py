import os

IBDB_URL = os.environ.get('IDDB_URL', 'ibdb://data-with-babish.jklewa.github.com')
IBDB_SQLFILE = os.environ.get('IBDB_SQLFILE', 'ibdb/db_dump.sql')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'datasets/')

DB_USERNAME = os.environ.get('POSTGRES_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.environ.get('POSTGRES_DBNAME', 'babish_db')
DB_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'db')
DB_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))


class FlaskConfig(object):
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
