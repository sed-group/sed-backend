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
    global testTreeID
    
    # test tree
    response = client.post(
        urlPrefix + "/trees/",
        json={"name": "foobar",  "description": "The Foo Barters"}
    )
    assert response.status_code == 200

    testTreeData = response.json()
    testTreeID = testTreeData['id']

    testTopLevelDSid = testTreeData['topLvlDSid']

    assert testTreeData == {
        "name": "foobar",
        "description": "The Foo Barters",
        "id": testTreeID,
        "concepts": [],
        # "fr": [],
        # "ds": [],
        "topLvlDSid": testTopLevelDSid,
        "topLvlDS":  {
            'id': testTopLevelDSid,
            'name': 'foobar',
            'description': 'Top-level DS',
            'is_top_level_DS': True,
            'treeID': testTreeID,
            'isbID': None,
            'requires_functions': [],
            "interacts_with": [],
            "design_parameters": []
        }
    }

    # test Top level DS:
    topLvlDS = client.get(urlPrefix + '/ds/' + str(testTopLevelDSid))

    assert topLvlDS.status_code == 200

# access non-existent tree
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
    global testTreeID
    global allFRID
    
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


    
    

# edit tree

# edit FR

# edit DS

# delete FR

# delete DS

# delete tree


## EF-M logic tests

# create tree with FR-DS tree

# instantiate concepts

# edit elements, reinstantiate
