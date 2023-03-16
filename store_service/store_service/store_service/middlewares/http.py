import time

from loguru import logger
from prisma.errors import PrismaError
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from store_service.core.config import get_app_settings


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except PrismaError as pe:
        return JSONResponse(
            status_code=420,
            content={"details": pe.args},
        )
    except Exception as e:
        logger.exception(e.args)
        return Response("Internal server error", status_code=500)


async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    pt = str(f"{process_time:0.4f} sec")
    response.headers["X-Process-Time"] = pt
    if get_app_settings().DEBUG:
        logger.debug(f"X-Process-Time: {pt}")
    return response
