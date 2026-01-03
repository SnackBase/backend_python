from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data.connector import create_db_and_tables
from app.settings import get_settings
from app.api.endpoints.product import router as product_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Backend API for DrinkBar",
    description="This API provides database connectivity and database validation.",
    root_path="/api/v1",
    lifespan=lifespan,
    swagger_ui_init_oauth={  # see: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/
        "appName": "DrinkBar",
        "clientId": settings.auth_client_id_frontend,
        "clientSecret": settings.auth_client_secret_frontend,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product_router)
