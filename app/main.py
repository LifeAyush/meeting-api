from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import meetings, summary, transcripts
from app.api.v1.websocket import websocket_endpoint
from app.db.session import init_db


def register_routes(app: FastAPI) -> None:
    app.include_router(meetings.router, prefix="/api/v1/meetings", tags=["meetings"])
    app.include_router(transcripts.router, prefix="/api/v1/transcripts", tags=["transcripts"])
    app.include_router(summary.router, prefix="/api/v1/summary", tags=["summary"])
    app.add_api_websocket_route("/ws/meetings/{meeting_id}", websocket_endpoint)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    # Import models so SQLAlchemy metadata is populated before create_all.
    import app.models  # noqa: F401

    app = FastAPI(title="Meeting API", version="1.0.0")
    init_db()
    register_routes(app)
    register_middlewares(app)
    return app


app = create_app()
