import secrets
from datetime import datetime

from fastapi.logger import logger

from sedbackend.apps.core.authentication.models import UserAuth, SSOResolutionData
from sedbackend.apps.core.users.exceptions import UserNotFoundException
from sedbackend.apps.core.authentication.exceptions import InvalidNonceException, FaultyNonceOperation
from mysqlsb.builder import MySQLStatementBuilder, FetchType

from mysql.connector.pooling import PooledMySQLConnection


def get_user_auth_only(connection, user_name: str) -> UserAuth:
    """
    Get a fully populated user model. This is unsafe to use anywhere but during authorization.
    :param connection: MySQL connection
    :param user_name: username
    :return: UserAuth
    """
    cursor = connection.cursor(prepared=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (user_name,))
    user_data = cursor.fetchone()

    if user_data is None:
        raise UserNotFoundException

    user_data = dict(zip(cursor.column_names, user_data))
    cursor.close()

    user = UserAuth(**user_data)
    return user


def db_insert_sso_token(connetion: PooledMySQLConnection, user_id: int, ip: str) -> str:
    nonce = secrets.token_urlsafe()
    stmnt = MySQLStatementBuilder(connetion)
    stmnt.insert('sso_tokens', ['user_id', 'ip', 'nonce']).set_values([user_id, ip, nonce]).execute(no_logs=True)
    return nonce


def db_resolve_sso_token(connection: PooledMySQLConnection, ip: str, nonce: str) -> int:
    """
    :param connection:
    :param ip:
    :param nonce:
    :return: User id for which the token is resolved
    """
    stmnt = MySQLStatementBuilder(connection)
    res = stmnt.select('sso_tokens', ['id', 'user_id', 'expiration'])\
        .where('nonce = %s AND ip = %s', [nonce, ip])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE, no_logs=True)

    if res is None:
        raise InvalidNonceException

    res_data = SSOResolutionData(**res)

    logger.debug(f'Expiration date: {res_data.expiration}')
    logger.debug(f'Current date: {datetime.now()}')

    if datetime.now() >= res_data.expiration:
        raise InvalidNonceException

    stmnt_del = MySQLStatementBuilder(connection)
    res_del, rows = stmnt_del.delete('sso_tokens').where('id = %s', [res_data.id]).execute(return_affected_rows=True, no_logs=True)

    if rows == 0:
        raise FaultyNonceOperation

    return res_data.user_id
