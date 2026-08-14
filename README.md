# Incident Summarizer

Azure Function w Pythonie do automatycznego podsumowywania incydentów IT przy użyciu lokalnego modelu LLM (Ollama). Na podstawie opisu incydentu generuje strukturalną analizę zawierającą podsumowanie, dotknięty system, severity i sugerowaną akcję.

## Wymagania

- Python 3.10+
- Azure Functions Core Tools v4
- [Ollama](https://ollama.com) z zainstalowanym modelem
- pip

## Konfiguracja Ollamy

Ollama musi być dostępna z sieci lokalnej. Włącz opcję **Expose Ollama to network** w ustawieniach Ollamy, następnie pobierz model:

```bash
ollama pull qwen2.5:7b
```

## Jak uruchomić lokalnie

1. Sklonuj repozytorium:
```bash
git clone https://github.com/PATRYKK2005/incident-summarizer
cd incident-summarizer
```

2. Stwórz plik konfiguracyjny:
```bash
cp local.settings.json.example local.settings.json
```

Uzupełnij `local.settings.json` swoimi wartościami:
- `OLLAMA_HOST` — adres IP maszyny z Ollama
- `OLLAMA_MODEL` — nazwa modelu

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

4. Uruchom funkcję:
```bash
func start
```

Funkcja będzie dostępna pod `http://localhost:7071/api/summarize`.

## Jak przetestować

```bash
curl -X POST http://localhost:7071/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"incident": "WSTAW_OPIS"}'
```


