# sed-backend
This project contains the SED Lab back-end. It consists of a core API containing functionality such as authentication, and a structure that supports other applications to be weaved in, as well as a common library.

# Installation

## Docker
Docker will automagically do everything (well, almost) for you.

### Prerequisites
- Docker (and docker-compose, though they seem to come as a package)

### Setup
This setup guide will take you through how to get the sed-backend application and the database up and running

- Go to the root directory of the project. There should be a file called docker-compose.yml in that directory.
- Run `docker-compose build`
- Run `docker-compose up -d`
- Check if it is working by surfing to `http://localhost:8000/docs`

That's it. If you change anything in the FastAPI application, then you need to rebuild. 
But before you build it is advisable to first shut down your containers. These operations can be done like this:
- run `docker-compose down`
- run `docker-compose build` again.
- Run `docker-compose up -d` again.

### Manual docker setup 
This is for documentation purposes. If docker-compose is working, then you should probably use that instead.

**Backend**

- Pull the project
- cd to the project directory
- run `docker network create --driver bridge sedlab`. This will create a shared network so that the containers can communicate with each other.
- run `docker build -f Dockerfile-backend-api -t sed-backend-img .`. This will create the docker image using the Dockerfile situated in this directory.
- run `docker run -d --name sed-backend -p 80:80 --network sedlab sed-backend-img`. This will create the docker container using the image, and include it into the sedlab network.
- Check if it worked. Log on to `http://localhost/docs`. You should be seeing the API documentation. However, since the database is not plugged in, most things won't be operational.

**Database**

- cd to the project directory
- run `cd apps/core`
- run `docker build -f Dockerfile-core-db -t sed-backend-core-db-img .`
- run `docker run -d --name sed-backend-core-db -p 3010:3306 --network sedlab sed-backend-core-db-img`

**Finally**

Now that you have both containers in place, restart the sed-backend container. The sed-backend container needs to be started LAST to ensure that all database containers are online during startup.
- run `docker restart sed-backend`

## Setup for application development
While you **could** use the docker-compose setup for development, you might find it worthwhile 
to at least run your FastAPI application the "old fashioned way". Why? Because you won't
have the benefits of "hot swap" if you are using docker, as with docker you need to rebuild
everytime something in the application is changed. 
However, if you don't want to change anything in the databases, then you could use docker to contain only the databases.

### Prerequisites
- Python 3.8
- MySQL server

### Setup
- cd to `sed-backend/sql/`, where you will find the sql files needed to setup the core database.
- Run `mysql -h localhost -u root -p` (or, use MySQL workbench which is easier) and execute the following code:
```
# This code creates a MySQL user with read and write access. 
# It will be used by the sed-backend to access and edit the database

CREATE USER IF NOT EXISTS 'rw' IDENTIFIED BY 'DONT_USE_IN_PRODUCTION!';
GRANT SELECT, INSERT, UPDATE, DELETE ON * TO 'rw';
GRANT EXECUTE ON `seddb`.* TO 'rw'@'%';
```
- Exit MySQL
- Run `mysql -h localhost -u root -p < V1__base.sql` (or you could use MySQL Workbench to execute the code)
- Run `pip install -r requirements.txt` 
- You may need to install some requirements, such as uvicorn and jose, manually. To do this, run `pip install uvicorn jose`
- Run `uvicorn main:app --reload` from project root to launch the application
- Go to http://localhost:8000/docs to get an overview of the API

### Using databases that are contained by docker
If you develop the application, but want to have your databases in docker, you need to go to all db.py-files and edit 
the host parameter such that it refers to localhost instead. You will also probably need to change the port numbers. 
The exposed port numbers are defined in docker-compose.yml

**Remember to never commit these changes** as they will break the environment for anyone who is using docker.

### Create an initial admin user for development purposes
Use the following MySQL query to create a user with the admin role:

```INSERT INTO users (`username`, `password`,`scopes`, `disabled`) VALUES ('admin', '$2b$12$HrAma.HCdIFuHtnbVcle/efa9luh.XUqZapqFEUISj91TKTN6UgR6', 'admin', False)```

- username: admin
- password: secret

