from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status

from apps.core.measurements.models import (Measurement, MeasurementPost,
                                           MeasurementDataType, MeasurementResultData,
                                           MeasurementDateClassification, MeasurementResultDataPost)
from apps.core.measurements.storage import (db_get_measurement, db_post_measurement, db_get_measurement_result_by_id,
                                            db_get_measurement_results, db_post_measurement_result)
from apps.core.measurements.exceptions import *
from apps.core.db import get_connection


def impl_get_measurement(measurement_id: int) -> Optional[Measurement]:
    try:
        with get_connection() as con:
            return db_get_measurement(con, measurement_id)
    except MeasurementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


def impl_post_measurement(measurement: MeasurementPost) -> Measurement:
    with get_connection() as con:
        res = db_post_measurement(con, measurement)
        con.commit()
        return res


def impl_get_measurement_result_by_id(m_id: int, mr_id: int) -> MeasurementResultData:
    with get_connection() as con:
        return db_get_measurement_result_by_id(con, m_id, mr_id)


def impl_get_measurement_results(measurement_id: int,
                                 dtype: Optional[MeasurementDataType],
                                 date_class: Optional[MeasurementDateClassification],
                                 date_from: Optional[datetime],
                                 date_to: Optional[datetime],
                                 ) -> List[MeasurementResultData]:

    with get_connection() as con:
        res = db_get_measurement_results(con,
                                         measurement_id,
                                         date_from=date_from,
                                         date_to=date_to,
                                         date_class=date_class,
                                         dtype=dtype)
        return res


def impl_post_measurement_result(measurement_id: int, mr: MeasurementResultDataPost):
    with get_connection() as con:
        res = db_post_measurement_result(con, measurement_id, mr)
        con.commit()
        return res
