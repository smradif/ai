import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.money.api import money_transfer_api_builder
from agents.person.api import person_api_builder
from users.api import user_api_builder
from agents.travel.api import travel_api_builder
from agents.chat.api import chat_api_builder
from agents.orchestrator.api import orchestrator_api_builder
from agents.supervisor.api import supervisor_api_builder
from datetime import datetime
from agents.llm.llm import llm
from contextlib import asynccontextmanager
from database.postgres import init_postgres, close_postgres
from mcp_app.mcp_server import create_mcp_server
from transformers import pipeline

mcp_http_app = create_mcp_server().http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_http_app.router.lifespan_context(app):
        await init_postgres()
        try:
            yield
        finally:
            await close_postgres()


app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

money_transfer_api_builder(app)
person_api_builder(app)
user_api_builder(app)
travel_api_builder(app)
chat_api_builder(app)
orchestrator_api_builder(app)
supervisor_api_builder(app)
app.mount("/mcp", mcp_http_app)


@app.get("/status")
async def status():
    """Simple health/status endpoint returning server time."""
    return {"status": "ok", "time": datetime.now().isoformat() + "Z"}


# For local development run:
# uvicorn main:app --reload --port 8000
