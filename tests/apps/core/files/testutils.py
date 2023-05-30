from typing import List
import sedbackend.apps.core.files.implementation as impl
import sedbackend.apps.core.files.models as models
import sedbackend.apps.core.users.models as user_models

def delete_files(files: List[models.StoredFileEntry], users: List[user_models.User]):
  for i,file in enumerate(files):
    impl.impl_delete_file(file.id, users[i].id)