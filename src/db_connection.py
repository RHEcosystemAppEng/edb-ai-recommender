import psycopg2
import os
import logging

def get_db_connection_string():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

    postgres_host_port = os.getenv("EDB_AIDB_PORT")
    postgres_host_port = postgres_host_port.replace("tcp://", "")
    postgres_host_port = postgres_host_port.replace("http://", "")
    
    postgres_user = os.getenv("DATABASE_USER")
    postgres_pwd = os.getenv("DATABASE_PASSWORD")
    postgres_db_name = os.getenv("DATABASE_NAME")

    postgres_uri = f"postgresql://{postgres_user}:{postgres_pwd}@{postgres_host_port}/{postgres_db_name}"

    logging.info(f"HERE!!!{postgres_uri}")

    return postgres_uri

def create_db_connection():

    postgres_uri = get_db_connection_string()
    
    conn = psycopg2.connect(postgres_uri)

    return conn