import json
import os
from typing import Any, Dict, List, Optional

from litellm import completion


SYSTEM_PROMPT = """You are Lit-Muse, an elite literary analyst and Spotify music curator.
Analyze the input text and recommend soundtrack songs that fit its emotional atmosphere, pacing, and themes.

Requirements:
1. Respect the user's Preferred Genre.
2. Recommend only real songs.
3. Output only valid JSON and nothing else.
4. The JSON must follow this exact schema:
{
  "vibe_keywords": ["keyword1", "keyword2", "keyword3"],
  "analysis": "A brief 1-2 sentence explanation of the text's atmosphere.",
  "tracks": [
    {"title": "Song Name", "artist": "Artist Name"}
  ]
}
5. Return exactly 5 track objects in "tracks".
"""

MODEL_OPTIONS: Dict[str, Dict[str, str]] = {
    "Gemini 1.5 Flash": {
        "model": "gemini/gemini-1.5-flash",
        "api_env": "GEMINI_API_KEY",
    },
    "Gemini 2.5 Flash": {
        "model": "gemini/gemini-2.5-flash",
        "api_env": "GEMINI_API_KEY",
    },
    "DeepSeek Chat": {
        "model": "deepseek/deepseek-chat",
        "api_env": "DEEPSEEK_API_KEY",
    },
    "Qwen Max (OpenRouter)": {
        "model": "openrouter/qwen/qwen-max",
        "api_env": "OPENROUTER_API_KEY",
    },
}


def _normalize_keywords(raw_keywords: Any) -> List[str]:
    if not isinstance(raw_keywords, list):
        raw_keywords = [raw_keywords]
    keywords = [str(item).strip() for item in raw_keywords if str(item).strip()]
    return keywords[:3]


def _normalize_tracks(raw_tracks: Any) -> List[Dict[str, str]]:
    if not isinstance(raw_tracks, list):
        return []

    tracks: List[Dict[str, str]] = []
    for item in raw_tracks:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        artist = str(item.get("artist", "")).strip()
        if not title or not artist:
            continue
        tracks.append({"title": title, "artist": artist})

    return tracks[:5]


def _extract_json_payload(raw_text: str) -> Optional[Dict[str, Any]]:
    candidate = raw_text.strip()
    if not candidate:
        return None

    try:
        return json.loads(candidate)
    except Exception:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    sliced = candidate[start : end + 1]
    try:
        return json.loads(sliced)
    except Exception:
        return None


def analyze_text_for_music(
    text: str,
    genre: str,
    api_key: str,
    model_label: str = "Gemini 1.5 Flash",
) -> Dict[str, Any]:
    model_config = MODEL_OPTIONS.get(model_label, MODEL_OPTIONS["Gemini 1.5 Flash"])
    model = model_config["model"]
    api_env = model_config["api_env"]

    os.environ[api_env] = api_key

    user_prompt = f"Text to analyze: {text}\nPreferred Genre: {genre}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        raw_output = response.choices[0].message.content or ""
        parsed = _extract_json_payload(raw_output)
    except Exception:
        parsed = None

    if parsed is None:
        try:
            response = completion(
                model=model,
                messages=messages,
            )
            raw_output = response.choices[0].message.content or ""
            parsed = _extract_json_payload(raw_output)
        except Exception as error:
            return {"error": f"LLM request failed: {error}"}

    if parsed is None:
        return {"error": "LLM response was not valid JSON."}

    result = {
        "vibe_keywords": _normalize_keywords(parsed.get("vibe_keywords", [])),
        "analysis": str(parsed.get("analysis", "")).strip(),
        "tracks": _normalize_tracks(parsed.get("tracks", [])),
    }
    if len(result["tracks"]) != 5:
        result["warning"] = f"Expected 5 tracks, received {len(result['tracks'])}."
    return result
