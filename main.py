from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware

import main_router as api
import setup
import env


# Parse environment variables
env.Environment.parse_env()


# setup.config_default_logging()

app = FastAPI(
    title="SED lab API",
    description="The SED lab API contains all HTTP operations available within the SED lab application.",
    version="1.0.0",
)

app.include_router(api.router, prefix="/api")

# CORS
origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Misc middleware
# setup.install_middleware(app)

origins = [
    "http://localhost:8080",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
