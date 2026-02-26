from typing import Optional

from config import SYSTEM_TENANT_ID

from .access_token_data import AccessTokenData


def resolve_tenant_id(
    current_user: AccessTokenData, tenant_id: Optional[int]
) -> Optional[int]:
    if current_user.tenant_id == SYSTEM_TENANT_ID:
        return tenant_id
    return current_user.tenant_id