# Development

## Module development
When creating a new module for the SED Lab backend, there are a few things that are good to be aware of.

### Step 1: Create an application description
Go to `applications.json` in the root directory of the SED-Backend project. Here you'll see a JSON list of all applications currently implemented into the backend. Note that each application has a "key" (e.g. the EF-M module has the key "MOD.EFM"). Create a key for your project, and follow the convention of the existing modules to create a description of your module. The `href_api` should have the same value as your API-prefix (remember this in the next sections).

### Step 2: Create an application module
Go to the folder `apps/` in the SED-backend catalogue. Here you will find every currently integrated module. Create a folder here with the name of your application module. This folder will contain ALL of your code (with only a few exceptions). This means that you shouldn't ever have to change or add code to other modules, as it is important that they remain unchanged for compatibility purposes. All application modules have the same package structure, as seen in the later chapter of this readme, called "Package structure".

### Step 3: Adding your module API to the backend API
There is one file outside of your own module that needs to be appended to make your module API accessible, and that is `main_router.py` in the root directory of the project. This contains references to each application API (routers). Look at how other sub-routers have been implemented (e.g. Core and DIFAM), and implement your own sub-router in the same way. Remember to add an API-prefix (same as the one written in step 1), a tag, and the security dependency "verify_token" (this forces the user to be logged in if he/she wants to use your API).

### Step 4: The database
Unless your module for some reason requires it, all modules use the same database. A connection to this database can be gained through `apps.core.db.get_connection()` This is typically done in the implementation layer, see the section about package structure below. Secondly, to avoid complexity and variation between modules, all interactions with the database are done so using "Prepared statement" calls, rather than using an ORM. Thus, database requests can either be written manually (e.g. ``SELECT username FROM `users` WHERE `id`=?``) or you can use some abstraction layer (e.g. the one provided in `libs.mysqlutils`). Examples of abstracted SQL requests can be found in any `storage.py`-file in the core application module `apps.core` (e.g. `apps.core.projects.storage`)

## Package structure
It is important that we are consistent when developing packages, such that 1) problems can easily be identified, 2) each component of the code-base can easily be navigated, 3) prevent degradation of code over time. Th that end, packages are suggested to comply to the following structure:

