import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from rolf_common.backend.logger import get_logger


class LogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        body = json.loads(body.decode("utf-8")) if body else None

        response: Response = await call_next(request)
        response_body = b"".join([chunk async for chunk in response.body_iterator])

        response_message = {
            'url': str(request.url),
            'method': request.method,
            'path_params': request.path_params,
            'request_body': body,
            'query_params': dict(request.query_params),
            'request_headers': dict(request.headers),

            'client_host': request.client.host,

            'status_code': response.status_code,
            'response_headers': dict(response.headers),
            'response_body': response_body.decode('utf-8'),
            'r': response
        }
        get_logger().info(json.dumps(response_message), extra={'is_request': 'É os guri'})

        return StreamingResponse(iter([response_body]), status_code=response.status_code,
                                 headers=dict(response.headers))
