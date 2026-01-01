from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import DirectoryPath, Field, HttpUrl, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Auth
    auth_client_secret: str = Field(
        description="Client Secret for the OIDC auth server (keycloak)"
    )
    auth_client_id: str = Field(
        description="Client ID for the OIDC auth server (keycloak)"
    )
    auth_url: HttpUrl = Field(
        description="Realm specific URL of the OIDC auth server (keycloak)"
    )

    @computed_field
    def auth_url_str(self) -> str:
        return self.oidc_url.encoded_string()

    # DB
    db_dsn: PostgresDsn = Field(description="DSN fot the database conenction")

    # Data
    data_root_dir: DirectoryPath = Path("./data")

    # Scopes
    admin_scope: str = "admin"
    customer_scope: str = "customer"
    kiosk_scope: str = "kiosk"

    # Network
    port: int = Field(
        description="Port on which the application shoul run.",
        default=8000,
        ge=1,  # valid tcp/udp range lower limit
        le=65535,  # valid tcp/udp range upper limit
    )

    @computed_field
    def product_image_root_dir(self) -> Path:
        return self.data_root_dir / "products/image"

    model_config = SettingsConfigDict(env_file=(".env"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
