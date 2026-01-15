# services/shared/llm.py
import os
import json
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")
genai.configure(api_key=API_KEY)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def _clean_json_text(text: str) -> str:
    # Remove markdown fences if present
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        # find JSON block
        for part in parts:
            part = part.strip()
            if part.startswith("{") or part.startswith("["):
                return part
    return text

def call_llm_sync(prompt: str, max_output_tokens=800, temperature=0.2, require_json=False):
    # Using synchronous generate_content
    model = genai.get_model(MODEL_NAME)
    resp = model.generate_text(
        prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens
    )
    text = resp.text or ""
    if require_json:
        text = _clean_json_text(text)
        return json.loads(text)
    return text
