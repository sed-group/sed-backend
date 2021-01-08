from fastapi import FastAPI

import main_router as api
import setup


setup.config_default_logging()

app = FastAPI(
    title="SED lab API",
    description="The SED lab API contains all HTTP operations available within the SED lab application.",
    version="1.0.0",
    redoc_url=None
)

app.include_router(api.router, prefix="/api")

setup.install_middleware(app)
