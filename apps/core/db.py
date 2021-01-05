import mysql.connector
from mysql.connector import errorcode, pooling

connection_pool = None

try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        user='rw',
        password='DONT_USE_IN_PRODUCTION!',     # Change for production environments
        host='127.0.0.1',
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
        print('Incorrect mysql credentials')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print('DB could not be found')
    else:
        print(err)
else:
    print('Database connection pool was successfully established')


def get_connection():
    return connection_pool.get_connection()
