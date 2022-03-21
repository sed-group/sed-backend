from mysql.connector.pooling import PooledMySQLConnection


def db_check_db_connection(con: PooledMySQLConnection) -> int:
    with con.cursor() as cursor:
        cursor.execute("SELECT NOW(3)")
        dt = cursor.fetchone()[0]
        return dt.timestamp() * 1000
