from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Security, Depends

import apps.core.measurements.models as models
import apps.core.measurements.implementation as impl

router = APIRouter()


@router.get("/sets/{measurement_set_id}",
            summary="Get measurement set by ID",
            response_model=models.MeasurementSet)
async def get_measurement_set(measurement_set_id: int):
    return impl.impl_get_measurement_set(measurement_set_id)


@router.post("/sets/",
             summary="Post measurement set",
             response_model=models.MeasurementSet)
async def post_measurement_set(measurement_set: models.MeasurementSetPost):
    return impl.impl_post_measurement_set(measurement_set)


@router.get("/sets/",
             summary="Get measurement sets",
             response_model=List[models.MeasurementSet])
async def get_measurement_sets(segment_length:int, index: int):
    return impl.impl_get_measurement_sets(segment_length, index)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}",
            summary="Get measurement",
            description="Get measurement information",
            response_model=models.Measurement)
async def get_measurement (measurement_set_id: int, measurement_id: int):
    return impl.impl_get_measurement(measurement_set_id, measurement_id)


@router.post("/sets/{measurement_set_id}/",
             summary="Post measurement",
             response_model=models.Measurement)
async def post_measurement(measurement: models.MeasurementPost, measurement_set_id: int):
    return impl.impl_post_measurement(measurement, measurement_set_id)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}/results/{measurement_result_data_id}",
            summary="Get measurement result datapoint",
            response_model=models.MeasurementResultData)
async def get_measurement_result_by_id(measurement_id: int, measurement_result_data_id: int):
    return impl.impl_get_measurement_result_by_id(measurement_id, measurement_result_data_id)


@router.get("/sets/{measurement_set_id}/measurements/{measurement_id}/results",
            summary="Get measurement result data",
            description="Search for specific data measurement. Dates are provided as UNIX timestamp in milliseconds.",
            response_model=List[models.MeasurementResultData])
async def get_measurement_results(measurement_set_id: int,
                                  measurement_id: int,
                                  dtype: Optional[models.MeasurementDataType] = None,
                                  date_from: Optional[int] = None,
                                  date_to: Optional[int] = None,
                                  date_class: Optional[models.MeasurementDateClassification] = models.MeasurementDateClassification.MEASUREMENT,
                                  ) -> List[models.MeasurementResultData]:
    date_from = datetime.fromtimestamp(date_from/1000)
    date_to = datetime.fromtimestamp(date_to/1000)
    return impl.impl_get_measurement_results(measurement_id, dtype, date_class, date_from, date_to)


@router.post("/sets/{measurement_set_id}/measurements/{measurement_id}/results/",
             summary="Post measurement result data",
             response_model=None)
async def post_measurement_result(measurement_id: int, measurement_data_post: models.MeasurementResultDataPost):
    impl.impl_post_measurement_result(measurement_id, measurement_data_post)
