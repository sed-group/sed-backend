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
- Check if it is working by surfing to `http://localhost/docs`

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
- cd to `sed-backend/apps/core`, where you will find the setup.sql file needed to setup the core database.
- Run `mysql -h localhost -u root -p < setup.sql` (or you could use MySQL Workbench to execute the code inside setup.sql)
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

# Logging
Logging is done using FastAPI's own logging module (which is based on the standard Python Logger). Use like this: 
```
from fastapi.logger import logger

logger.debug('Use for debugging applications')
logger.info('Useful information')
logger.warn('Something might be wrong')
logger.error('Something is definitely wrong')

```  
By default, the log is saved in the system TEMP directory: `%TEMP%/sed-backend.log`.
