# sed-backend
This project contains the SED Lab back-end. It consists of a core API containing functionality such as authentication, and a structure that supports other applications to be weaved in, as well as a common library.

# Installation

## Prerequisites
- Python 3.8
- MySQL server

## Setup
- Run `mysql -h localhost -u root -p < setup.sql` (or you could use MySQL Workbench to execute the code inside setup.sql)
- Run `pip install -r requirements.txt` (you may need to install some requirements, such as uvicorn, manually)
- Run `uvicorn main:app --reload` from project root to launch the application
- Go to http://localhost:8000/docs to get an overview of the API

## Create an initial admin user for development purposes
Use the following MySQL query to create a user with the admin role:

```INSERT INTO users (`username`, `password`,`scopes`, `disabled`) VALUES ('admin', '$2b$12$HrAma.HCdIFuHtnbVcle/efa9luh.XUqZapqFEUISj91TKTN6UgR6', 'admin', False)```

- username: admin
- password: secret

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
