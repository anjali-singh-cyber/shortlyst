import os
import json
from groq import Groq
from pydantic import BaseModel
from groq import Groq, AsyncGroq


# Model chosen for Groq's strict structured-output support.
# Check console.groq.com/docs/structured-outputs for the current
# supported-model list before shipping — this changes as Groq adds models.
EXTRACTION_MODEL = "openai/gpt-oss-120b"


def _to_strict_schema(schema: type[BaseModel]) -> dict:
    """
    Groq's strict structured-output mode requires every property to be
    listed under "required" (a field can still be null — "required" in
    JSON Schema just means the key must appear) and requires
    additionalProperties: false on every object.

    Pydantic's model_json_schema() doesn't set this up for us when a
    field is Optional with a default, so we patch it here rather than
    fighting Pydantic's schema generation directly.
    """
    raw = schema.model_json_schema()
    raw["required"] = list(raw.get("properties", {}).keys())
    raw["additionalProperties"] = False
    return raw


def get_client() -> Groq:
    """
    Reads the API key from an environment variable — never hardcode it.
    Set GROQ_API_KEY in your shell/.env before running anything.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Export it or add it to a .env file."
        )
    return Groq(api_key=api_key)


def extract_structured(
    system_prompt: str,
    user_content: str,
    schema: type[BaseModel],
) -> BaseModel:
    """
    Sends a prompt to Groq and forces the response to conform to a
    Pydantic schema, using Groq's strict json_schema mode.

    Temperature is fixed at 0 — this is an extraction task, not a
    creative one. We want the same input to produce the same output
    every time, not a range of "plausible" answers.
    """
    client = get_client()

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": _to_strict_schema(schema),
            },
        },
    )

    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)
    return schema.model_validate(data)

def get_async_client() -> AsyncGroq:
    """Same idea as get_client(), but returns Groq's async client."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Export it or add it to a .env file."
        )
    return AsyncGroq(api_key=api_key)


async def extract_structured_async(
    system_prompt: str,
    user_content: str,
    schema: type[BaseModel],
) -> BaseModel:
    """
    Async version of extract_structured() — identical logic, but
    'await'-able, so multiple calls can be in-flight at once under a
    semaphore instead of blocking one at a time.
    """
    client = get_async_client()

    response = await client.chat.completions.create(
        model=EXTRACTION_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": _to_strict_schema(schema),
            },
        },
    )

    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)
    return schema.model_validate(data)