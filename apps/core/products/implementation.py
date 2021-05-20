from fastapi import HTTPException, status

from apps.core.db import get_connection
from apps.core.products.storage import *
from apps.core.products.exceptions import DuplicateDesignParameterException


def impl_create_product(name, design_parameters):
    try:
        with get_connection() as con:
            res = db_create_product(con, name, design_parameters)
            con.commit()
            return res
    except DuplicateDesignParameterException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate design parameter",
        )