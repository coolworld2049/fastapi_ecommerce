import time

from loguru import logger
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(e.args)
        return Response("Internal server error", status_code=500)


async def process_time_header_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    pt = str(f"{process_time:0.4f} sec")
    response.headers["X-Process-Time"] = pt
    if request.app.debug:
        logger.debug(f"X-Process-Time: {pt}")
    return response


async def logger_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    status_color = "w"
    if 200 <= response.status_code <= 299:
        status_color = "light-white"
    elif 300 <= response.status_code <= 399:
        status_color = "light-magenta"
    elif 400 <= response.status_code <= 499:
        status_color = "fg 255,150,38"
    elif 499 <= response.status_code <= 599:
        status_color = "light-red"

    msg = (
        f"<{status_color}>{request.client.host}:{request.client.port} - "
        f"{request.method} {request.url} {response.status_code}</{status_color}>"
    )
    logger.opt(colors=True).info(msg)
    if request.app.debug:
        headers = []
        for route in request.app.router.routes:
            match, scope = route.matches(request)
            if match == Match.FULL:
                for name, value in scope["path_params"].items():
                    headers.append(f"\n\t{name}: {value}")
        if headers:
            logger.info(
                f"<{status_color}>Params: \n{headers}</{status_color}>"
            )
    return response
