from fastapi import FastAPI

import main_router as api

app = FastAPI()

app.include_router(api.router, prefix="/api")
