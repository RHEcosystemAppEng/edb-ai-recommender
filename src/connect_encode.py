import pandas as pd
import psycopg2
import time
import os
import boto3, botocore

from io import StringIO
from typing import Tuple, List

from psycopg2.extras import execute_batch
from psycopg2 import sql

from db_connection import create_db_connection
from s3_connection import get_s3_connection_profile


def initialize_database(conn):
    """Initialize the database with required extensions and tables."""
    with conn.cursor() as cur:
        _create_extensions(cur)
        _create_tables(cur)
        # _populate_test_images_data(cur, '/dataset/images')


def _create_extensions(cur):
    """Create required extensions if they do not exist."""
    cur.execute("CREATE EXTENSION IF NOT EXISTS aidb cascade;")
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgfs;")


def _create_tables(cur):
    """Create required tables."""
    # Drop tables if they exist
    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute("DROP TABLE IF EXISTS product_review;")
    # Create products table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            img_id TEXT,
            gender VARCHAR(50),
            masterCategory VARCHAR(100),
            subCategory VARCHAR(100),
            articleType VARCHAR(100),
            baseColour VARCHAR(50),
            season TEXT,
            year INTEGER,
            usage TEXT NULL,
            productDisplayName TEXT NULL
        );
    """)
    # Create product_review table
    cur.execute(
        """CREATE TABLE IF NOT EXISTS product_review(
            user_id TEXT,
            product_id TEXT,
            rating INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review TEXT
    );"""
    )
    

def populate_product_data(conn: psycopg2.extensions.connection, csv_file: str
) -> None:
    """
    Populate the products table with data from the CSV file.
    Args:
        conn (psycopg2.extensions.connection): PostgreSQL connection object.
        csv_file (str): Path to the CSV file containing product data.
    """
    # Create a string buffer
    # Read the train.csv file into a pandas dataframe, skipping bad lines
    df = pd.read_csv(csv_file, on_bad_lines="skip")
    output = StringIO()
    df_copy = df.copy()
    # Drop rows where any column value is empty
    df_copy = df_copy.dropna()
    # Convert year to integer if it's not already
    df_copy["year"] = df_copy["year"].astype("Int64")

    # Replace NaN with None for proper NULL handling in PostgreSQL
    df_copy = df_copy.replace({pd.NA: None, pd.NaT: None})
    df_copy = df_copy.where(pd.notnull(df_copy), None)
    print("Starting to populate products table")
    # Convert DataFrame to csv format in memory
    tuples: List[Tuple] = [tuple(x) for x in df_copy.to_numpy()]
    cols_list: List[str] = list(df_copy.columns)
    cols: str = ",".join(cols_list)
    placeholders: str = ",".join(
        ["%s"] * len(cols_list)
    )  # Create the correct number of placeholders
    # Create a parameterized query
    query: sql.SQL = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier("products"), sql.SQL(cols), sql.SQL(placeholders)
    )
    cursor: psycopg2.extensions.cursor = conn.cursor()
    try:
        execute_batch(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while inserting data into PostgreSQL: {error}")
        conn.rollback()

    # Commit and close
    conn.commit()
    print("Finished populating products table")

def insert_dataframe(
    df: pd.DataFrame, table_name: str, connection: psycopg2.extensions.connection
) -> None:
    """
    Insert product_review data into the PostgreSQL table.
    Args:
        df (pd.DataFrame): DataFrame containing the data to be inserted.
        table_name (str): Name of the target table in PostgreSQL.
        connection (psycopg2.extensions.connection): PostgreSQL connection object.
    """
    if pd.api.types.is_integer_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    tuples: List[Tuple] = [tuple(x) for x in df.to_numpy()]
    cols_list: List[str] = list(df.columns)
    cols: str = ",".join(cols_list)
    placeholders: str = ",".join(
        ["%s"] * len(cols_list)
    )  # Create the correct number of placeholders
    # Create a parameterized query
    query: sql.SQL = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name), sql.SQL(cols), sql.SQL(placeholders)
    )
    cursor: psycopg2.extensions.cursor = connection.cursor()
    try:
        execute_batch(cursor, query, tuples)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while inserting data into PostgreSQL: {error}")
        connection.rollback()
    finally:
        cursor.close()

def populate_product_review_data(
    conn: psycopg2.extensions.connection, csv_file: str
) -> None:
    """
    Populate the product_review table with data from the CSV file.
    Args:
        conn (psycopg2.extensions.connection): PostgreSQL connection object.
        csv_file (str): Path to the CSV file containing product review data.
    """
    try:
        # Read the product_review.csv file into a pandas dataframe, skipping bad lines
        product_review: pd.DataFrame = pd.read_csv(csv_file, on_bad_lines="skip")[
            ["user_id", "product_id", "rating", "timestamp", "review"]
        ]
        insert_dataframe(product_review, "product_review", conn)
        print(
            f"DataFrame successfully written to the 'product_review' table in the database."
        )
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def upload_images_to_s3():
     
    s3_profile = get_s3_connection_profile()

    local_images_directory = "./dataset/images"
     
    session = boto3.session.Session(
            aws_access_key_id=s3_profile.access_key,
            aws_secret_access_key=s3_profile.secret_key
          )

    s3_resource = session.resource('s3',
        config=botocore.client.Config(signature_version='s3v4'),
        endpoint_url=s3_profile.endpoint_url,
        region_name=s3_profile.region
        )
     
    edb_bucket = s3_resource.Bucket(s3_profile.bucket_name)

    images_uploaded = 0
    print(f"Uploading images to s3 bucket {s3_profile.endpoint_url}:{s3_profile.bucket_name} ... ", end="")

    for root, dirs, files in os.walk(local_images_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            object_key = os.path.join(s3_profile.recommender_images_path, filename)
            edb_bucket.upload_file(file_path, object_key)
            images_uploaded += 1
            if images_uploaded % 100 == 0:
                print(f"{images_uploaded} ", end="")

    print("Upload completed.")

def create_and_refresh_retriever(conn):
    """Create and retriever with bytea image data"""
    
    s3_connection_profile = get_s3_connection_profile()
    
    with conn.cursor() as cur:
        start_time = time.time()
        # Run for S3 bucket
        # The idea is to create a retriever for the images bucket so the image search can run over it.
        fdw_drop_sql = "drop server if exists images_s3_little cascade;"
        cur.execute(fdw_drop_sql)

        fdw_create_sql = f"""CREATE SERVER images_s3_little FOREIGN DATA WRAPPER pgfs_fdw OPTIONS (url '{s3_connection_profile.bucket_name}', region '{s3_connection_profile.region}', skip_signature '{s3_connection_profile.skip_signature}');"""
        cur.execute(fdw_create_sql)
        cur.execute("""SELECT aidb.create_volume('images_bucket_vol', 'images_s3_little', '/', 'Image');""")
        cur.execute("""SELECT aidb.create_model('multimodal_clip', 'clip_local');""")
        cur.execute("""
            SELECT aidb.create_retriever_for_volume(
               name => 'recom_images',
               model_name => 'multimodal_clip',
               source_volume_name => 'images_bucket_vol'
       );
        """)
        cur.execute(f"""SELECT aidb.bulk_embedding('recom_images');""")
        vector_time = time.time() - start_time
        print(f"Creating and refreshing recom_images retriever took {vector_time:.4f} seconds.")
        start_time = time.time()
        # Run retriever for products table
        # The idea is to create a retriever for the products table so the text search can run over it.
        cur.execute("""SELECT aidb.create_model('paraphrase', 
                            'bert_local', 
                            '{"model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                             "revision": "main"}'::JSONB);""")
        cur.execute("""SELECT aidb.create_retriever_for_table(
                    name => 'recommend_products',
                    model_name => 'paraphrase',
                    source_table => 'products',
                    source_key_column => 'img_id',
                    source_data_column => 'productdisplayname',
                    source_data_type => 'Text'
                    );""")
        cur.execute(f"""SELECT aidb.bulk_embedding('recommend_products');""")
        
        ########### WARNING: The below command will create a remote model ############
        # So please replace the url with the OpenShift vLLM endpoint
        # This is the GenAI model that will be used to generate review summary
        cur.execute(
            f"""select aidb.create_model('llama38b', 'completions', '{{"model":"llama3", "url":"http://host.docker.internal:11434/v1/chat/completions"}}'::JSONB);"""
        )
        vector_time = time.time() - start_time
        print(f"Creating and refreshing recom_products retriever took {vector_time:.4f} seconds.")

def main():
        conn=None
        try:
            conn = create_db_connection() # Connect to the database
            conn.autocommit = True  # Enable autocommit for creating the database
            start_time = time.time()
            initialize_database(conn) # Initialize the db with aidb, pgfs extensions and necessary tables
            populate_product_data(conn, './dataset/styles.csv') # Populate the products table with the stylesc.csv data
            populate_product_review_data(conn, "dataset/product_reviews.csv")
            create_and_refresh_retriever(conn) # Create and refresh the retriever for the products table and images bucket
            vector_time = time.time() - start_time
            print(f"Total process time: {vector_time:.4f} seconds.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
        finally:
            if conn:
                    conn.close()

if __name__ == "__main__":
    #main()
    upload_images_to_s3()