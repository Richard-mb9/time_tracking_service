# pylint: disable=unused-argument
# pyright: reportUnusedFunction=false
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routers import create_routes
from application.exceptions import APIError
from infra.mappers import import_mappers

URL_PREFIX = ""
API_DOC = f"{URL_PREFIX}/doc/api"
API_DOC_REDOC = f"{URL_PREFIX}/doc/redoc"
API_DOC_JSON = f"{URL_PREFIX}/doc/api.json"
API_VERSION = "V1.0.0"


def create_app() -> FastAPI:
    import_mappers()

    api = FastAPI(
        root_path="/time-tracking-service",
        title="Time Tracking Service API",
        description="Time tracking and attendance management API",
        openapi_url=API_DOC_JSON,
        redoc_url=API_DOC_REDOC,
        docs_url=API_DOC,
        version=API_VERSION,
    )

    @api.exception_handler(APIError)
    def api_error_handler(request: Request, error: APIError) -> JSONResponse:
        _ = request
        return JSONResponse(
            content={"detail": error.message},
            status_code=error.status_code,
        )

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        _ = request
        errors = exc.errors()
        response = {}
        for error in errors:
            key = error["loc"][1]
            response[key] = error["msg"]
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"detail": response},
        )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    create_routes(api, URL_PREFIX)

    return api
