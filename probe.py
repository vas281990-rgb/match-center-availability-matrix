import json
import os
import time
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.sofascore.com/api/v1")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 1.5))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 10))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

ENDPOINTS = [
    "statistics",
    "incidents",
    "lineups",
    "graph",
    "momentum",
    "player-statistics",
]


def load_events() -> list[dict]:
    with open("selected_events.json", "r") as file:
        return json.load(file)


def normalize_status_code(status_code: int) -> int | str:
    # 403 means upstream blocked automated access.
    if status_code == 403:
        return "blocked"

    return status_code


def classify_response(
    http_status: int | str,
    body: Any,
) -> tuple[bool, list[str]]:
    # Only HTTP 200 can be useful.
    if http_status != 200:
        return False, []

    if not body:
        return False, []

    if isinstance(body, dict):
        top_keys = list(body.keys())

        if not top_keys:
            return False, top_keys

        return True, top_keys[:10]

    if isinstance(body, list):
        return len(body) > 0, []

    return False, []


def probe_endpoint(
    event_id: int,
    status: str,
    endpoint: str,
) -> dict:
    url = f"{BASE_URL}/event/{event_id}/{endpoint}"
    retries = 0

    while retries <= MAX_RETRIES:
        try:
            started = time.time()

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
            )

            latency_ms = int((time.time() - started) * 1000)

            try:
                body = response.json()
            except ValueError:
                body = None

            http_status = normalize_status_code(response.status_code)

            useful, top_keys = classify_response(
                http_status=http_status,
                body=body,
            )

            return {
                "event_id": event_id,
                "status": status,
                "endpoint": endpoint,
                "http_status": http_status,
                "raw_http_status": response.status_code,
                "latency_ms": latency_ms,
                "body_size": len(response.text),
                "top_keys": top_keys,
                "useful": useful,
            }

        except requests.Timeout:
            retries += 1

            if retries > MAX_RETRIES:
                return {
                    "event_id": event_id,
                    "status": status,
                    "endpoint": endpoint,
                    "http_status": "timeout",
                    "raw_http_status": None,
                    "latency_ms": -1,
                    "body_size": 0,
                    "top_keys": [],
                    "useful": False,
                }

            time.sleep(1)


def write_result(result: dict) -> None:
    with open("results.jsonl", "a") as file:
        file.write(json.dumps(result) + "\n")


def main() -> None:
    events = load_events()

    for event in events:
        event_id = event["event_id"]
        status = event["status"]

        for endpoint in ENDPOINTS:
            result = probe_endpoint(
                event_id=event_id,
                status=status,
                endpoint=endpoint,
            )

            print(
                f"[{status}] "
                f"event={event_id} "
                f"endpoint={endpoint} "
                f"status={result['http_status']} "
                f"latency={result['latency_ms']}ms "
                f"useful={result['useful']}"
            )

            write_result(result)

            # Basic rate limit to avoid hammering upstream.
            time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    main()