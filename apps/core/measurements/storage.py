from typing import Optional, List
from datetime import datetime

from libs.mysqlutils import MySQLStatementBuilder, FetchType, exclude_cols
from apps.core.measurements.models import MeasurementPost, MeasurementResultDataPost, Measurement, MeasurementResultData, MeasurementDateClassification, MeasurementDataType
from apps.core.measurements.exceptions import MeasurementNotFoundException, MeasurementResultNotFoundException

MEASUREMENTS_TABLE = 'measurements'
MEASUREMENTS_COLUMNS = ['id', 'name', 'type', 'description']
MEASUREMENTS_RESULTS_DATA_TABLE = 'measurements_results_data'
MEASUREMENTS_RESULTS_DATA_COLUMNS = ['id', 'measurement_id', 'value', 'type', 'insert_timestamp', 'measurement_timestamp']


def db_get_measurement(con, measurement_id) -> Optional[Measurement]:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt\
        .select(MEASUREMENTS_TABLE, MEASUREMENTS_COLUMNS)\
        .where("id = %s", [measurement_id])\
        .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

    if res is None:
        raise MeasurementNotFoundException(f'No measurement found with id {measurement_id}')

    measurement = Measurement(**res)

    return measurement


def db_post_measurement(con, measurement: MeasurementPost) -> Measurement:
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(MEASUREMENTS_TABLE, exclude_cols(MEASUREMENTS_COLUMNS, ['id']))\
        .set_values([measurement.name, measurement.type, measurement.description])\
        .execute()

    measurement_id = insert_stmnt.last_insert_id

    return db_get_measurement(con, measurement_id)


def db_get_measurement_result_by_id(con, m_id: int, mr_id: int) -> MeasurementResultData:
    select_stmnt = MySQLStatementBuilder(con)
    res = select_stmnt.select(MEASUREMENTS_RESULTS_DATA_TABLE, MEASUREMENTS_RESULTS_DATA_COLUMNS)\
        .where('id = %s AND measurement_id = %s', [mr_id, m_id])\
        .execute(dictionary=True, fetch_type=FetchType.FETCH_ONE)

    if res is None:
        raise MeasurementResultNotFoundException(f'No measurement result found with id {mr_id}')

    mrd = MeasurementResultData(**res)

    return mrd


def db_get_measurement_results(con,
                               measurement_id: int,
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None,
                               date_class: Optional[MeasurementDateClassification] = MeasurementDateClassification.MEASUREMENT,
                               dtype: Optional[MeasurementDataType] = None
                               ) -> List[MeasurementResultData]:
    select_stmnt = MySQLStatementBuilder(con)
    where_stmnt = 'measurement_id = %s'
    where_values = [measurement_id]

    if date_class is MeasurementDateClassification.MEASUREMENT:
        date_column = 'measurement_timestamp'
    elif date_class is MeasurementDateClassification.INSERT:
        date_column = 'insert_timestamp'
    else:
        raise ValueError("Unknown date classification")

    if date_from is not None:
        where_stmnt += f' AND {date_column} > %s'
        where_values.append(date_from)

    if date_to is not None:
        where_stmnt += f' AND {date_column} < %s'
        where_values.append(date_to)

    if date_to is not None:
        where_stmnt += f' AND type = %s'
        where_values.append(dtype.value)

    # Breaks here, probably? Test.

    rs = select_stmnt.select(MEASUREMENTS_RESULTS_DATA_TABLE, MEASUREMENTS_RESULTS_DATA_COLUMNS)\
        .where(where_stmnt, where_values)\
        .execute(dictionary=True)

    data_list = []
    for res in rs:
        mrd = MeasurementResultData(**res)
        data_list.append(mrd)
    return data_list


def db_post_measurement_result(con, measurement_id: int, mr: MeasurementResultDataPost) -> bool:
    insert_stmnt = MySQLStatementBuilder(con)
    insert_stmnt\
        .insert(MEASUREMENTS_RESULTS_DATA_TABLE, exclude_cols(MEASUREMENTS_RESULTS_DATA_COLUMNS, ['id', 'insert_timestamp']))\
        .set_values([measurement_id, mr.value, mr.type, mr.measurement_timestamp])\
        .execute()

    return True
