from typing import Any, Dict

import jwt
from fastapi import Request
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError

from application.exceptions import UnauthorizedError
from config import JWT_SECRET_KEY

from .access_token_data import AccessTokenData


def get_current_user(request: Request) -> AccessTokenData:
    authorization = request.headers.get("Authorization")

    if authorization is None:
        raise UnauthorizedError("Authorization header is missing")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid authorization header format")

    token = parts[1]

    try:
        payload: Dict[str, Any] = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=["HS256"])
        return AccessTokenData(
            session_id=payload["sessionId"],
            user_id=payload["uid"],
            roles=payload["roles"],
            email=payload.get("email"),
            username=payload["username"],
            validated=payload["validated"],
            tenant_id=payload["tenantId"],
        )
    except ExpiredSignatureError:
        raise UnauthorizedError("Access Token is expired")
    except InvalidSignatureError:
        raise UnauthorizedError("Invalid Access Token")
    except (ValueError, KeyError, DecodeError):
        raise UnauthorizedError("Invalid Access Token")
