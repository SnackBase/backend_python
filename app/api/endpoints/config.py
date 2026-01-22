from fastapi import APIRouter

from app.api.interface.tags import Tags
from app.auth.service import AuthenticatedUserDep


router = APIRouter(prefix=f"/{Tags.CONFIG}", tags=[Tags.CONFIG])


### TODO: implement Config structure
# {
#   "currency": {
#     "code": "EUR",
#     "symbol": "€",
#     "locale": "de-DE",
#     "name": "Euro"
#   }
# }


@router.get(f"/{Tags.CURRENCY}")
def get_currency_config(_: AuthenticatedUserDep) -> dict:
    # TODO: make available through admin config pandel
    return {"code": "EUR", "symbol": "€", "locale": "de-DE", "name": "Euro"}
