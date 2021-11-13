from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from apps.EFMbackend.models import Base
from apps.EFMbackend.router import get_db

## test DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

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

# override testDB
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# test client setup
client = TestClient(app)

urlPrefix = "/api/efm"

## GLOBAL TESTING VARIABLES
testTreeID = 0
allFRID = []
allDSID = []

### BASIC TESTS ##################################################
# create tree
def test_create_tree():
    global TEST_TREE    
    
    # test tree
    response = client.post(
        urlPrefix + "/trees/",
        json={  
            "name": TEST_TREE['name'], 
            "description": TEST_TREE['description']
            }
    )
    assert response.status_code == 200

    testTreeData = response.json()
    TEST_TREE['id'] = testTreeData['id']

    TEST_TREE['top_level_ds_id'] = testTreeData['top_level_ds_id']
    TEST_TREE['subproject_id'] = testTreeData['subproject_id']

    assert testTreeData == {
        "name": TEST_TREE['name'],
        "description":TEST_TREE['description'],
        "id": TEST_TREE['id'],
        "top_level_ds_id": TEST_TREE['top_level_ds_id'],
        'subproject_id': TEST_TREE['subproject_id']   
    }

    # test Top level DS:
    topLvlDS = client.get(urlPrefix + '/ds/' + str(TEST_TREE['top_level_ds_id']))

    assert topLvlDS.status_code == 200

# access non-existent tree & other objects
def test_acces_nonexistent_objects():

    # tree via string
    response = client.get(urlPrefix + '/trees/' + "test")
    assert response.status_code == 422
    # tree via nonexisting ID
    response = client.get(urlPrefix + '/trees/' + str(99))
    assert response.status_code == 404
    # tree via nonexisting ID (0)
    response = client.get(urlPrefix + '/trees/' + str(0))
    assert response.status_code == 404

    ## DS via string
    response = client.get(urlPrefix + '/ds/' + "wrong")
    assert response.status_code == 422 # bad request
    ## DS via nonexisting ID
    response = client.get(urlPrefix + '/ds/' + str(99))
    assert response.status_code == 404 # not found
    ## DS via nonexisting ID (0)
    response = client.get(urlPrefix + '/ds/' + str(0))
    assert response.status_code == 404


    # FR via nonexisting string
    response = client.get(urlPrefix + '/fr/' + "fr")
    assert response.status_code == 422
    # FR via nonexisting ID
    response = client.get(urlPrefix + '/fr/' + str(99))
    assert response.status_code == 404
    # FR via nonexisting ID (0)
    response = client.get(urlPrefix + '/fr/' + str(0))
    assert response.status_code == 404

