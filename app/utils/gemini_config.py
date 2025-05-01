import logging
import os

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument, RetryError

logger = logging.getLogger(__name__)

PREFERRED_MODELS = [
    "models/gemini-1.5-pro-latest",
    "models/gemini-1.5-pro-002",
    "models/gemini-1.5-pro",
]


def configure_gemini(api_key: str):
    if not api_key:
        logger.critical("GEMINI_API_KEY is missing.")
        raise RuntimeError("Gemini API key not configured.")

    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        available_models = genai.list_models()
        model_names = [model.name for model in available_models]

        selected_model = next((m for m in PREFERRED_MODELS if m in model_names), None)
        if not selected_model:
            logger.critical("No supported Gemini model found.")
            raise RuntimeError("No supported Gemini model found.")

        os.environ["GEMINI_MODEL"] = selected_model
        logger.info(f" Gemini model configured: {selected_model}")
        return selected_model

    except InvalidArgument:
        logger.critical("Gemini API key is invalid or unauthorized.", exc_info=True)
        raise RuntimeError("Invalid or expired Gemini API key.")
    except (GoogleAPICallError, RetryError) as e:
        logger.error("Error communicating with Gemini API: %s", str(e), exc_info=True)
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during Gemini configuration: %s", str(e), exc_info=True
        )
        raise
