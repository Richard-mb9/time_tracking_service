from typing import Annotated

from fastapi import Depends

from infra.database_manager import DatabaseManagerConnection

from .get_current_user import get_current_user
from .get_database_manager import get_database_manager

login_required = Depends(get_current_user)

DBManager = Annotated[DatabaseManagerConnection, Depends(get_database_manager)]
