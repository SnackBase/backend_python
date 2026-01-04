from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import DirectoryPath, Field, HttpUrl, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


OIDC_ENDPOINT = "/protocol/openid-connect"


class Settings(BaseSettings):
    # Auth
    auth_client_secret: str = Field(
        description="Client secret for the OIDC auth server (keycloak)"
    )
    auth_client_id: str = Field(
        description="Client ID for the OIDC auth server (keycloak)"
    )
    auth_client_secret_frontend: str = Field(
        description="Frontend client secret for the OIDC auth server (keycloak)"
    )
    auth_client_id_frontend: str = Field(
        description="Frontend client ID for the OIDC auth server (keycloak)"
    )
    auth_server_url: HttpUrl = Field(
        description="Realm specific URL of the OIDC auth server (keycloak)"
    )
    auth_realm: str = Field(description="Name of the realm to use")
    auth_admin_username: str = Field(
        description="Username of the admin account for the (master) realm",
        default="admin",
    )
    auth_admin_password: str = Field(description="Password for the admin account")

    @computed_field
    @property
    def authorization_url(self) -> str:
        return (
            self.auth_server_url.encoded_string()
            + f"realms/{self.auth_realm}"
            + OIDC_ENDPOINT
            + "/auth"
        )

    @computed_field
    @property
    def token_url(self) -> str:
        return (
            self.auth_server_url.encoded_string()
            + f"realms/{self.auth_realm}"
            + OIDC_ENDPOINT
            + "/token"
        )

    # DB
    db_dsn: PostgresDsn = Field(description="DSN fot the database conenction")

    # Data
    data_root_dir: DirectoryPath = Path("./data")

    @computed_field
    @property
    def product_image_root_dir(self) -> Path:
        return self.data_root_dir / "product/images"

    # Network
    port: int = Field(
        description="Port on which the application shoul run.",
        default=8000,
        ge=1,  # valid tcp/udp range lower limit
        le=65535,  # valid tcp/udp range upper limit
    )
    host: HttpUrl = Field(
        description="URL of the host. Used for e.g. path resolution for static content delivery."
    )
    api_prefix: str = "/api/v1"

    @computed_field
    @property
    def api_host(self) -> HttpUrl:
        return HttpUrl(f"{self.host}/{self.api_prefix}")

    # Model Config
    model_config = SettingsConfigDict(env_file=(".env"), extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
