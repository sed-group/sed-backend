import tests.testutils as tu
import tests.apps.core.projects.testutils as tu_projects
import tests.apps.core.users.testutils as tu_users
import apps.core.users.implementation as impl_users
import apps.core.projects.implementation as impl
import apps.core.projects.models as proj_models
import apps.EFMbackend.schemas as schemas
from fastapi.logger import logger

# test data: 
TEST_TREE = {
    'name': 'efm test tree',
    'description': 'A EFM test tree for pytest',
    'top_level_ds_id': None,
    'subproject_id': None,
    'id': None,
}

FR_1 = {
    'name': 'Function 1',
    'description': 'a test function the product has to perform',
    id: None,
    'tree_id': None,
    'rf_id': None,
}

FR_2 = {
    'name': 'Function 2',
    'description': 'another test function the product has to perform',
    id: None,
    'tree_id': None,
    'rf_id': None,
}

DS_1A = {
    'name': 'Design Solution A for FR 1',
    'description': 'this is just a test DS, alternative A',
    'id': None,
    'tree_id': None,
    'is_top_level_ds': False,
    'isb_id': None,
}

DS_1B = {
    'name': 'Design Solution B for FR 1',
    'description': 'this is just a test DS, alternative A',
    'id': None,
    'tree_id': None,
    'is_top_level_ds': False,
    'isb_id': None,
}

IW_1A_1B = {
    'description': 'interaction between DS 1A and 1B',
    'id': None,
    'tree_id': None,
    'from_ds_id': None,
    'to_ds_id': None,
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

urlPrefix = "/api/efm"

## GLOBAL TESTING VARIABLES
testTreeID = 0
allFRID = []
allDSID = []

### BASIC TESTS ##################################################


def test_create_tree(client, std_headers, std_user):

    # setup (project generation)
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id, participants={
        current_user.id: proj_models.AccessLevel.ADMIN
    })
    
    # generate test tree data
    tree_data = schemas.TreeNew(**TEST_TREE_DATA)

    # test
    response = client.post(
        urlPrefix + f"/{p.id}/newTree/",
        headers=std_headers,
        json=tree_data.dict()
    )

    # assert status code
    assert response.status_code == 200

    response_tree = response.json()
    # TEST_TREE['id'] = response_tree['id']

    # TEST_TREE['top_level_ds_id'] = response_tree['top_level_ds_id']
    # TEST_TREE['subproject_id'] = response_tree['subproject_id']

    assertion_tree_data = schemas.TreeInfo(**TEST_TREE_DATA)
    assertion_tree_data.id = response_tree['id']
    assertion_tree_data.top_level_ds_id = response_tree['top_level_ds_id']

    assert response_tree == assertion_tree_data.dict()

    # test whether Top level DS exists:
    get_ds_url = f"{urlPrefix}/{assertion_tree_data.id}/ds/{assertion_tree_data.top_level_ds_id}"
    top_lvl_ds = client.get(
        get_ds_url,
        headers=std_headers,
        )
    # logger.info(assertion_tree_data)
    
    assert top_lvl_ds.status_code == 200

    # cleanup
    tu_projects.delete_projects([p])


def test_full_tree_insertion():
    pass

# # access non-existent tree & other objects
# def test_acces_nonexistent_objects(client, std_headers, std_user):

#     # setup (project generation)
#     current_user = impl_users.impl_get_user_with_username(std_user.username)
#     p = tu_projects.seed_random_project(current_user.id, participants={
#         current_user.id: proj_models.AccessLevel.ADMIN
#     })

#     # tree via string
#     response = client.get(urlPrefix + '/trees/' + "test")
#     assert response.status_code == 422
#     # tree via nonexisting ID
#     response = client.get(urlPrefix + '/trees/' + str(99))
#     assert response.status_code == 404
#     # tree via nonexisting ID (0)
#     response = client.get(urlPrefix + '/trees/' + str(0))
#     assert response.status_code == 404

#     ## DS via string
#     response = client.get(urlPrefix + '/ds/' + "wrong")
#     assert response.status_code == 422 # bad request
#     ## DS via nonexisting ID
#     response = client.get(urlPrefix + '/ds/' + str(99))
#     assert response.status_code == 404 # not found
#     ## DS via nonexisting ID (0)
#     response = client.get(urlPrefix + '/ds/' + str(0))
#     assert response.status_code == 404


#     # FR via nonexisting string
#     response = client.get(urlPrefix + '/fr/' + "fr")
#     assert response.status_code == 422
#     # FR via nonexisting ID
#     response = client.get(urlPrefix + '/fr/' + str(99))
#     assert response.status_code == 404
#     # FR via nonexisting ID (0)
#     response = client.get(urlPrefix + '/fr/' + str(0))
#     assert response.status_code == 404

# # create FR, DS
# def test_create_basic_objects():
#     global TEST_TREE    
#     global DS_1A
#     global DS_1B
#     global FR_1
#     global FR2
    
#     # create FR in testTree, as child of top_lvl_ds
#     # first we need to get the top_lvl_ds ID:
#     print("test_create_basic_objects testTreeID:" + str(testTreeID)) 
#     testTreeUrl = urlPrefix + '/trees/' +str(testTreeID)
#     testTree =  client.get(testTreeUrl)

#     assert testTree.status_code == 200
#     response_tree = testTree.json()

