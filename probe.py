import json
import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

from policy import should_fetch


load_dotenv()

BASE_URL = os.getenv("BASE_URL")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 1.5))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 10))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    )
}


# Endpoints to probe
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


def classify_response(
    status_code: int,
    body: Any,
) -> tuple[bool, list[str]]:
    """
    Decide whether response is useful.
    """

    if status_code != 200:
        return False, []

    if not body:
        return False, []

    if isinstance(body, dict):
        keys = list(body.keys())

        if len(keys) == 0:
            return False, keys

        return True, keys[:10]

    return True, []


def probe_endpoint(
    event_id: int,
    status: str,
    endpoint: str,
) -> dict:
    """
    Probe one endpoint safely.
    """

    url = (
        f"{BASE_URL}/event/"
        f"{event_id}/{endpoint}"
    )

    retries = 0

    while retries <= MAX_RETRIES:
        try:
            started = time.time()

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
            )

            latency_ms = int(
                (time.time() - started) * 1000
            )

            try:
                body = response.json()
            except Exception:
                body = {}

            useful, top_keys = classify_response(
                response.status_code,
                body,
            )

            return {
                "event_id": event_id,
                "status": status,
                "endpoint": endpoint,
                "http_status": response.status_code,
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
        detail_id = event.get("detail_id")
        is_editor = event.get("is_editor", False)

        for endpoint in ENDPOINTS:

            if not should_fetch(
                endpoint,
                status,
                detail_id,
                is_editor,
            ):
                continue

            result = probe_endpoint(
                event_id,
                status,
                endpoint,
            )

            print(result)

            write_result(result)

            # Respect upstream
            time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    main()