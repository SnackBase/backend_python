from enum import Enum
from typing import Annotated, Literal
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
    OpenIdConnect,
    SecurityScopes,
)
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakConnectionError, KeycloakGetError
from jwcrypto.jwt import JWTExpired

from app.data.models.user import User
from app.settings import get_settings


class SCOPES(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    KIOSK = "kiosk"


settings = get_settings()

# This is used for fastapi docs authentification
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.authorization_url,
    tokenUrl=settings.token_url,
)

TokenDep = Annotated[str, Depends(oauth2_scheme)]

# This actually does the auth checks
# client_secret_key is not mandatory if the client is public on keycloak
keycloak_openid = KeycloakOpenID(
    server_url=settings.auth_server_url.encoded_string(),
    client_id=settings.auth_client_id,
    client_secret_key=settings.auth_client_secret,
    realm_name=settings.auth_realm,
    verify=settings.auth_ssl_verify,
)

# this is the admin interface
# The admin user authenticates in the 'master' realm but manages the DrinkBar realm
keycloak_admin = KeycloakAdmin(
    server_url=str(settings.auth_server_url),
    username=settings.auth_admin_username,
    password=settings.auth_admin_password,
    realm_name=settings.auth_realm,  # The realm to manage (DrinkBar)
    user_realm_name="master",  # The realm where admin user exists
    verify=settings.auth_ssl_verify,
)


async def authorize(
    token: TokenDep,
    security_scopes: SecurityScopes,
    mode: Literal["all", "any"] = "all",
) -> User:
    try:
        decoded_token = await keycloak_openid.a_decode_token(token=token)
    except JWTExpired as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except KeycloakConnectionError | KeycloakGetError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Connection error while connecting to auth server. {e}",
        )
    user = User(**decoded_token)
    scopes = security_scopes.scopes
    if len(scopes) < 1:
        return user
    contained_scopes = [scope in user.scopes for scope in scopes]
    condition = all(contained_scopes) if mode == "all" else any(contained_scopes)
    if not condition:
        missing_scopes = [s for s, c in zip(scopes, contained_scopes) if not c]
        msg = (
            ("Scope: " if len(missing_scopes) == 1 else "Scopes: ")
            + str(missing_scopes)
            + (" is " if len(missing_scopes) == 1 else " are ")
            + "missing"
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    return user


async def authorize_any(token: TokenDep, security_scopes: SecurityScopes) -> User:
    return await authorize(token=token, security_scopes=security_scopes, mode="any")


async def authorize_all(token: TokenDep, security_scopes: SecurityScopes) -> User:
    return await authorize(token=token, security_scopes=security_scopes, mode="all")


AuthorizedDep = Annotated[
    User, Security(authorize_any, scopes=[])
]  # for all authenticated users, ignoring scopes
AuthorizedAnyDep = Annotated[
    User, Security(authorize_any, scopes=[s.value for s in SCOPES])
]  # for all users having one of the available scopes
AuthorizedConsumerDep = Annotated[
    User, Security(authorize_any, scopes=[SCOPES.CUSTOMER.value, SCOPES.KIOSK.value])
]  # for all user except the admin
AuthorizedAdminDep = Annotated[
    User, Security(authorize_all, scopes=[SCOPES.ADMIN.value])
]  # only admin
AuthorizedKioskDep = Annotated[
    User, Security(authorize_all, scopes=[SCOPES.KIOSK.value])
]  # only kiosk
AuthorizedCustomerDep = Annotated[
    User, Security(authorize_all, scopes=[SCOPES.CUSTOMER.value])
]  # only customer
