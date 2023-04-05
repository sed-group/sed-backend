from fastapi.logger import logger
import mysql.connector
from mysql.connector import errorcode, pooling
from sedbackend.env import Environment

from contextlib import contextmanager


connection_pool = None

user = 'rw'
password = Environment.get_variable('MYSQL_PWD_RW')
host = 'core-db'
database = 'seddb'
port = 3306


try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        user=user,
        password=password,
        host=host,
        database=database,
        port=port,
        autocommit=False,
        get_warnings=True,                      # Change for production environments (True in dev)
        raise_on_warnings=True,                 # Change for production environments (True in dev)
        pool_size=4,                            # Change for production environments (as few as possible in dev)
        connection_timeout=10                   # Might want to increase this for production
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        logger.error('Incorrect mysql credentials')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        logger.error('DB could not be found')
    elif err.errno == 2003:
        logger.error('Incorrect database configuration')
    else:
        logger.debug('Unknown database error')

    raise ValueError(f'Malfunctioning database configuration. {user}@{database} at Host: {host}:{port}')


@contextmanager
def get_connection() -> pooling.PooledMySQLConnection:
    """
    Returns a MySQL connection that can be used for read/write.
    Should be utilized through "get with resources" methodology.
    """
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()
