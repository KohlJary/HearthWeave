"""Model hookups for the household agent: hosted and local, stdlib only.

Each returns ``complete(system, prompt) -> str``. Nothing is called until
the agent calls it.
"""

from __future__ import annotations

import json
import os
import urllib.request

from .household import Complete


def _post(url: str, body: dict, headers: dict[str, str], timeout: float) -> dict:
    req = urllib.request.Request(url, json.dumps(body).encode(), {"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def anthropic(model: str | None = None, max_tokens: int = 1024, timeout: float = 60) -> Complete:
    """Claude, through the Messages API. Reads ANTHROPIC_API_KEY."""
    model = model or os.environ.get("HEARTHWEAVE_MODEL", "claude-haiku-5-5")

    def complete(system: str, prompt: str) -> str:
        key = os.environ["ANTHROPIC_API_KEY"]
        d = _post("https://api.anthropic.com/v1/messages",
                  {"model": model, "max_tokens": max_tokens, "system": system,
                   "messages": [{"role": "user", "content": prompt}]},
                  {"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout)
        return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")

    complete.model = model  # type: ignore[attr-defined]
    return complete


def ollama(model: str | None = None, base: str | None = None, timeout: float = 180) -> Complete:
    """A local model through Ollama, on the household's own box."""
    model = model or os.environ.get("HEARTHWEAVE_LOCAL_MODEL", "llama3.1:8b-instruct-q8_0")
    base = base or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def complete(system: str, prompt: str) -> str:
        d = _post(f"{base}/api/chat",
                  {"model": model, "stream": False, "format": "json",
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]},
                  {}, timeout)
        return d.get("message", {}).get("content", "")

    complete.model = model  # type: ignore[attr-defined]
    return complete
