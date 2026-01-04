from pydantic import BaseModel, EmailStr, Field, computed_field, ConfigDict
# from pydantic.alias_generators import to_camel


class UserPublic(BaseModel):
    preferred_username: str = Field(alias="username")
    given_name: str = Field(alias="firstName")
    family_name: str = Field(alias="lastName")

    model_config = ConfigDict(
        populate_by_name=True, from_attributes=True, serialize_by_alias=True
    )


class User(UserPublic):
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
        return self.scope.split(" ")