![Client to database chain](https://github.com/sed-group/architecture/raw/main/img/20210813_Package.PNG?raw=true "System Architecture Overview")

Each application package contains (at least) 3-4 files: `router.py`, `implementation.py`, `storage.py` and/or `algorithms.py`. The code contained in these files make up the communication chain from client request to data insertion/extraction into the database. In the case of a request not utilizing the database (such as a request for a computation) should not utilize storage, but rather another file handling such algorithms (e.g. `algorithms.py`).

- The job of `router.py` is to define the API interface, and to relay requests on to its corresponding implementation.
- `models.py` contains all data structures needed to provide the functionality of the package. As a rule of thumb, if a new class is needed, it likely belongs in `models.py` (with few exceptions). To elaborate further: If you need a class that will be passed to/from the client through `router.py` then that class definitely belongs in `models.py`.
- The job of `implementation.py` is to ask for a database connection, and to pass the request on to the appropriate storage methods
- The job of `storage.py` is to perform the necessary database operations. Note that this package should be the only package that imports database-related packages (such as sqlalchemy or mysql-driver).
- The job of `algorithms.py` is to perform any detailed operations that is not database related. For instance, it could be a calculation, or a simulation, that for some reason needs to be outsourced to the back-end rather than run on the client side. Temporary sidenote (2021-10-06): we would now like to encourage you to put any algorithm-code in a separate repository, and then import that code into the backend. If you are unsure about this ask Julian or Alejandro.
- The job of `exceptions.py`, is to contain all exceptions that your package can throw. Having all exceptions gathered in a single file makes them easy to find and import for any code that needs to catch (or "except") them.


## Logging
Logging is done using FastAPI's own logging module (which is based on the standard Python Logger). Use like this: 
```
from fastapi.logger import logger

logger.debug('Use for debugging applications')
logger.info('Useful information')
logger.warn('Something might be wrong')
logger.error('Something is definitely wrong')

```  
By default, the log is saved in the system TEMP directory: `%TEMP%/sed-backend.log`.

# Automated tests
To execute automated tests, you need to have __pytest__ installed (`pip install pytest`).
To run the automated tests manually, go to the project root and run `pytest`. This will automatically find and 
run all available tests in the project.

## Write tests
All tests are found in the tests-directory. The tests directory mirrors the directory-structure of the 
rest of the project. For instance, tests related to `apps/core/users` are located in 
`tests/apps/core/users/users_tests.py`. Tests are typically divided into 4 steps: 

- __Setup__: Set the stage for the test
- __Act__: Perform the action you want to test
- __Assert__: Check if your action had the intended results/consequences
- __Cleanup__: Reset the database and application state to as it was before the test started

During the __setup__ stage, you build the necessary state in the application needed to run a test. This could for 
instance be that you need to create a user, or a project, which you then want to perform a test on.
The __act__ stage is where you perform the action you want to test. For instance, you try to delete the project you 
created in the setup stage. During the __assert__ stage you check if your act actually had the intended results.
For instance, if your act was to delete a project, then in this step you check if the project still exists in 
the database. During the __cleanup__ stage you reset the state of the application to what it was before the test. This is 
critical, as not performing cleanup can cause other tests to fail. An example of cleanup is that you have a test that
creates a new User. You then test to assert that the user exists, then you delete the user during the cleanup stage.

Tests should ideally be written for all new functionality. Before you start I recommend that you study existing tests 
and how they work before writing your own tests. Some simple tests can be found in 
`tests/apps/core/users/test_users.py`.

One last thing: As a general rule of thumb, before pushing a new change to the remote repository, 
all tests should have passed. This helps us ensure that our application remains of adequate quality.

More reading, if you are interested: https://fastapi.tiangolo.com/tutorial/testing/

# Production deployment

## TL;DR
There are control scripts available on the server to facilitate safe and secure deployment of all 
assets (you're welcome). The control scripts can be found at `F:\control-scripts`.
Use those, and as long as it works you shouldn't have to worry.

## How it really works (in case something goes wrong)
In production (on the SED Server) things are a bit more complicated.
For starters, we have an extra docker-compose file which needs to be run after the first file for the server to start properly.
This can be done (BUT IT IS NOT SAFE) by running
- Go to project root
- Run `docker-compose -f docker-compose.yml -f docker-compose.prod.yml build`
- Run `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
- Done

This is all we need to start the web-server. But, in order to make it safe, we first need to change the contents 
of all files in the `env/` directory. This ensures that the passwords used are not the same 
ones that are publically available on github. To ease this, I've created some 
standardized launch/stop/rebuild-scripts that are available on the server.


The reason we need to setup production slightly differently is because we also need docker-compose to use the contents 
of `docker-compose.prod.yml` which contains setup instructions that are specific to the production environment. 
In short, `docker-compose.prod.yml` sets up a new docker container, which contains a TLS termination proxy 
using nginx. Incomming HTTPS traffic is handled by the nginx container, which translates it to HTTP for the 
FastAPI container. This allows FastAPI to communicate with HTTP within the docker network, 
while clients connecting to the API can communicate safely with HTTPS. 


TLS is achieved using a certbot certificate, which is mounted into the container in `docker-compose.prod.yml`. The `nginx/` directory contains the rest of the necessary files to make this work. Note that the setup requires knowledge of what the domain name is. At the time of writing, it was `sedlab.ppd.chalmers.se`. Attempting to deploy using the production composition on any other domain will not work without minor tweaks to the build code.

# Known issues

## Docker fails
The docker deployment can fail for many reasons. This section lists some of the more regular problems. If a container fails, click on that container in the docker desktop application and check what error has occuted.

### Incorrect line breaks
If the output of any container says:
`standard_init_linux.go:228: exec user process caused: no such file or directory`, then this is due to the windows line endings. This can usually be fixed by stopping the container, and running these commands in the repo:
```
git config core.autocrlf false 
git rm --cached -r . 
git reset --hard
```
These commands should set the appropriate line breaks. Rebuild using `docker-compose build` and restart all the components.

