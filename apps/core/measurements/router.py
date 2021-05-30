from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Security, Depends

import apps.core.measurements.models as MeasurementMdls
import apps.core.measurements.implementation as MeasurementImpl

router = APIRouter()


@router.get("/{measurement_id}",
             summary="Get measurement",
             description="Get measurement information")
async def get_measurement (measurement_id: int):
    return MeasurementImpl.impl_get_measurement(measurement_id)


@router.post("/",
             summary="Post measurement")
async def post_measurement(measurement: MeasurementMdls.MeasurementPost):
    return MeasurementImpl.impl_post_measurement(measurement)


@router.get("/{measurement_id}/{measurement_result_data_id}",
            summary="Get measurement result datapoint")
async def get_measurement_result_by_id(measurement_id: int, measurement_result_data_id: int):
    return MeasurementImpl.impl_get_measurement_result_by_id(measurement_id, measurement_result_data_id)


@router.get("/{measurement_id}/",
            summary="Get measurement result data")
async def get_measurement_results(measurement_id: int,
                                  date_from: Optional[datetime],
                                  date_to: Optional[datetime],
                                  date_class: Optional[MeasurementMdls.MeasurementDateClassification],
                                  dtype: Optional[MeasurementMdls.MeasurementDataType]) -> List[MeasurementMdls.MeasurementResultData]:
    return MeasurementImpl.impl_get_measurement_results(measurement_id,
                                                        date_from=date_from,
                                                        date_to=date_to,
                                                        date_class=date_class,
                                                        dtype=dtype)


@router.post("{measurement_id}/",
             summary="Post measurement result data")
async def post_measurement_result(measurement_id: int, measurement_data_post: MeasurementMdls.MeasurementResultDataPost):
    MeasurementImpl.impl_post_measurement_result(measurement_id, measurement_data_post)
