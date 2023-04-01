import json
import time
from typing import Callable

from loguru import logger
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Match


class LoguruLoggingMiddleware:
    async def __call__(self, request: Request, call_next: Callable):
        try:
            st = time.time()
            response = await call_next(request)
            elapsed = f"{time.time() - st:0.10f} sec"
            response.headers.append("X-Response-Time", elapsed)
        except Exception as e:
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"{e.__class__.__name__} - {e}"},
                media_type="application/json",
            )
        return await self.http(request, response)

    async def http(self, request: Request, response: Response | JSONResponse):
        status_color = self.__colorize_response_status(response.status_code)
        msg = (
            f"{request.client.host}:{request.client.port} - "
            f"{request.method} {request.url} {response.status_code}"
        )
        if 500 <= response.status_code <= 599:
            msg += f" - response: {response.__dict__}"
        if request.app.debug:
            headers = []
            for route in request.app.router.routes:
                match, scope = route.matches(request)
                if match == Match.FULL:
                    for name, value in scope["path_params"].items():
                        headers.append(f"{name}: {value}")
            if len(headers) > 0:
                logger.opt(colors=True).info(
                    f"<{status_color}>- Params: {headers}</{status_color}>"
                )
        logger.opt(colors=True).info(f"<{status_color}>{msg}</{status_color}>")
        return response

    @staticmethod
    def __colorize_response_status(status_code: int):
        color = "w"
        if 200 <= status_code <= 299:
            color = "light-white"
        elif 300 <= status_code <= 399:
            color = "light-magenta"
        elif 400 <= status_code <= 499:
            color = "fg 255,150,38"
        elif 500 <= status_code <= 599:
            color = "light-red"
        return color
