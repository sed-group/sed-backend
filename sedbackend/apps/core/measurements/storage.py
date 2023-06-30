from typing import Optional, List
from datetime import datetime

from fastapi.logger import logger

from mysqlsb import MySQLStatementBuilder, FetchType, exclude_cols
import sedbackend.apps.core.measurements.models as models
import sedbackend.apps.core.measurements.exceptions as exc

MEASUREMENTS_SETS_TABLE = 'measurements_sets'
MEASUREMENTS_SETS_COLUMNS = ['id', 'name', 'type', 'description']
MEASUREMENTS_TABLE = 'measurements'
MEASUREMENTS_COLUMNS = ['id', 'name', 'type', 'description', 'measurement_set_id']
MEASUREMENTS_RESULTS_DATA_TABLE = 'measurements_results_data'
MEASUREMENTS_RESULTS_DATA_COLUMNS = ['id', 'measurement_id', 'value', 'type', 'insert_timestamp', 'measurement_timestamp']
MEASUREMENTS_SETS_SUBPROJECTS_MAP_TABLE = 'measurements_sets_subprojects_map'
MEASUREMENTS_SETS_SUBPROJECTS_MAP_COLUMNS = ['id', 'subproject_id', 'measurement_set_id']


def db_get_measurement_set(con, measurement_set_id) -> models.MeasurementSet:
    # Fetch measurement set
    select_set_stmnt = MySQLStatementBuilder(con)
    res = select_set_stmnt\
        .select(MEASUREMENTS_SETS_TABLE, MEASUREMENTS_SETS_COLUMNS)\
        .where("id = ?", [measurement_set_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.MeasurementNotFoundException

    measurement_set = models.MeasurementSet(**res)

    # Fetch measurements
    nested_count_exp = f'(SELECT COUNT(*) FROM `{MEASUREMENTS_RESULTS_DATA_TABLE}` ' \
                       f'WHERE `{MEASUREMENTS_RESULTS_DATA_TABLE}`.`measurement_id` = `{MEASUREMENTS_TABLE}`.`id`)'

    with con.cursor(prepared=True) as cursor:
        # This expression requires nested expressions, and is thus written by hand, rather than through abstraction
        # build expression..
        data_count_name = 'data_count'
        query = f"SELECT {', '.join(MEASUREMENTS_COLUMNS)}, {nested_count_exp} as {data_count_name} " \
                f"FROM {MEASUREMENTS_TABLE} " \
                f"WHERE measurement_set_id = ?"
        values = [measurement_set_id]

        # Log for sanity-check
        logger.debug(f"db_get_measurement_set query: '{query}' with values: {values}")

        # Execute query
        cursor.execute(query, values)

        # Loop through results, and put information into measurement_set object
        rs = cursor.fetchall()
        columns = MEASUREMENTS_COLUMNS + [data_count_name]
        for res in rs:
            res_dict = dict(zip(columns, res))
            measurement_set.measurements.append(models.MeasurementListing(**res_dict))

    return measurement_set


def db_delete_measurement_set(con, measurement_set_id) -> bool:
    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(MEASUREMENTS_SETS_TABLE)\
        .where("id = %s", [measurement_set_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exc.MeasurementSetNotFoundException

    return True


def db_post_measurement_set(con, measurement_set: models.MeasurementSetPost, subproject_id: Optional[int] = None,
                            project_id: Optional[int] = None) \
        -> models.MeasurementSet:
    post_stmnt = MySQLStatementBuilder(con)
    post_stmnt\
        .insert(MEASUREMENTS_SETS_TABLE, ['name', 'type', 'description'])\
        .set_values([measurement_set.name, measurement_set.type.value, measurement_set.description])\
        .execute()

    set_id = post_stmnt.last_insert_id

    # Map to subproject
    if subproject_id is not None:
        insert_map_stmnt = MySQLStatementBuilder(con)
        insert_map_stmnt\
            .insert(MEASUREMENTS_SETS_SUBPROJECTS_MAP_TABLE, ['subproject_id', 'measurement_set_id'])\
            .set_values([subproject_id, set_id]).execute()

    # Map to project
    if project_id is not None:
        raise NotImplemented

    return db_get_measurement_set(con, set_id)


def db_get_measurement_sets(con, subproject_id: Optional[int] = None, project_id: Optional[int] = None) \
        -> List[models.MeasurementSetListing]:
    # Validate input
    if subproject_id is None and project_id is None:
        raise exc.MeasurementSearchParameterException('Project ID or subproject ID needs to be set')

    if subproject_id is not None:
        return db_get_measurements_sets_in_subproject(con, subproject_id)

    if project_id is not None:
        raise NotImplemented


def db_get_measurement(con, measurement_set_id, measurement_id) -> Optional[models.Measurement]:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(MEASUREMENTS_TABLE, MEASUREMENTS_COLUMNS)\
        .where("id = %s AND measurement_set_id = %s", [measurement_id, measurement_set_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise exc.MeasurementNotFoundException(f'No measurement found with id {measurement_id}')

    measurement = models.Measurement(**res)

    return measurement


def db_post_measurement(con, measurement: models.MeasurementPost, measurement_set_id: int) -> models.Measurement:
    # Assert that the measurement set exists
    db_get_measurement_set(con, measurement_set_id) # Raises if it does not

    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(MEASUREMENTS_TABLE, exclude_cols(MEASUREMENTS_COLUMNS, ['id']))\
        .set_values([measurement.name, measurement.type, measurement.description, measurement_set_id])\
        .execute()

    measurement_id = insert_stmnt.last_insert_id

    return db_get_measurement(con, measurement_set_id, measurement_id)


def db_delete_measurement(con, measurement_set_id: int, measurement_id: int) -> bool:
    db_get_measurement_set(con, measurement_set_id) # Raises if set does not exist

    delete_stmnt = MySQLStatementBuilder(con)
    res, rows = delete_stmnt\
        .delete(MEASUREMENTS_TABLE)\
        .where("id = %s AND measurement_set_id = %s", [measurement_id, measurement_set_id])\
        .execute(return_affected_rows=True)

    if rows == 0:
        raise exc.MeasurementNotFoundException

    return True


def db_get_measurement_result_by_id(con, measurement_id: int, result_id: int) -> models.MeasurementResultData:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(MEASUREMENTS_RESULTS_DATA_TABLE, MEASUREMENTS_RESULTS_DATA_COLUMNS)\
        .where('id = %s AND measurement_id = %s', [result_id, measurement_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.MeasurementResultNotFoundException(f'No measurement result found with id {result_id}')

    mrd = models.MeasurementResultData(**res)

    return mrd


def db_get_measurement_results(con,
                               measurement_id: int,
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None,
                               date_class: Optional[
                                   models.MeasurementDateClassification] = models.MeasurementDateClassification.MEASUREMENT,
                               dtype: Optional[models.MeasurementDataType] = None
                               ) -> List[models.MeasurementResultData]:
    select_stmnt = MySQLStatementBuilder(con)
    where_stmnt = 'measurement_id = %s'
    where_values = [measurement_id]

    if date_class is models.MeasurementDateClassification.MEASUREMENT:
        date_column = 'measurement_timestamp'
    elif date_class is models.MeasurementDateClassification.INSERT:
        date_column = 'insert_timestamp'
    else:
        raise ValueError("Unknown date classification")

    if date_from is not None:
        where_stmnt += f' AND {date_column} > %s'
        where_values.append(date_from)

    if date_to is not None:
        where_stmnt += f' AND {date_column} < %s'
        where_values.append(date_to)

    if dtype is not None:
        where_stmnt += f' AND type = %s'
        where_values.append(dtype.value)

    rs = select_stmnt.select(MEASUREMENTS_RESULTS_DATA_TABLE, MEASUREMENTS_RESULTS_DATA_COLUMNS)\
        .where(where_stmnt, where_values).execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)

    data_list = []
    for res in rs:
        mrd = models.MeasurementResultData(**res)
        data_list.append(mrd)

    return data_list


def db_post_measurement_result(con, measurement_id: int, mr: models.MeasurementResultDataPost) -> models.MeasurementResultData:
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(MEASUREMENTS_RESULTS_DATA_TABLE, exclude_cols(MEASUREMENTS_RESULTS_DATA_COLUMNS, ['id', 'insert_timestamp']))\
        .set_values([measurement_id, mr.value, mr.type, mr.measurement_timestamp])\
        .execute()

    insert_id = insert_stmnt.last_insert_id

    return db_get_measurement_result_by_id(con, measurement_id, insert_id)


def db_get_measurements_sets_in_subproject(con, subproject_id: int) -> List[models.MeasurementSetListing]:
    """
    Get all measurement sets that are accessible to a specific subproject
    :param con:
    :param subproject_id:
    :return:
    """
    nested_measurement_count = "(SELECT COUNT(*) FROM `measurements` " \
                               "WHERE `measurements`.`measurement_set_id` = `measurements_sets`.`id`)"

    nested_subproject_map = f"(SELECT `measurements_sets_subprojects_map`.`measurement_set_id` " \
                            f"FROM `measurements_sets_subprojects_map` " \
                            f"WHERE `measurements_sets_subprojects_map`.`subproject_id` = ?)"

    query = f"SELECT *, {nested_measurement_count} " \
            f"FROM `measurements_sets` " \
            f"WHERE `measurements_sets`.`id` IN {nested_subproject_map}"

    values = [subproject_id]

    logger.debug(f"db_get_measurements_sets_in_subproject query: '{query}' with values: {values}")

    set_list = []
    with con.cursor(prepared=True) as cursor:
        cursor.execute(query, values)
        rs = cursor.fetchall()
        columns = MEASUREMENTS_SETS_COLUMNS + ['measurement_count']

        for res in rs:
            res_dict = dict(zip(columns, res))
            print(res_dict)
            m_set = models.MeasurementSetListing(**res_dict)
            set_list.append(m_set)

    return set_list
