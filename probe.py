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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Safari/605.1.15",
    "Accept": "*/*",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.sofascore.com/football/match/auckland-fc-adelaide-united/Wibszevg",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "916c14",
    "Cookie": "cto_bidid=CzHTTl94enozeXFBbjc5RCUyRlFHZmUwVWVhUHlYWTBZYSUyQnBNOXR2Y1djTmRadXJOV29wWTlSYXRGRWxydFRtd0szMlBDZkR2cHR5dnM5dzhOR1BZZERERjd2elElM0QlM0Q; cto_bundle=SgAeHV9yRE9tMTUlMkIzRk90YnFnWFFmcGlHNlJOMmp2aUJOOU5mbVdHSSUyQkZwM3F6SVklMkZ6d1ZJc1NTQjdoT0UwOGhFRDk1UUY4cXprcHh1Z3JRYkhXNW5Ud1QzU01KSWwzUlNid0RDUzlBMnFhWUtkTmhhSVJQR1k4eDNQNHp2M1dqM2JRdA; _ga=GA1.1.1396489115.1778851201; _adv_sid=9bf6125c-a4fa-4a2d-9765-8c84edf125f7; _adv_uid=24fdf0ae-c8b8-4d86-8836-987850eff555",
}

ENDPOINTS = [
    "statistics",
    "incidents",
    "lineups",
    "graph",
    "momentum",
    "player-statistics",
]

USEFUL_KEYS: dict[str, str] = {
    "statistics":        "statistics",
    "incidents":         "incidents",
    "lineups":           "home",
    "graph":             "graphPoints",
    "momentum":          "momentum",
    "player-statistics": "home",
}


def load_events() -> list[dict]:
    with open("selected_events.json", "r") as file:
        return json.load(file)


def normalize_status_code(status_code: int) -> int | str:
    if status_code == 403:
        return "blocked"
    return status_code


def classify_response(
    endpoint: str,
    http_status: int | str,
    body: Any,
) -> tuple[bool, list[str]]:
    if http_status != 200 or not body or not isinstance(body, dict):
        return False, []

    top_keys = list(body.keys())[:10]

    key = USEFUL_KEYS.get(endpoint)
    if key is None:
        return bool(top_keys), top_keys

    value = body.get(key)
    if value is None:
        return False, top_keys
    if isinstance(value, list):
        return len(value) > 0, top_keys
    if isinstance(value, dict):
        return bool(value), top_keys
    return False, top_keys


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
                endpoint=endpoint,
                http_status=http_status,
                body=body,
            )

            return {
                "event_id":        event_id,
                "status":          status,
                "endpoint":        endpoint,
                "http_status":     http_status,
                "raw_http_status": response.status_code,
                "latency_ms":      latency_ms,
                "body_size":       len(response.text),
                "top_keys":        top_keys,
                "useful":          useful,
            }

        except requests.Timeout:
            retries += 1
            if retries > MAX_RETRIES:
                return {
                    "event_id":        event_id,
                    "status":          status,
                    "endpoint":        endpoint,
                    "http_status":     "timeout",
                    "raw_http_status": None,
                    "latency_ms":      -1,
                    "body_size":       0,
                    "top_keys":        [],
                    "useful":          False,
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
            time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    main()