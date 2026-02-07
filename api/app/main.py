from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import projects, renders, assets, heygen


def create_app() -> FastAPI:
    app = FastAPI(title="txt2video")
    init_db()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(projects.router)
    app.include_router(renders.router)
    app.include_router(assets.router)
    app.include_router(heygen.router)

    return app


app = create_app()
