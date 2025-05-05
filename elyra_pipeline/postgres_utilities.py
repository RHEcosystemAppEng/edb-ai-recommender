import psycopg2, os

def connect_db(uri:str=None) -> psycopg2.extensions.connection:
    if not uri:
        uri = os.environ.get('URI')
    if not uri:
        missing_connection_uri = """
            A connection string URI was not provided and none was found in the local environment configuration.
            Ensure your OpenShift AI workbench specifies a string environment variable named 'URI' that
            provides a valid Postgres connection URI to a running EDB-AI Postgres database in the cluster.
            """
        raise Exception(missing_connection_uri)

    try:
        conn = psycopg2.connect(uri)
    except:
        invalid_connection_uri = """
            The configured or provided Postgres connection URI is invalid.
            Ensure your OpenShift AI workbench specifies a string environment variable named 'URI' that
            provides a valid Postgres connection URI to a running EDB-AI Postgres database in the cluster.
            """
        raise Exception(invalid_connection_uri)
        
    return conn

def close_db(conn:psycopg2.extensions.connection) -> None:
    conn.close()

def execute_sql(conn:psycopg2.extensions.connection, sql:str) -> None:
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def execute_sql_results(conn:psycopg2.extensions.connection, sql:str) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(sql, prepare=True)
    rows = cur.fetchall()
    return rows

def execute_sql_results_np(conn:psycopg2.extensions.connection, sql:str) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def execute_sql_results_params(conn:psycopg2.extensions.connection, sql:str, *params) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(sql, params, prepare=True)
    rows = cur.fetchall()
    return rows

def execute_sql_results_params_np(conn:psycopg2.extensions.connection, sql:str, *params) -> list[tuple]:
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    return rows