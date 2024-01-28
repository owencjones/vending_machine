import importlib
from pathlib import Path
from typing import List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)

from vending_machine.config import settings
from vending_machine.logging import get_logger

logger = get_logger(__name__)


def get_routes_from_controllers() -> List[APIRouter]:
    here_path = Path(__file__).parent
    route_files_dir = here_path / "vending_machine/controllers"
    route_files = [f for f in route_files_dir.iterdir() if f.suffix == ".py"]

    routes: List[APIRouter] = []
    for route_file in route_files:
        module_name = f"vending_machine.{route_files_dir.name}.{route_file.stem}"
        logger.info(f"Importing routes from {module_name}")
        module = importlib.import_module(module_name)

        if hasattr(module, "routes"):
            module_routes = getattr(module, "routes")
        else:
            logger.info(f"No routes found in {module_name}")
            continue

        if module_routes:
            logger.info(
                f"Imported {len(module_routes.routes)} routes from {module_name}"
            )
            routes.append(module_routes)
        else:
            logger.info(f"No routes found in {module_name}")

    return routes


def main() -> FastAPI:
    logger.info("Starting the application")

    logger.info("Connecting to the DB")
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    if settings.debug:
        logger.info("Adding Swagger UI")

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app.title + " - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
            )

        @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_oauth2_redirect_html()

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
            )

    logger.info("Connection established")

    if settings.debug:
        logger.info("Running in debug mode")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add the assets to the app
    app.logger = logger

    @app.middleware("http")
    async def set_default_content_type(request, call_next):
        response = await call_next(request)
        response.headers["Content-Type"] = "application/json"
        return response

    routes = get_routes_from_controllers()
    for route in routes:
        app.include_router(route)

    return app


# Run the app
if __name__ == "__main__":
    import uvicorn

    app = main()

    uvicorn.run(
        app,
        host=settings.host or "0.0.0.0",
        port=settings.port or 8000,
        log_level="debug" if settings.debug else "info",
        reload=settings.debug,
    )
