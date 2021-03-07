from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from apps.EFMbackend.database import Base
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
testProjectID = 0

### BASIC TESTS ##################################################
# create project
def test_create_project():
    global testProjectID
    
    # test project
    response = client.post(
        urlPrefix + "/projects/",
        json={"name": "foobar",  "description": "The Foo Barters"}
    )
    assert response.status_code == 200

    testProjectData = response.json()
    testProjectID = testProjectData['id']

    testTopLevelDSid = testProjectData['topLvlDSid']

    assert testProjectData == {
        "name": "foobar",
        "description": "The Foo Barters",
        "id": testProjectID,
        "concepts": [],
        "fr": [],
        "ds": [],
        "topLvlDSid": testTopLevelDSid
    }

    # test Top level DS:
    topLvlDS = client.get(urlPrefix + '/ds/' + str(testTopLevelDSid))

    assert topLvlDS.status_code == 200
    assert topLvlDS.json() == {
        'id': testTopLevelDSid,
        'name': 'foobar',
        'description': 'Top-level DS',
        'is_top_level_DS': True,
        'projectID': testProjectID,
        'isbID': None,
        'requires_functions': []
    }

# access non-existent project
def test_acces_nonexistent_objects():

    # project via string
    response = client.get(urlPrefix + '/projects/' + "test")
    assert response.status_code == 422
    # project via nonexisting ID
    response = client.get(urlPrefix + '/projects/' + str(99))
    assert response.status_code == 404
    # project via nonexisting ID (0)
    response = client.get(urlPrefix + '/projects/' + str(0))
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
    global testProjectID
    
    # create FR in testProject, as child of topLvlDS
    # first we need to get the topLvlDS ID:
    print("testProjectID:" + str(testProjectID)) 
    testProject =  client.get(urlPrefix + '/projects/' + str(testProjectID))
    assert testProject.status_code == 200
    testProjectData = testProject.json()
    testTopLevelDSid = testProjectData['topLvlDSid']

    # creating new FR:
    newFRdata = {
        "name": "testFunction",
        "description": "to test the FR creation",
        "projectID": testProjectID,
        "rfID": testTopLevelDSid
        }
    newFRurl = urlPrefix + "/ds/" + str(testTopLevelDSid) + "/newFR"
    responseFR = client.post(
        newFRurl,
        json = newFRdata,
        )

    print("testing: url {}, json: {}".format(newFRurl, newFRdata))
    print(responseFR.json() )

    assert responseFR.status_code == 200
    theFRdata = responseFR.json()
    theFRid = theFRdata['id']
    assert theFRdata == {
        "name": "testFunction",
        "id": theFRid,
        "description": "to test the FR creation",
        "projectID": testProjectID,
        "rfID": testTopLevelDSid,
        "is_solved_by": []
    }

    # check whether topLvlDS now has theFR as a "requires_function"
    requestTopLvlDS = client.get(urlPrefix + '/ds/' + str(testTopLevelDSid))
    topLvlDSdata = requestTopLvlDS.json()
    assert theFRdata in topLvlDSdata['requires_functions']


    # create DS as child of FR above
    theDSdata = {
        "name": "testDS",
        "description": "to test the DS creation",
        "projectID": testProjectID,
        "isbID": theFRid
    }
    responseDS = client.post(
        urlPrefix + '/fr/' + str(theFRid) + "/newDS",
        json = theDSdata,
    )


    assert responseDS.status_code == 200
    theDSdata = responseDS.json()
    theDSid = theDSdata['id']
    assert theDSdata == {
        "id": theDSid,
        "name": "testDS",
        "description": "to test the DS creation",
        "projectID": testProjectID,
        "isbID": theFRid,
        "is_top_level_DS": False,
        "requires_functions": []
    }

    # check whether theFR now has theDS as a "is_solved_by"
    requestFR2 = client.get(urlPrefix + '/fr/' + str(theFRid))
    FR2data = requestFR2.json()
    assert theDSdata in FR2data['is_solved_by']

    
    

# edit project

# edit FR

# edit DS

# delete FR

# delete DS

# delete project


## EF-M logic tests

# create project with FR-DS tree

# instantiate concepts

# edit elements, reinstantiate
