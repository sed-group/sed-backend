from typing import Any, List

from fastapi import HTTPException, Request, status
from fastapi.logger import logger

from sedbackend.apps.core.projects.models import AccessLevel
from sedbackend.apps.core.files.implementation import impl_get_file_path

class FileAccessChecker:
  def __init__(self, allowed_levels: List[AccessLevel]) -> None:
    self.access_levels = allowed_levels
  
  def __call__(self, file_id: int, request: Request):
    logger.debug(f'Does user with id {request.state.user_id}'
                 f'have the appropriate access levels ({self.access_levels})?')
    user_id = request.state.user_id
    
    file_path = impl_get_file_path(file_id, user_id)
    
    #Should have accesslevel on the files...
    # or check simply for admin access
    
    if user_id == file_path.owner_id or AccessLevel.ADMIN in self.access_levels:
      logger.debug(f'Yes, user {user_id} has correct access level')
      return True
    
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="User does not have the necessary access level"
    )