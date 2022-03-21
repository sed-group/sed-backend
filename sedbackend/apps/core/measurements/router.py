from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File

import sedbackend.apps.core.measurements.models as models
import sedbackend.apps.core.measurements.implementation as impl
from sedbackend.apps.core.users.models import User
from sedbackend.apps.core.authentication.utils import get_current_active_user

router = APIRouter()


@router.post("/sets",
             summary="Post measurement set",
             response_model=models.MeasurementSet)
async def post_measurement_set(measurement_set: models.MeasurementSetPost, subproject_id: Optional[int] = None):
    return impl.impl_post_measurement_set(measurement_set, subproject_id=subproject_id)


@router.get("/sets",
            summary="Get measurement sets",
            response_model=List[models.MeasurementSetListing])
async def get_measurement_sets(subproject_id: Optional[int] = None):
    return impl.impl_get_measurement_sets(subproject_id=subproject_id)


@router.post("/sets/upload",
             summary="Upload measurement set",
             response_model=List[str],
             description="Upload a measurement set using a CSV or Excel file. Leaving csv_delimiter as None will "
                         "result in the value being inferred automatically.")
async def post_upload_set(file: UploadFile = File(...), current_user: User = Depends(get_current_active_user),
                          csv_delimiter: Optional[str] = None):
    return impl.impl_post_upload_set(file, current_user.id, csv_delimiter=csv_delimiter)


@router.get("/sets/{measurement_set_id}",
            summary="Get measurement set by ID",
            response_model=models.MeasurementSet)
async def get_measurement_set(measurement_set_id: int):
    return impl.impl_get_measurement_set(measurement_set_id)


@router.delete("/sets/{measurement_set_id}",
               summary="Delete measurement set",
               response_model=bool)
async def delete_measurement_set(measurement_set_id: int) -> bool:
    return impl.impl_delete_measurement_set(measurement_set_id)


@router.post("/sets/{measurement_set_id}/measurements",
             summary="Post measurement",
             response_model=models.Measurement)
async def post_measurement(measurement: models.MeasurementPost, measurement_set_id: int):
    return impl.impl_post_measurement(measurement, measurement_set_id)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}",
            summary="Get measurement",
            description="Get measurement information",
            response_model=models.Measurement)
async def get_measurement (measurement_set_id: int, measurement_id: int):
    return impl.impl_get_measurement(measurement_set_id, measurement_id)


@router.delete("/sets/{measurement_set_id}/measurements/{measurement_id}",
               summary="Delete measurement",
               response_model=bool)
async def delete_measurement(measurement_set_id: int, measurement_id: int):
    return impl.impl_delete_measurement(measurement_set_id, measurement_id)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}/results",
            summary="Get measurement result data",
            description="Search for specific data measurement. Dates are provided as UNIX timestamp in milliseconds.",
            response_model=List[models.MeasurementResultData])
async def get_measurement_results(measurement_set_id: int,
                                  measurement_id: int,
                                  dtype: Optional[models.MeasurementDataType] = None,
                                  date_from: Optional[int] = None,
                                  date_to: Optional[int] = None,
                                  date_class: Optional[
                                      models.MeasurementDateClassification] = models.MeasurementDateClassification.MEASUREMENT,
                                  ) -> List[models.MeasurementResultData]:
    if date_from:
        date_from = datetime.fromtimestamp(date_from/1000)
    if date_to:
        date_to = datetime.fromtimestamp(date_to/1000)
    return impl.impl_get_measurement_results(measurement_id, dtype, date_class, date_from, date_to)


@router.post("/sets/{measurement_set_id}/measurements/{measurement_id}/results",
             summary="Post measurement result data",
             response_model=models.MeasurementResultData)
async def post_measurement_result(measurement_id: int, measurement_data_post: models.MeasurementResultDataPost):
    return impl.impl_post_measurement_result(measurement_id, measurement_data_post)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}/results/{measurement_result_data_id}",
            summary="Get measurement result datapoint",
            response_model=models.MeasurementResultData)
async def get_measurement_result_by_id(measurement_id: int, measurement_result_data_id: int):
    return impl.impl_get_measurement_result_by_id(measurement_id, measurement_result_data_id)
