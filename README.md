# sed-backend
This project contains the SED Lab back-end. It consists of a core API containing functionality such as authentication, and a structure that supports other applications to be weaved in, as well as a common library.

# Installation

## Docker
Docker will automagically do everything (well, almost) for you.

### Prerequisites
- Docker

### Setup
This setup guide will take you through how to get the sed-backend application and the database up and running

**Backend**
- Pull the project
- cd to the project directory
- run `docker network create --driver bridge sedlab`. This will create a shared network so that the containers can communicate with each other.
- run `docker build -t sed-backend-img .`. This will create the docker image using the Dockerfile situated in this directory.
- run `docker run -d --name sed-backend -p 80:80 --network sedlab sed-backend-img`. This will create the docker container using the image, and include it into the sedlab network.
- Check if it worked. Log on to `http://localhost/docs`. You should be seeing the API documentation. However, since the database is not plugged in, most things won't be operational.

**Database**
- cd to the project directory
- run `cd apps/core`
- run `docker build -t sed-backend-core-db-img .`
- run `docker run -d --name sed-backend-core-db -p 3010:3306 --network sedlab sed-backend-core-db-img`

**Finally**
Now that you have both containers in place, restart the sed-backend container. The sed-backend container needs to be started LAST to ensure that all database containers are online during startup.
- run `docker restart sed-backend`

## Old school setup
So you're feeling fancy and you want to do it all by yourself even though there is an easy to use dockerfile? 
Very old school. Very cool.

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
