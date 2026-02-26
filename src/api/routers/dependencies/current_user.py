from typing import Annotated

from fastapi import Depends

from .access_token_data import AccessTokenData
from .get_current_user import get_current_user

CurrentUser = Annotated[AccessTokenData, Depends(get_current_user)]
