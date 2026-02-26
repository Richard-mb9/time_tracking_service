from typing import Literal, cast

from decouple import config
from dotenv import find_dotenv, load_dotenv

ENVIRONMENT: Literal["HML", "PRD", "local", "test"] = cast(
    Literal["HML", "PRD", "local", "test"],
    config("ENVIRONMENT", default="local"),
)

dotenv = find_dotenv(f".env.{ENVIRONMENT.lower()}")
load_dotenv(dotenv)

USER_DB = config("USER_DB", default=None)
PASSWORD_DB = config("PASSWORD_DB", default=None)
HOST_DB = config("HOST_DB", default=None)
NAME_DB = config("NAME_DB", default=None)
PORT_DB = config("PORT_DB", default=None)

URL_DB = f"postgresql://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"

JWT_SECRET_KEY = cast(str, config("JWT_SECRET_KEY", default="local-key"))
SYSTEM_TENANT_ID = int(config("SYSTEM_TENANT_ID", cast=int, default=1))
