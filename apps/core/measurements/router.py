from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Security, Depends

import apps.core.measurements.models as MeasurementMdls
import apps.core.measurements.implementation as MeasurementImpl

router = APIRouter()


@router.get("/{measurement_id}",
            summary="Get measurement",
            description="Get measurement information",
            response_model=MeasurementMdls.Measurement)
async def get_measurement (measurement_id: int):
    return MeasurementImpl.impl_get_measurement(measurement_id)


@router.post("/",
             summary="Post measurement",
             response_model=MeasurementMdls.Measurement)
async def post_measurement(measurement: MeasurementMdls.MeasurementPost):
    return MeasurementImpl.impl_post_measurement(measurement)


@router.get("/{measurement_id}/results/{measurement_result_data_id}",
            summary="Get measurement result datapoint",
            response_model=MeasurementMdls.MeasurementResultData)
async def get_measurement_result_by_id(measurement_id: int, measurement_result_data_id: int):
    return MeasurementImpl.impl_get_measurement_result_by_id(measurement_id, measurement_result_data_id)


@router.get("/{measurement_id}/results",
            summary="Get measurement result data",
            description="Search for specific data measurement. Dates are provided as UNIX timestamp in milliseconds.",
            
            response_model=List[MeasurementMdls.MeasurementResultData])
async def get_measurement_results(measurement_id: int,
                                  dtype: Optional[MeasurementMdls.MeasurementDataType] = None,
                                  date_from: Optional[int] = None,
                                  date_to: Optional[int] = None,
                                  date_class: Optional[MeasurementMdls.MeasurementDateClassification] = MeasurementMdls.MeasurementDateClassification.MEASUREMENT,
                                  ) -> List[MeasurementMdls.MeasurementResultData]:
    date_from = datetime.fromtimestamp(date_from/1000)
    date_to = datetime.fromtimestamp(date_to/1000)
    return MeasurementImpl.impl_get_measurement_results(measurement_id, dtype, date_class, date_from, date_to)


@router.post("/{measurement_id}/results/",
             summary="Post measurement result data",
             response_model=None)
async def post_measurement_result(measurement_id: int, measurement_data_post: MeasurementMdls.MeasurementResultDataPost):
    MeasurementImpl.impl_post_measurement_result(measurement_id, measurement_data_post)
