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


# EFM database setup
try:
    from apps.EFMbackend.database import engine as efmEngine
    from apps.EFMbackend.database import Base as efmBase
    efmBase.metadata.create_all(bind=efmEngine)
except:
    pass