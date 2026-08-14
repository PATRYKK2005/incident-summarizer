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

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Nieprawidłowy format JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    incident_text = body.get("incident", "")

    if not incident_text:
        return func.HttpResponse(
            json.dumps({"error": "Pole 'incident' jest wymagane"}),
            status_code=400,
            mimetype="application/json"
        )

    if len(incident_text) < 10:
        return func.HttpResponse(
            json.dumps({"error": "Opis incydentu jest zbyt krótki"}),
            status_code=400,
            mimetype="application/json"
        )

    prompt = PROMPT_TEMPLATE.format(incident=incident_text)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()

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

    except requests.exceptions.Timeout:
        return func.HttpResponse(
            json.dumps({"error": "Timeout — model nie odpowiedział w czasie 60s"}),
            status_code=504,
            mimetype="application/json"
        )

    except requests.exceptions.ConnectionError:
        return func.HttpResponse(
            json.dumps({"error": f"Nie można połączyć się z Ollama pod {OLLAMA_URL}"}),
            status_code=503,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Nieoczekiwany błąd: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