# create FR, DS
def test_create_basic_objects():
    global TEST_TREE    
    global DS_1A
    global DS_1B
    global FR_1
    global FR2
    
    # create FR in testTree, as child of topLvlDS
    # first we need to get the topLvlDS ID:
    print("test_create_basic_objects testTreeID:" + str(testTreeID)) 
    testTreeUrl = urlPrefix + '/trees/' +str(testTreeID)
    testTree =  client.get(testTreeUrl)

    assert testTree.status_code == 200
    testTreeData = testTree.json()

    print("testing TREE: url {}, RESPONSE: status: {}, json: {}".format(testTreeUrl, testTree.status_code, testTreeData))

    testTopLevelDSid = testTreeData['topLvlDSid']


    # creating three top lvl FR:
    for i in range(1,4):
        newFRdata = {
            "name": f"Test function {i}",
            "description": f"Top level function number {i}",
            "treeID": testTreeID,
            "rfID": testTopLevelDSid
            }
        newFRurl = urlPrefix + "/fr/new"
        responseFR = client.post(
            newFRurl,
            json = newFRdata,
            )

        print("testing FR: url {}, json: {}".format(newFRurl, newFRdata))
        print(responseFR.json() )

        assert responseFR.status_code == 200
        theFRdata = responseFR.json()
        theFRid = theFRdata['id']
        assert theFRdata == {
            "name": f"Test function {i}",
            "id": theFRid,
            "description": f"Top level function number {i}",
            "treeID": testTreeID,
            "rfID": testTopLevelDSid,
            "is_solved_by": []
        }

        allFRID.append(theFRid)

        # check whether topLvlDS now has theFR as a "requires_function"
        requestTopLvlDS = client.get(urlPrefix + '/ds/' + str(testTopLevelDSid))
        topLvlDSdata = requestTopLvlDS.json()
        assert theFRid in topLvlDSdata['requires_functions_id']

        # create DS as child of FR above
        for ii in range(1,i+1):
            theDSdata = {
                "name": f"DS {ii} for FR {i}",
                "description": f"One of {i} alternatives solutions",
                "treeID": testTreeID,
                "isbID": theFRid
            }
            responseDS = client.post(
                urlPrefix + '/ds/new',
                json = theDSdata,
            )


            assert responseDS.status_code == 200
            theDSdata = responseDS.json()
            theDSid = theDSdata['id']
            assert theDSdata == {
                "id": theDSid,
                "name": f"DS {ii} for FR {i}",
                "description": f"One of {i} alternatives solutions",
                "treeID": testTreeID,
                "isbID": theFRid,
                "is_top_level_DS": False,
                "requires_functions": [],
                'interacts_with': [],
                'design_parameters': []
            }

            # check whether theFR now has theDS as a "is_solved_by"
            requestFR2 = client.get(urlPrefix + '/fr/' + str(theFRid))
            FR2data = requestFR2.json()
            assert theDSid in FR2data['is_solved_by_id']

            allDSID.append(theDSid)

# create iw
def test_create_iw():
    global testTreeID
    global allDSID

    # pick the first 2 DS frim allDSID
    DS1id = allDSID[0]
    DS2id = allDSID[2]

    theNewIWdata = {
        'fromDsID': DS1id,
        'toDsID': DS2id,
        'iwType': 'spatial'
    }

    response = client.post(
                urlPrefix + '/iw/new',
                json = theNewIWdata,
                )
    
    ## assert status
    assert response.status_code ==200
    responseData = response.json()
    theIWid = responseData['id']
    
    ## assert returndata
    assert responseData == {
        'id': theIWid,
        'treeID': testTreeID,
        'fromDsID': DS1id,
        'toDsID': DS2id,
        'iwType': 'spatial'
    }

    ## assert that the iw is listed in the DS:
    theDS1response = client.get(urlPrefix + '/ds/'+ str(DS1id))
    theDS1 = theDS1response.json()
    assert theIWid in theDS1['interacts_with_id']

# create iw in alternative instances (--> 400)
def test_create_bad_iw():
    global testTreeID
    global allFRID

    # allFRID[1] should have two alternative DS
    theFRresponse = client.get(urlPrefix + '/fr/' + str(allFRID[1]))
    # assert theFRresponse.status_code == 200

    theFR = theFRresponse.json()

    DS1id = theFR['is_solved_by_id'][0]
    DS2id = theFR['is_solved_by_id'][1]
    
    theNewIWdata = {
        'fromDsID': DS1id,
        'toDsID': DS2id,
        'iwType': 'spatial'
    }

    iwResponse = client.post(
        urlPrefix + '/iw/new',
        json = theNewIWdata,
    )

    assert iwResponse.status_code == 400

# edit tree
def test_edit_tree():
    global testTreeID
    newTreeData = {
        'name': 'a new tree name',
        'description': 'an edited description'
    }

    response = client.put(urlPrefix + '/trees/' + str(testTreeID), newTreeData)

    assert response.status_code == 200

    responseData = response.json()
    topLvlDSid = responseData['topLvlDSid']
    
    assert responseData == {
        'id': testTreeID,
        'name': 'a new tree name',
        'description': 'an edited description',
        'topLvlDSid': topLvlDSid
    }

# edit FR

# edit DS

# delete FR
def test_delete_FR():
    global testTreeID
    pass


# delete DS

# delete tree


## EF-M logic tests

# create tree with FR-DS tree

# instantiate concepts

# edit elements, reinstantiate
