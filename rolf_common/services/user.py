from httpx import AsyncClient
from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from rolf_common.backend.settings import settings
from rolf_common.schemas.auth import RequireUserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_service_base_url = settings.auth_service_base_url


async def get_user(permissions: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not provided')

    permissions: list[str] = permissions.scopes

    async with AsyncClient() as client:
        payload = {
            'access_token': token,
            'permissions': permissions
        }
        auth_response = await client.post(auth_service_base_url + '/validate/auth', json=payload)

        response = RequireUserResponse(
            user_id=auth_response.json()['user_id'],
        )

        return response


