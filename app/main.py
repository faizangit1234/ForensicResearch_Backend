from dotenv import load_dotenv

load_dotenv()

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1.api_router import router
from app.utils.gemini_config import configure_gemini

# ----------------------------- Logging Configuration -----------------------------
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.FileHandler("dna_api.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ----------------------------- Environment & Config -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------- FastAPI Initialization -----------------------------
app = FastAPI(
    title="🧬 DNA Sequence Analysis API",
    description="An AI-powered API for analyzing DNA sequences using Gemini models.",
    version="1.0.0",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ----------------------------- Home Route -----------------------------
@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to the 🧬 DNA Sequence Analysis API!",
        "docs_url": "/docs",
        "status": "Running",
        "author": " Dev Faizan Farooq",
    }


# ----------------------------- Startup Event -----------------------------
@app.on_event("startup")
async def startup_event():
    selected_model = configure_gemini(GEMINI_API_KEY)
    # Store or use selected_model as needed
    logger.info(f"Using Gemini model: {selected_model}")


# ----------------------------- Include API Routers -----------------------------
app.include_router(router)
