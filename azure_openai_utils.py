"""
azure_openai_utils.py ── backend helpers for the Streamlit chat app
------------------------------------------------------------------
• Reads the Azure OpenAI key from a .env file (via python-dotenv)
• Uses *hard-coded* API version and endpoint
• Loads GenAISetup3.json for prompt + chat parameters
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Hard-coded connection details
# ---------------------------------------------------------------------------
API_VERSION: str = "2024-12-01-preview"
AZURE_ENDPOINT: str = "https://bburgaletaaihu0046123931.openai.azure.com/"

# ---------------------------------------------------------------------------
# Load environment variables (.env → process env)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def load_config(path: str | Path) -> dict:
    """Return the parsed JSON config (systemPrompt + chatParameters)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_client() -> AzureOpenAI:
    """Return an AzureOpenAI client using the key from $AZURE_OPENAI_KEY."""
    api_key = os.getenv("AZURE_OPENAI_KEY")
    if not api_key:
        raise EnvironmentError(
            "AZURE_OPENAI_KEY not set. Add it to a .env file or your shell session."
        )

    return AzureOpenAI(
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=api_key,
    )


def chat_completion(
    client: AzureOpenAI,
    cfg: dict,
    messages: List[Dict[str, str]],
) -> str:
    """
    Light wrapper around ChatCompletion – pulls all numeric/text parameters
    from cfg['chatParameters'] and returns the assistant's text only.
    """
    params = cfg["chatParameters"]

    response = client.chat.completions.create(
        model=params["deploymentName"],                # e.g. "gpt-4o-mini"
        messages=messages,
        max_tokens=params.get("maxResponseLength", 1024),
        temperature=params.get("temperature", 1.0),
        top_p=params.get("topProbablities", 1.0),
        stop=params.get("stopSequences") or None,
        frequency_penalty=params.get("frequencyPenalty", 0.0),
        presence_penalty=params.get("presencePenalty", 0.0),
    )

    return response.choices[0].message.content.strip()
