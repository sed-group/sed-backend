from mysql.connector.pooling import PooledMySQLConnection

import apps.EFMbackend.implementation as implementation
import apps.EFMbackend.schemas as schemas

import tests.testutils as tu
import tests.apps.core.projects.testutils as tu_projects
import tests.apps.core.users.testutils as tu_users
import apps.core.users.implementation as impl_users
import apps.core.projects.implementation as proj_impl
import apps.core.projects.models as proj_models

TEST_TREE_DATA = {
  "name": "Test tree",
  "description": "",
  "id": 30,
  "top_level_ds_id": 45,
  "ds": [
    {
      "name": "Test tree",
      "description": "Top-level DS",
      "isb_id": None,
      "tree_id": 30,
      "is_top_level_ds": True,
      "id": 45
    },
    {
      "name": "solution A1",
      "description": None,
      "isb_id": 17,
      "tree_id": 30,
      "is_top_level_ds": False,
      "id": 46
    },
    {
      "name": "Solution A2",
      "description": None,
      "isb_id": 18,
      "tree_id": 30,
      "is_top_level_ds": False,
      "id": 47
    },
    {
      "name": "Solution B2",
      "description": "description solution b2 ",
      "isb_id": 18,
      "tree_id": 30,
      "is_top_level_ds": False,
      "id": 48
    }
  ],
  "fr": [
    {
      "name": "Function 1",
      "description": "description function 1",
      "tree_id": 30,
      "rf_id": 45,
      "id": 17
    },
    {
      "name": "Function 2",
      "description": "description function 2",
      "tree_id": 30,
      "rf_id": 45,
      "id": 18
    }
  ],
  "iw": [
    {
      "tree_id": 30,
      "iw_type": "spatial",
      "description": None,
      "from_ds_id": 46,
      "to_ds_id": 47,
      "id": 8
    },
    {
      "tree_id": 30,
      "iw_type": "spatial",
      "description": None,
      "from_ds_id": 48,
      "to_ds_id": 46,
      "id": 9
    }
  ],
  "dp": [],
  "c": [
    {
      "name": "Constraint for A1",
      "description": "",
      "tree_id": 30,
      "icb_id": 46,
      "id": 2
    },
    {
      "name": "Second constraint for A1",
      "description": "",
      "tree_id": 30,
      "icb_id": 46,
      "id": 3
    },
    {
      "name": "Constraint for A2",
      "description": "",
      "tree_id": 30,
      "icb_id": 47,
      "id": 4
    }
  ]
}

def create_tree(db: PooledMySQLConnection):
    # setup (project generation)
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id, participants={
        current_user.id: proj_models.AccessLevel.ADMIN
    })
    
    tree = implementation.create_tree(
        db = db,
        project_id = p.id,
        new_tree = tree_data,
        user_id = current_user.id
        )

    # generate test tree data
    tree_data = schemas.TreeNew(**TEST_TREE_DATA)

    return {
        'tree_data': tree,
        'tree_id': tree.id,
        'top_lvl_ds_id': tree.top_level_ds_id,
        'project_id': p.id,
        'user_id': current_user.id,
    }

def delete_tree(db: PooledMySQLConnection, tree_id: int):
    pass