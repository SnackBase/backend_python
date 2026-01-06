from pydantic import EmailStr, computed_field, ConfigDict
from sqlmodel import SQLModel, Field
# from pydantic.alias_generators import to_camel


class UserPublic(SQLModel):
    """
    Public API schema for user information.

    Contains basic user profile data that can be safely exposed in API responses.
    Uses aliases for cleaner API field names (camelCase from Keycloak → snake_case).

    Attributes
    ----------
    preferred_username : str
        The user's username (exposed as "username" in API)
    given_name : str
        User's first name (exposed as "firstName" in API)
    family_name : str
        User's last name (exposed as "lastName" in API)

    Notes
    -----
    Field aliases allow the model to accept both snake_case and camelCase field names
    but always serialize using the aliases (camelCase).
    """

    preferred_username: str = Field(alias="username")
    given_name: str = Field(alias="firstName")
    family_name: str = Field(alias="lastName")

    model_config = ConfigDict(
        populate_by_name=True, from_attributes=True, serialize_by_alias=True
    )


class UserFull(UserPublic):
    """
    Complete user model with authentication and authorization data.

    Extends UserPublic with identity provider details, email, and OAuth2 scopes.
    Used internally for authorization decisions and full user context.

    Attributes
    ----------
    sub : str
        Subject identifier - unique user ID from identity provider (Keycloak UUID)
        Exposed as "id" in API responses
    email : EmailStr
        User's email address (validated format)
    email_verified : bool
        Whether the email has been verified by the identity provider
        Exposed as "emailVerified" in API
    scope : str | None, default=""
        Space-separated OAuth2 scopes granted to the user
    scopes : list[str]
        Computed property that splits scope string into a list

    Notes
    -----
    Inherits preferred_username, given_name, and family_name from UserPublic.
    """

    sub: str = Field(
        description="Unique ID from the identity Provider (in the case of keycloak, this is a UUID)",
        alias="id",
    )
    email: EmailStr
    email_verified: bool = Field(alias="emailVerified")
    scope: str | None = ""

    @computed_field
    @property
    def scopes(self) -> list[str]:
        """
        Parse the OAuth2 scope string into a list of individual scopes.

        Returns
        -------
        list[str]
            List of scope strings (e.g., ["admin", "customer"])

        Examples
        --------
        >>> user = User(scope="admin customer kiosk", ...)
        >>> user.scopes
        ['admin', 'customer', 'kiosk']
        """
        return self.scope.split(" ")
