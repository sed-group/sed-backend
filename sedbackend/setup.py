import time
import logging
from logging.handlers import TimedRotatingFileHandler
import tempfile

import mysqlsb
from fastapi import Request
from fastapi.logger import logger
from starlette.responses import Response

# Set database logger
mysqlsb.Configuration.logger = logger


def config_default_logging():
    """
    Should be run during application setup
    :return:
    """
    log_level = logging.DEBUG
    log_name = tempfile.gettempdir()+"/sed-backend.log"
    file_name_date_handler = TimedRotatingFileHandler(log_name, when="midnight", interval=1)
    file_name_date_handler.suffix = "%Y%m%d"
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    handlers = [file_name_date_handler]
    logging.basicConfig(
        handlers=handlers,
        format=log_format,
        level=log_level)


def install_middleware(app):
    """
    Install middleware
    :param app: FastAPI app
    :return: Null
    """

    @app.middleware("http")
    async def log_exceptions(request: Request, call_next):
        try:
            return await call_next(request)
        except:
            logger.exception("Internal server error.")
            return Response("Internal server error", status_code=500)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)

        url_str = request.url.path
        if request.url.query:
            url_str += ('?' + request.url.query)

        logger.info(f"Request completed_in={formatted_process_time}ms status_code={response.status_code} "
                    f"path={url_str}")

        return response
