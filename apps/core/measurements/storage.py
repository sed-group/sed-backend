from typing import Optional, List
from datetime import datetime

from libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols
import apps.core.measurements.models as models
import apps.core.measurements.exceptions as exc

MEASUREMENTS_SETS_TABLE = 'measurements_sets'
MEASUREMENTS_SETS_COLUMNS = ['measurements_sets.id', 'measurements_sets.name', 'measurements_sets.type', 'measurements_sets.description']
MEASUREMENTS_TABLE = 'measurements'
MEASUREMENTS_COLUMNS = ['id', 'name', 'type', 'description', 'measurement_set_id']
MEASUREMENTS_RESULTS_DATA_TABLE = 'measurements_results_data'
MEASUREMENTS_RESULTS_DATA_COLUMNS = ['id', 'measurement_id', 'value', 'type', 'insert_timestamp', 'measurement_timestamp']
MEASUREMENTS_SETS_SUBPROJECTS_MAP_TABLE = 'measurements_sets_subprojects_map'
MEASUREMENTS_SETS_SUBPROJECTS_MAP_COLUMNS = ['id', 'subproject_id', 'measurement_set_id']


def db_get_measurement_set(con, measurement_set_id) -> models.MeasurementSet:
    select_stmnt = MySQLStatementBuilder(con)
    rs_list = select_stmnt.execute_procedure('get_measurements_set', [measurement_set_id])

    if len(rs_list[0]) == 0:
        raise exc.MeasurementSetNotFoundException(f'Measurement set with id {measurement_set_id} not found.')

    measurement_set = models.MeasurementSet(**rs_list[0][0])
    for res in rs_list[1]:
        measurement_set.measurements.append(models.Measurement(**res))

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

    # Build SQL statement
    sql = MySQLStatementBuilder(con)
    rs_list = []
    if subproject_id is not None:
        rs_list = sql.execute_procedure('get_measurements_sets_in_subproject', [subproject_id])

    if project_id is not None:
        raise NotImplemented

    # Parse results
    set_list = []
    for res in rs_list[0]:
        mset = models.MeasurementSetListing(**res)
        set_list.append(mset)

    return set_list


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


def db_get_measurement_result_by_id(con, m_id: int, mr_id: int) -> models.MeasurementResultData:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(MEASUREMENTS_RESULTS_DATA_TABLE, MEASUREMENTS_RESULTS_DATA_COLUMNS)\
        .where('id = %s AND measurement_id = %s', [mr_id, m_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise exc.MeasurementResultNotFoundException(f'No measurement result found with id {mr_id}')

    mrd = models.MeasurementResultData(**res)

    return mrd


def db_get_measurement_results(con,
                               measurement_id: int,
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None,
                               date_class: Optional[models.MeasurementDateClassification] = models.MeasurementDateClassification.MEASUREMENT,
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


def db_post_measurement_result(con, measurement_id: int, mr: models.MeasurementResultDataPost) -> bool:
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(MEASUREMENTS_RESULTS_DATA_TABLE, exclude_cols(MEASUREMENTS_RESULTS_DATA_COLUMNS, ['id', 'insert_timestamp']))\
        .set_values([measurement_id, mr.value, mr.type, mr.measurement_timestamp])\
        .execute()

    return True
