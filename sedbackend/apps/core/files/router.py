from fastapi import APIRouter, Depends, Security
from fastapi.responses import FileResponse

import sedbackend.apps.core.files.implementation as impl
from sedbackend.apps.core.projects.dependencies import ProjectAccessChecker
import sedbackend.apps.core.projects.models as models
from sedbackend.apps.core.authentication.utils import get_current_active_user, verify_scopes
from sedbackend.apps.core.users.models import User


router = APIRouter()


@router.get("/{file_id}/download",
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

@router.delete("/{file_id}/delete",
               summary="Delete file",
               response_model=bool,
               dependencies=[Security(verify_scopes, scopes=["admin"])])
async def delete_file(file_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Delete a file. 
    Only accessible to admins and the owner of the file. 
    """
    return impl.impl_delete_file(file_id, current_user.id)
    