from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

import apps.core.files.implementation as impl
from apps.core.authentication.utils import get_current_active_user
from apps.core.users.models import User


router = APIRouter()


@router.post("/download",
             summary="Download file",
             response_class=FileResponse)
async def get_file(file_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Download an uploaded file
    """
    stored_file_path = impl.impl_get_file_path(file_id, current_user.id)
    resp = FileResponse(
        path=stored_file_path.path,
        filename=stored_file_path.filename
    )
    return resp
