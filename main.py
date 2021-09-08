import os
import os.path as path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import main_router as api
import setup


setup.config_default_logging()

app = FastAPI(
    title="SED lab API",
    description="The SED lab API contains all HTTP operations available within the SED lab application.",
    version="1.0.0",
)

app.include_router(api.router, prefix="/api")

# Production specific logic
deploy_mode = os.getenv("SED_DEPLOY_MODE")
if deploy_mode == 'prod':
    # Set static content
    static_content_directory = '/var/www/static'
    if path.exists(static_content_directory):
        app.mount("/static", StaticFiles(directory="/var/www/static"), name="static")

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
setup.install_middleware(app)
