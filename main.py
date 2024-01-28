# Import the routes
import importlib
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vending_machine.config import settings
from vending_machine.database import get_db

logger = logging.getLogger(__name__)


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
            logger.info(f"Imported {len(module_routes.routes)} routes from {module_name}")
            routes.append(module_routes)
        else:
            logger.info(f"No routes found in {module_name}")

    return routes


def main() -> FastAPI:
    logger.setLevel(logging.INFO)

    # Add a handler to the logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Starting the application")

    logger.info("Connecting to the DB")
    app = FastAPI(title=settings.app_name, debug=settings.debug, dependencies=[Depends(get_db)])
    logger.info("Connection established")

    if settings.debug:
        logger.info("Running in debug mode")
        logger.setLevel(logging.DEBUG)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add the assets to the app
    app.db = get_db()
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

    if settings.debug:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="debug")
    else:
        uvicorn.run(app, host=settings.host or "0.0.0.0", port=settings.port or 8000)
