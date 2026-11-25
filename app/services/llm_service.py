import logging
import time

import httpx
from google import genai
from google.genai import errors

from app.config import settings


logger = logging.getLogger(__name__)


class EmptyModelResponseError(RuntimeError):
    """Raised when Gemini returns an empty response."""


class GeminiService:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.primary_model = settings.GEMINI_MODEL
        self.fallback_model = settings.GEMINI_FALLBACK_MODEL

        self.max_retries = 2

    @staticmethod
    def _get_status_code(exc):

        for attribute in ("code", "status_code"):
            value = getattr(exc, attribute, None)

            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    pass

        return None

    def _generate_with_model(self, model: str, prompt: str) -> str:

        for attempt in range(self.max_retries):

            try:
                logger.info(
                    "Generating response using model: %s",
                    model
                )

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if not response.text or not response.text.strip():
                    raise EmptyModelResponseError(
                        "Gemini returned an empty response."
                    )

                return response.text.strip()

            except errors.ClientError as exc:

                status_code = self._get_status_code(exc)

                if status_code == 429:
                    logger.warning(
                        "Quota or rate limit reached for model %s.",
                        model
                    )

                raise

            except (
                errors.ServerError,
                httpx.TransportError,
                EmptyModelResponseError
            ):

                if attempt == self.max_retries - 1:
                    logger.warning(
                        "Model %s failed after %s attempts.",
                        model,
                        self.max_retries
                    )
                    raise

                wait_time = 2 ** attempt

                logger.warning(
                    "Temporary failure with model %s. "
                    "Retrying in %s seconds.",
                    model,
                    wait_time
                )

                time.sleep(wait_time)

        raise RuntimeError("Model generation failed.")

    def generate_response(self, prompt: str) -> str:

        try:
            return self._generate_with_model(
                self.primary_model,
                prompt
            )

        except (
            errors.ServerError,
            errors.ClientError,
            httpx.TransportError,
            EmptyModelResponseError
        ) as exc:

            if isinstance(exc, errors.ClientError):
                status_code = self._get_status_code(exc)

                if status_code not in (429, 503):
                    raise

            logger.warning(
                "Primary model %s unavailable. "
                "Switching to fallback model %s.",
                self.primary_model,
                self.fallback_model
            )

        return self._generate_with_model(
            self.fallback_model,
            prompt
        )


gemini_service = GeminiService()