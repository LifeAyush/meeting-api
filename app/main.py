from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api.v1.routes import meetings
from app.api.v1.routes import transcripts
from app.api.v1.websocket import websocket_endpoint

def register_routes(app: FastAPI):
    app.include_router(meetings.router, prefix="/api/v1/meetings")
    app.include_router(transcripts.router, prefix="/api/v1/transcripts")
    app.add_api_websocket_route("/ws/meetings/{meeting_id}", websocket_endpoint)

def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def create_app() -> FastAPI:
    app = FastAPI()
    init_db()
    register_routes(app)
    register_middlewares(app)
    return app

app = create_app()
