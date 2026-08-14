import azure.functions as func
import requests
import json
import logging
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_URL = f"http://{OLLAMA_HOST}:11434/api/generate"

PROMPT_TEMPLATE = """Jesteś asystentem IT Operations. Przeanalizuj poniższy opis incydentu i zwróć podsumowanie w formacie JSON.

Opis incydentu:
{incident}

Zwróć TYLKO poprawny JSON bez żadnego dodatkowego tekstu, w następującym formacie:
{{
  "summary": "2-3 zdaniowe podsumowanie co się stało",
  "affected_system": "nazwa systemu którego dotyczy incydent",
  "severity": "critical/high/medium/low",
  "key_facts": ["fakt 1", "fakt 2", "fakt 3"],
  "suggested_action": "najbardziej pilna czynność do wykonania"
}}"""


@app.route(route="summarize", methods=["POST"])
def summarize_incident(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Otrzymano incydent do podsumowania")

    body = req.get_json()
    incident_text = body.get("incident")
    prompt = PROMPT_TEMPLATE.format(incident=incident_text)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    ollama_response = response.json()
    raw_text = ollama_response.get("response", "")

    try:
        summary = json.loads(raw_text)
    except json.JSONDecodeError:
        summary = {"raw_response": raw_text}

    result = {
        "incident": incident_text,
        "analysis": summary,
        "model": OLLAMA_MODEL
    }

    return func.HttpResponse(
        json.dumps(result, ensure_ascii=False, indent=2),
        status_code=200,
        mimetype="application/json"
    )
