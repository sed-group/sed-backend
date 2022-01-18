# test data: 
TEST_TREE = {
    'name': 'efm test tree',
    'description': 'A EFM test tree for pytest',
    'top_level_ds_id': 0,
    'subproject_id': 0,
    'id': 0,
}

FR_1 = {
    'name': 'Function 1',
    'description': 'a test function the product has to perform',
    'tree_id': 0,
    'rf_id': 0,
}

FR_2 = {
    'name': 'Function 2',
    'description': 'another test function the product has to perform',
    'id': 0,
    'tree_id': 0,
    'rf_id': 0,
}

DS_1A = {
    'name': 'Design Solution A for FR 1',
    'description': 'this is just a test DS, alternative A',
    'id': 0,
    'tree_id': 0,
    'is_top_level_ds': False,
    'isb_id': 0,
}

DS_1B = {
    'name': 'Design Solution B for FR 1',
    'description': 'this is just a test DS, alternative A',
    'id': 0,
    'tree_id': 0,
    'is_top_level_ds': False,
    'isb_id': 0,
}

IW_1A_1B = {
    'description': 'interaction between DS 1A and 1B',
    'id': 0,
    'tree_id': 0,
    'from_ds_id': 0,
    'to_ds_id': 0,
    'iw_type': 'energy',
}

TEST_TREE_DATA = {
  "name": "Test tree",
  "description": "",
  "id": 30,
  "top_level_ds_id": 45,
  "ds": [
    {
      "name": "Test tree",
      "description": "Top-level DS",
      "isb_id": 0,
      "tree_id": 30,
      "is_top_level_ds": True,
      "id": 45
    },
    {
      "name": "solution A1",
      "description": 0,
      "isb_id": 17,
      "tree_id": 30,
      "is_top_level_ds": False,
      "id": 46
    },
    {
      "name": "Solution A2",
      "description": 0,
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
      "description": 0,
      "from_ds_id": 46,
      "to_ds_id": 47,
      "id": 8
    },
    {
      "tree_id": 30,
      "iw_type": "spatial",
      "description": 0,
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