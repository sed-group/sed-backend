from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# EFM database setup
try:
    from apps.EFMbackend.database import engine as efmEngine
    from apps.EFMbackend.models import Base as efmBase
    efmBase.metadata.create_all(bind=efmEngine)
    print(" EFM databases created")
except:
    print(" /!\\ could not create EFM databases")