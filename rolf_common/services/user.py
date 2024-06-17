from httpx import AsyncClient
from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from rolf_common.backend.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_service_base_url = settings.auth_service_base_url


async def require_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not provided')

    async with AsyncClient() as client:
        payload = {
            'token': token
        }
        response = await client.post(auth_service_base_url + '/validate/token', json=payload)

        # TODO: create a pydantic schema to return (must match the return from /validate/token
        return {
            'username': 'lucas',
            'userId': 'este.e.um.uuid',
        }


