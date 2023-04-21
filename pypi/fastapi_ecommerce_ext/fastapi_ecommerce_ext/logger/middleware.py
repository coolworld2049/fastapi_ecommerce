import json
import time
from typing import Callable

from loguru import logger
from starlette import status
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import StreamingResponse
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Match


class LoguruLoggingMiddleware:
    async def __call__(self, request: Request, call_next: Callable):
        try:
            await self.log_before_response(request)
            st = time.time()
            response = await call_next(request)
            elapsed = f"{time.time() - st:0.10f} sec"
            response.headers.append("X-Response-Time", elapsed)
        except Exception as e:
            if request.app.debug:
                logger.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"{e.__class__.__name__} - {e.args}"},
                media_type="application/json",
            )
            return await self.log_after_response(request, response)
        return response

    @staticmethod
    def log_format(request: Request):
        return f"{request.client.host}:{request.client.port} - {request.method} {request.url}"

    async def log_before_response(self, request: Request):
        msg = (
            f"{request.client.host}:{request.client.port} - "
            f"{request.method} {request.url}"
        )
        if request.app.debug:
            headers = []
            for route in request.app.router.routes:
                match, scope = route.matches(request)
                if match == Match.FULL:
                    for name, value in scope["path_params"].items():
                        headers.append(f"{name}: {value}")
            if len(headers) > 0:
                logger.info(f"- Params: {headers}")
        logger.info(self.log_format(request))
        return request

    @staticmethod
    async def log_after_response(request: Request, response: Response | StreamingResponse):
        msg = "response to prev request: "
        if isinstance(response, StreamingResponse):
            response_body = [
                section async for section in response.body_iterator
            ]
            response.body_iterator = iterate_in_threadpool(
                iter(response_body)
            )
            msg += f"{response_body[0].decode()}"
        elif isinstance(response, Response):
            msg += f"{json.loads(response.body)}"
        logger.info(msg)
        return response