#     print("testing TREE: url {}, RESPONSE: status: {}, json: {}".format(testTreeUrl, testTree.status_code, response_tree))

#     testTopLevelDSid = response_tree['top_lvl_dsid']


#     # creating three top lvl FR:
#     for i in range(1,4):
#         newFRdata = {
#             "name": f"Test function {i}",
#             "description": f"Top level function number {i}",
#             "treeID": testTreeID,
#             "rfID": testTopLevelDSid
#             }
#         newFRurl = urlPrefix + "/fr/new"
#         responseFR = client.post(
#             newFRurl,
#             json = newFRdata,
#             )

#         print("testing FR: url {}, json: {}".format(newFRurl, newFRdata))
#         print(responseFR.json() )

#         assert responseFR.status_code == 200
#         theFRdata = responseFR.json()
#         theFRid = theFRdata['id']
#         assert theFRdata == {
#             "name": f"Test function {i}",
#             "id": theFRid,
#             "description": f"Top level function number {i}",
#             "treeID": testTreeID,
#             "rfID": testTopLevelDSid,
#             "is_solved_by": []
#         }

#         allFRID.append(theFRid)

#         # check whether top_lvl_ds now has theFR as a "requires_function"
#         requestTopLvlDS = client.get(urlPrefix + '/ds/' + str(testTopLevelDSid))
#         top_lvl_dsdata = requestTopLvlDS.json()
#         assert theFRid in top_lvl_dsdata['requires_functions_id']

#         # create DS as child of FR above
#         for ii in range(1,i+1):
#             theDSdata = {
#                 "name": f"DS {ii} for FR {i}",
#                 "description": f"One of {i} alternatives solutions",
#                 "treeID": testTreeID,
#                 "isbID": theFRid
#             }
#             responseDS = client.post(
#                 urlPrefix + '/ds/new',
#                 json = theDSdata,
#             )


#             assert responseDS.status_code == 200
#             theDSdata = responseDS.json()
#             theDSid = theDSdata['id']
#             assert theDSdata == {
#                 "id": theDSid,
#                 "name": f"DS {ii} for FR {i}",
#                 "description": f"One of {i} alternatives solutions",
#                 "treeID": testTreeID,
#                 "isbID": theFRid,
#                 "is_top_level_DS": False,
#                 "requires_functions": [],
#                 'interacts_with': [],
#                 'design_parameters': []
#             }

#             # check whether theFR now has theDS as a "is_solved_by"
#             requestFR2 = client.get(urlPrefix + '/fr/' + str(theFRid))
#             FR2data = requestFR2.json()
#             assert theDSid in FR2data['is_solved_by_id']

#             allDSID.append(theDSid)

# # create iw
# def test_create_iw():
#     global testTreeID
#     global allDSID

#     # pick the first 2 DS frim allDSID
#     DS1id = allDSID[0]
#     DS2id = allDSID[2]

#     theNewIWdata = {
#         'fromDsID': DS1id,
#         'toDsID': DS2id,
#         'iwType': 'spatial'
#     }

#     response = client.post(
#                 urlPrefix + '/iw/new',
#                 json = theNewIWdata,
#                 )
    
#     ## assert status
#     assert response.status_code ==200
#     responseData = response.json()
#     theIWid = responseData['id']
    
#     ## assert returndata
#     assert responseData == {
#         'id': theIWid,
#         'treeID': testTreeID,
#         'fromDsID': DS1id,
#         'toDsID': DS2id,
#         'iwType': 'spatial'
#     }

#     ## assert that the iw is listed in the DS:
#     theDS1response = client.get(urlPrefix + '/ds/'+ str(DS1id))
#     theDS1 = theDS1response.json()
#     assert theIWid in theDS1['interacts_with_id']

# # create iw in alternative instances (--> 400)
# def test_create_bad_iw():
#     global testTreeID
#     global allFRID

#     # allFRID[1] should have two alternative DS
#     theFRresponse = client.get(urlPrefix + '/fr/' + str(allFRID[1]))
#     # assert theFRresponse.status_code == 200

#     theFR = theFRresponse.json()

#     DS1id = theFR['is_solved_by_id'][0]
#     DS2id = theFR['is_solved_by_id'][1]
    
#     theNewIWdata = {
#         'fromDsID': DS1id,
#         'toDsID': DS2id,
#         'iwType': 'spatial'
#     }

#     iwResponse = client.post(
#         urlPrefix + '/iw/new',
#         json = theNewIWdata,
#     )

#     assert iwResponse.status_code == 400

# # edit tree
# def test_edit_tree():
#     global testTreeID
#     newTreeData = {
#         'name': 'a new tree name',
#         'description': 'an edited description'
#     }

#     response = client.put(urlPrefix + '/trees/' + str(testTreeID), newTreeData)

#     assert response.status_code == 200

#     responseData = response.json()
#     top_lvl_dsid = responseData['top_lvl_dsid']
    
#     assert responseData == {
#         'id': testTreeID,
#         'name': 'a new tree name',
#         'description': 'an edited description',
#         'top_lvl_dsid': top_lvl_dsid
#     }

# # edit FR

# # edit DS

# # delete FR
# def test_delete_FR():
#     global testTreeID
#     pass


# delete DS

# delete tree


## EF-M logic tests

# create tree with FR-DS tree

# instantiate concepts

# edit elements, reinstantiate
