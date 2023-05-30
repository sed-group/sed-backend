import tempfile
import tests.apps.core.projects.testutils as tu_proj
import tests.apps.core.users.testutils as tu_users
import tests.apps.core.files.testutils as tu

import sedbackend.apps.core.files.implementation as impl
import sedbackend.apps.core.files.models as models
import sedbackend.apps.core.users.implementation as impl_users
from sedbackend.apps.core.projects.models import AccessLevel


def test_get_file(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu_proj.seed_random_project(current_user.id)
  subp = tu_proj.seed_random_subproject(current_user.id, project.id)
  
  
  tmp_file = tempfile.SpooledTemporaryFile()
  tmp_file.write(b"Hello World!")
  
  post_file = models.StoredFilePost(
    filename="hello",
    owner_id=current_user.id,
    extension=".txt",
    file_object=tmp_file,
    subproject_id=subp.id
  )
  saved_file = impl.impl_save_file(post_file)
  
  #Act
  res = client.get(f"/api/core/files/{saved_file.id}/download",
                      headers=std_headers)
  
  #Assert
  assert res.status_code == 200
  
  #Cleanup
  tu.delete_files([saved_file], [current_user])
  tu_proj.delete_subprojects([subp])
  tu_proj.delete_projects([project])


def test_delete_file_admin(client, admin_headers, admin_user):
  #Setup
  std_user = tu_users.seed_random_user(admin=False, disabled=False)
  adm_user = impl_users.impl_get_user_with_username(admin_user.username)
  project = tu_proj.seed_random_project(std_user.id, {adm_user.id: AccessLevel.ADMIN})
  subp = tu_proj.seed_random_subproject(std_user.id, project.id)
  
  
  tmp_file = tempfile.SpooledTemporaryFile()
  tmp_file.write(b"Hello World!")
  
  post_file = models.StoredFilePost(
    filename="hello",
    owner_id=std_user.id,
    extension=".txt",
    file_object=tmp_file,
    subproject_id=subp.id
  )
  saved_file = impl.impl_save_file(post_file)
  
  #Act
  res = client.delete(f"/api/core/files/{saved_file.id}/delete",
                      headers=admin_headers)
  
  #Assert
  assert res.status_code == 200
  
  #Cleanup
  tu_proj.delete_subprojects([subp])
  tu_proj.delete_projects([project])
  tu_users.delete_users([std_user])
  
  


def test_delete_file_standard(client, std_headers, std_user):
  #Setup
  file_owner = tu_users.seed_random_user(admin=False, disabled=False)
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu_proj.seed_random_project(file_owner.id, {current_user.id: AccessLevel.READONLY})
  subp = tu_proj.seed_random_subproject(file_owner.id, project.id)
  
  
  tmp_file = tempfile.SpooledTemporaryFile()
  tmp_file.write(b"Hello World!")
  
  post_file = models.StoredFilePost(
    filename="hello",
    owner_id=file_owner.id,
    extension=".txt",
    file_object=tmp_file,
    subproject_id=subp.id
  )
  saved_file = impl.impl_save_file(post_file)
  
  #Act
  res = client.delete(f"/api/core/files/{saved_file.id}/delete",
                      headers=std_headers)
  
  #Assert
  assert res.status_code == 403 #403 forbidden, should not be able to access resource
  
  #Cleanup
  tu_proj.delete_subprojects([subp])
  tu_proj.delete_projects([project])
  tu_users.delete_users([file_owner])
  


def test_delete_file_owner(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu_proj.seed_random_project(current_user.id)
  subp = tu_proj.seed_random_subproject(current_user.id, project.id)
  
  
  tmp_file = tempfile.SpooledTemporaryFile()
  tmp_file.write(b"Hello World!")
  
  post_file = models.StoredFilePost(
    filename="hello",
    owner_id=current_user.id,
    extension=".txt",
    file_object=tmp_file,
    subproject_id=subp.id
  )
  saved_file = impl.impl_save_file(post_file)
  
  #Act
  res = client.delete(f"/api/core/files/{saved_file.id}/delete",
                      headers=std_headers)
  
  #Assert
  assert res.status_code == 200
  
  #Cleanup
  tu_proj.delete_subprojects([subp])
  tu_proj.delete_projects([project])
  