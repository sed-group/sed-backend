# sed-backend
This project contains the SED Lab back-end. It consists of a core API containing functionality such as authentication, and a structure that supports other applications to be weaved in, as well as a common library.

# WORK IN PROGRESS
- [x] Basic authentication
- [x] Standardized database connections
- [x] Users
- [x] Permissions/scopes
- [ ] Support for cookie based authentication

# Installation

## Prerequisites
- Python 3.8
- MySQL server

## Setup
- Run `mysql -h hostname -u user < setup.sql`
- Run `pip install -r requirements.txt`
- Run `uvicorn main:app --reload` from project root to launch the application
- Go to http://localhost:8000/docs to get an overview of the API
