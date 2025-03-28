import logging.config
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, RedirectResponse

from app.api.api_v1.api import router
from app.config.api_settings import UnicodeApiSettings, get_settings
from app.core.cache import cached_data
from app.core.logging import LOGGING_CONFIG
from app.core.rate_limit import rate_limit
from app.core.redis_client import redis
from app.core.umami import send_api_request_event_to_umami, send_rate_limit_exceeded_event_to_umami
from app.docs.api_docs.swagger_ui import get_api_docs_for_swagger_ui, get_swagger_ui_html
from app.enums.request_type import RequestType


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_logging(settings)
    init_redis()
    init_unicode_data(settings)
    yield


def init_logging(settings: UnicodeApiSettings) -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("app.api")
    logger.info(f"ENV: {settings.ENV}, UNICODE_VERSION: {settings.UNICODE_VERSION}")
    logger.info(settings.rate_limit_settings_report)


def init_redis():
    _ = redis.client


def init_unicode_data(settings: UnicodeApiSettings) -> None:
    start = time.process_time_ns()
    _ = cached_data.property_value_id_map
    _ = cached_data.non_unihan_character_name_map
    _ = cached_data.blocks
    _ = cached_data.planes
    _ = cached_data.all_non_unihan_codepoints
    _ = cached_data.all_cjk_codepoints
    _ = cached_data.all_tangut_ideograph_codepoints
    _ = cached_data.all_tangut_component_codepoints
    end = time.process_time_ns()
    td = (end - start) / 1_000_000
    logger = logging.getLogger("app.api")
    logger.info(f"Initialized Unicode v{settings.UNICODE_VERSION} data in {td:.0f} milliseconds.")


def simplify_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name
            cached_data.api_routes.append({"name": route.name, "path": route.path, "path_regex": route.path_regex})


app = FastAPI(
    title=get_settings().PROJECT_NAME,
    description=get_api_docs_for_swagger_ui(),
    version=get_settings().API_VERSION,
    openapi_url=f"{get_settings().API_VERSION}/openapi.json",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3500",
        "http://10.0.1.74:3500",
        "https://base64.aaronluna.dev",
        "http://172.17.0.1",
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["X-UnicodeAPI-Test"],
)
STATIC_FOLDER = Path(__file__).parent.joinpath("static")
app.mount("/static", StaticFiles(directory=str(STATIC_FOLDER)), name="static")
app.include_router(router, prefix=get_settings().API_VERSION)
simplify_operation_ids(app)


@app.middleware("http")
async def apply_rate_limiting(request: Request, call_next):
    decision = rate_limit.validate_request(request)
    match decision.request_type:
        case RequestType.RATE_LIMITED_ALLOWED:
            send_api_request_event_to_umami(request, decision)
            decision.log()
        case RequestType.RATE_LIMITED_DENIED:
            send_rate_limit_exceeded_event_to_umami(request, decision)
            decision.log()
            return JSONResponse(content=decision.error, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        case RequestType.ERROR:
            return JSONResponse(content=decision.error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return await call_next(request)


@app.get(f"{get_settings().API_VERSION}/docs", include_in_schema=False, response_class=FileResponse)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{get_settings().PROJECT_NAME} Docs - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": -1,
            "useUnsafeMarkdown": True,
            "syntaxHighlight.theme": "arta",
            "tryItOutEnabled": "true",
            "displayRequestDuration": "true",
            "requestSnippetsEnabled": "true",
            "requestSnippets": {
                "generators": {
                    "curl_bash": {"title": "cURL (bash)", "syntax": "bash"},
                },
                "defaultExpanded": False,
                "languages": None,
            },
        },
        custom_js_url="/static/custom.js",
    )


@app.get("/", include_in_schema=False)
def get_api_root():
    return RedirectResponse(
        url=app.url_path_for("swagger_ui_html"),
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
