"""DeepSeek API client for sentence segmentation."""

import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from splitter.prompt import SYSTEM_PROMPT

load_dotenv()

_BASE_URL = "https://api.deepseek.com"
_MODEL = "deepseek-chat"

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set. Add it to .env")
        _client = AsyncOpenAI(api_key=api_key, base_url=_BASE_URL)
    return _client


def _parse_segments(raw: str) -> list[str]:
    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        for key in ("segments", "data", "results"):
            if key in parsed and isinstance(parsed[key], list):
                return [str(s) for s in parsed[key]]
    if isinstance(parsed, list):
        return [str(s) for s in parsed]
    return []


async def split_text(text: str) -> list[str]:
    """Send full transcript to DeepSeek, get back sentence strings."""
    client = _get_client()
    resp = await client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n\n{text}"},
        ],
        temperature=0.0,
        max_tokens=16384,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content or ""
    if not raw.strip():
        return []
    return _parse_segments(raw)


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
