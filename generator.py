import os
import time

from google.generativeai import configure as _configure
from google.generativeai import GenerativeModel as _GenerativeModel
from google.generativeai.types import GenerationConfig as _GenerationConfig
from prompts import build_prompt

_configured = False
MAX_RETRIES = 5
RETRY_DELAY = 15
_last_call_time = 0.0
MIN_CALL_INTERVAL = 13.0  # Stay under 5 requests/minute free-tier limit


def _ensure_configured():
    global _configured
    if not _configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Missing GEMINI_API_KEY. Set it as an environment variable before running."
            )
        _configure(api_key=api_key)
        _configured = True


def generate_email(intent, facts, tone, model="gemini-2.5-flash", use_few_shot=True):
    """Call the Google Gemini API to generate a professional email with retry logic."""
    _ensure_configured()
    prompt_text = build_prompt(intent, facts, tone, use_few_shot=use_few_shot)

    gen_model = _GenerativeModel(
        model_name=model,
        generation_config=_GenerationConfig(
            temperature=0.3,
            max_output_tokens=512,
        ),
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            global _last_call_time
            elapsed = time.time() - _last_call_time
            if elapsed < MIN_CALL_INTERVAL:
                time.sleep(MIN_CALL_INTERVAL - elapsed)
            _last_call_time = time.time()

            response = gen_model.generate_content(prompt_text)
            email_text = response.text.strip() if response.text else ""
            if not email_text:
                raise RuntimeError(f"Empty response from {model}")
            return email_text

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"    Error on {model} (attempt {attempt}): {e}, retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"{model} failed after {MAX_RETRIES} attempts for intent: {intent}") from e
