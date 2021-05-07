from fastapi.logger import logger
import mysql.connector
from mysql.connector import errorcode, pooling

from contextlib import contextmanager

connection_pool = None

try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        user='rw',            # Change for production environments
        password='DONT_USE_IN_PRODUCTION!',      # Change for production environments
        host='localhost', #'core-db',
        database='seddb',
        port=3306,
        autocommit=False,
        get_warnings=True,                      # Change for production environments (True in dev)
        raise_on_warnings=True,                 # Change for production environments (True in dev)
        pool_size=1,                            # Change for production environments (as few as possible in dev)
        connection_timeout=10                   # Might want to increase this for production
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        logger.error('Incorrect mysql credentials')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        logger.error('DB could not be found')
    else:
        logger.error(err)
else:
    logger.debug('Database connection pool was successfully established')


@contextmanager
def get_connection():
    """
    Returns a MySQL connection that can be used for read/write.
    Should be utilized through "get with resources" methodology.
    """
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()
