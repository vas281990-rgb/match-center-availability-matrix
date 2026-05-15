import json
import time
from playwright.sync_api import sync_playwright

ENDPOINTS = [
    "statistics",
    "incidents",
    "lineups",
    "graph",
    "momentum",
    "player-statistics",
]

USEFUL_KEYS = {
    "statistics":        "statistics",
    "incidents":         "incidents",
    "lineups":           "home",
    "graph":             "graphPoints",
    "momentum":          "momentum",
    "player-statistics": "home",
}



def classify(endpoint: str, body: dict) -> bool:
    if not body or not isinstance(body, dict):
        return False
    key = USEFUL_KEYS.get(endpoint)
    if not key:
        return bool(body)
    value = body.get(key)
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return bool(value)
    return False


def main():
    with open("selected_events.json") as f:
        events = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://www.sofascore.com", wait_until="domcontentloaded")
        time.sleep(2)

        for event in events:
            event_id = event["event_id"]
            status = event["status"]

            for endpoint in ENDPOINTS:
                url = f"https://www.sofascore.com/api/v1/event/{event_id}/{endpoint}"

                try:
                    t0 = time.perf_counter()
                    api_response = context.request.get(url)
                    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
                    http_status = api_response.status

                    try:
                        raw_text = api_response.text() 
                        body = api_response.json()
                        body_size = len(raw_text)
                    except Exception:
                        body = None
                        body_size = 0  

                    useful = classify(endpoint, body) if http_status == 200 else False
                    top_keys = list(body.keys())[:10] if isinstance(body, dict) else []

                except Exception as e:
                    http_status = "error"
                    body = None
                    useful = False
                    top_keys = []
                    latency_ms = -1
                    body_size = 0

                result = {
                    "event_id":    event_id,
                    "status":      status,
                    "endpoint":    endpoint,
                    "http_status": http_status,
                    "latency_ms":  latency_ms, 
                    "body_size":   body_size, 
                    "useful":      useful,
                    "top_keys":    top_keys,
                }

                print(
                    f"[{status}] event={event_id} endpoint={endpoint} "
                    f"status={http_status} useful={useful}"
                )

                with open("results.jsonl", "a") as f:
                    f.write(json.dumps(result) + "\n")

                time.sleep(1.5)

        browser.close()


if __name__ == "__main__":
    main()