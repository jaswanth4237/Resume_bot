import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    LLM Client for structured JSON extraction.
    Supports Google Gemini REST API (AIza keys) and OpenAI.
    Falls back to rule engine if API is unavailable or times out.
    """
    @classmethod
    async def extract_structured_json(
        cls,
        prompt: str,
        document_text: str,
        schema_cls: Type[T]
    ) -> Optional[T]:
        api_key = settings.LLM_API_KEY.strip()

        if not api_key or api_key == "your_llm_api_key_here":
            return None

        # Google Gemini API (AIza keys only — AQ. keys are not Gemini keys)
        if api_key.startswith("AIza"):
            for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": f"{prompt}\n\nDOCUMENT:\n{document_text}"}]}],
                        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.0}
                    }
                    async with httpx.AsyncClient(timeout=12.0) as client:
                        resp = await client.post(url, json=payload)
                        if resp.status_code == 200:
                            raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                            return schema_cls.model_validate(json.loads(raw))
                        else:
                            logger.warning(f"Gemini {model_name} returned {resp.status_code}")
                except Exception as e:
                    logger.warning(f"Gemini {model_name} failed: {e}")

        # OpenAI-compatible API (sk- keys)
        if api_key.startswith("sk-"):
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key)
                response = await client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": document_text}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                )
                raw_json = response.choices[0].message.content
                if raw_json:
                    return schema_cls.model_validate(json.loads(raw_json))
            except Exception as e:
                logger.warning(f"OpenAI extraction failed: {e}")

        # Unknown key type — skip LLM, use rule engine
        logger.info("API key format not recognized for LLM extraction. Using rule-based engine.")
        return None
