import os
import re

from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

router = APIRouter(prefix="/image", tags=["image"])

# Use a dedicated DALLE_API_KEY if set, otherwise fall back to OPENAI_API_KEY
_dalle_key = os.getenv("DALLE_API_KEY") or os.getenv("OPENAI_API_KEY")
_dalle_client = OpenAI(api_key=_dalle_key) if _dalle_key else None

BLOCKED_PATTERNS = [
    r"\bhate\b",
    r"\bviolence\b",
    r"\bextremis[mt]\b",
    r"\bterror",
    r"\bkill\b",
    r"\bmurder\b",
    r"\bblood\b.{0,20}\b(cross|church|christ)",
    r"\bsexual\b",
    r"\berotic\b",
    r"\bnude\b",
    r"\bnaked\b.{0,30}\b(jesus|god|mary|saint|angel)",
    r"rewrite\b.{0,40}\bbible",
    r"white supremac",
    r"racial (purity|cleansing|superiority)",
    r"satanic\b.{0,20}\b(worship|ritual|church)",
    r"\bdemons?\b.{0,20}\b(praise|worship|adore)",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

SAFE_STYLE_SUFFIX = (
    ", digital painting, warm golden light, reverent atmosphere, "
    "tasteful religious art, no violence, no nudity, no offensive content"
)


def _is_blocked(prompt: str) -> bool:
    for p in _COMPILED:
        if p.search(prompt):
            return True
    return False


def _enrich_prompt(prompt: str) -> str:
    """Add safe-style suffix if not already detailed."""
    if len(prompt) < 80:
        return prompt + SAFE_STYLE_SUFFIX
    return prompt


class ImageRequest(BaseModel):
    prompt: str


@router.post("/generate")
def generate_image(request: ImageRequest):
    if _is_blocked(request.prompt):
        return {
            "success": False,
            "message": "Unsafe image prompt detected. Please describe a respectful Christian scene.",
        }

    enriched = _enrich_prompt(request.prompt)

    # Attempt real generation if a non-OpenRouter key is available
    if _dalle_client and not (os.getenv("OPENAI_API_KEY", "").startswith("sk-or-")):
        try:
            resp = _dalle_client.images.generate(
                model="dall-e-3",
                prompt=enriched,
                n=1,
                size="1024x1024",
                quality="standard",
            )
            image_url = resp.data[0].url
            return {
                "success": True,
                "image_url": image_url,
                "prompt_used": enriched,
                "mode": "generated",
            }
        except Exception as e:
            # Fall through to prompt-only response on API error
            pass

    # Fallback: return the enriched prompt so the frontend can display it
    return {
        "success": True,
        "image_url": None,
        "prompt_used": enriched,
        "mode": "prompt_only",
        "message": (
            "Image generation requires a direct OpenAI API key (DALLE_API_KEY). "
            "The enriched prompt above is ready for use with DALL-E 3 or Stable Diffusion."
        ),
    }
