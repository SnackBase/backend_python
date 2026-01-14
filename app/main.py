from contextlib import asynccontextmanager

import urllib3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data.connector import create_db_and_tables
from app.settings import get_settings
from app.api.endpoints.product import router as product_router
from app.api.endpoints.user import router as user_router
from app.api.endpoints.order import router as order_router
from app.api.endpoints.payment import router as payment_router
from app.api.endpoints.balance import router as balance_router

settings = get_settings()

# Disable SSL warnings when SSL verification is disabled for internal Docker network communication
if not settings.auth_ssl_verify:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Backend API for DrinkBar",
    description="This API provides database connectivity and data validation.",
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
app.include_router(user_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(balance_router)
