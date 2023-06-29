from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

import sedbackend.apps.core.files.implementation as impl
from sedbackend.apps.core.files.dependencies import FileAccessChecker
from sedbackend.apps.core.authentication.utils import get_current_active_user
from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.core.users.models import User


router = APIRouter()


@router.get("/{file_id}/download",
             summary="Download file",
             response_class=FileResponse,
             dependencies=[Depends(FileAccessChecker(AccessLevel.list_can_read()))]
             )
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


@router.delete("/{file_id}/delete",
               summary="Delete file",
               response_model=bool,
               dependencies=[Depends(FileAccessChecker(AccessLevel.list_are_admins()))])
async def delete_file(file_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Delete a file. 
    Only accessible to admins and the owner of the file. 
    """
    return impl.impl_delete_file(file_id, current_user.id)
    