from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status

import apps.core.measurements.models as models
import apps.core.measurements.storage as storage
import apps.core.measurements.exceptions as exc
import apps.core.measurements.algorithms as algs
import apps.core.files.models as models_files
from apps.core.db import get_connection


def impl_get_measurement_set(measurement_set_id: int):
    try:
        with get_connection() as con:
            return storage.db_get_measurement_set(con, measurement_set_id)
    except exc.MeasurementSetNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement set with id {measurement_set_id} could not be found."
        )


def impl_post_measurement_set(measurement_set: models.MeasurementSetPost, subproject_id: Optional[int] = None):
    with get_connection() as con:
        res = storage.db_post_measurement_set(con, measurement_set, subproject_id=subproject_id)
        con.commit()
        return res


def impl_get_measurement_sets(subproject_id: Optional[int] = None) -> List[models.MeasurementSetListing]:
    try:
        with get_connection() as con:
            return storage.db_get_measurement_sets(con, subproject_id=subproject_id)
    except exc.MeasurementSearchParameterException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def impl_delete_measurement_set(measurement_set_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_measurement_set(con, measurement_set_id)
            con.commit()
            return res
    except exc.MeasurementSetNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No rows were affected. Incorrect ID?"
        )


def impl_get_measurement(measurement_set_id: int, measurement_id: int) -> Optional[models.Measurement]:
    try:
        with get_connection() as con:
            return storage.db_get_measurement(con, measurement_set_id, measurement_id)
    except exc.MeasurementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with id {measurement_id} could not be found.",
        )


def impl_post_measurement(measurement: models.MeasurementPost, measurement_set_id: int) -> models.Measurement:
    with get_connection() as con:
        res = storage.db_post_measurement(con, measurement, measurement_set_id)
        con.commit()
        return res


def impl_delete_measurement(measurement_set_id: int, measurement_id: int) -> bool:
    try:
        with get_connection() as con:
            res = storage.db_delete_measurement(con, measurement_set_id, measurement_id)
            con.commit()
            return res
    except exc.MeasurementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Measurement not found"
        )
    except exc.MeasurementSetNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Measurement set not found"
        )


def impl_get_measurement_result_by_id(m_id: int, mr_id: int) -> models.MeasurementResultData:
    with get_connection() as con:
        return storage.db_get_measurement_result_by_id(con, m_id, mr_id)


def impl_get_measurement_results(measurement_id: int,
                                 dtype: Optional[models.MeasurementDataType],
                                 date_class: Optional[models.MeasurementDateClassification],
                                 date_from: Optional[datetime],
                                 date_to: Optional[datetime],
                                 ) -> List[models.MeasurementResultData]:

    with get_connection() as con:
        res = storage.db_get_measurement_results(con,
                                                 measurement_id,
                                                 date_from=date_from,
                                                 date_to=date_to,
                                                 date_class=date_class,
                                                 dtype=dtype)
        return res


def impl_post_measurement_result(measurement_id: int, mr: models.MeasurementResultDataPost) -> models.MeasurementResultData:
    with get_connection() as con:
        res = storage.db_post_measurement_result(con, measurement_id, mr)
        con.commit()
        return res


def impl_post_upload_set(stored_file_path: models_files.StoredFilePath, csv_delimiter: Optional[str] = None):
    return algs.get_sheet_headers(stored_file_path, csv_delimiter=csv_delimiter)
