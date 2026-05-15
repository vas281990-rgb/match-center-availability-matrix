from typing import Optional


# Endpoints grouped by lifecycle behavior
PREMATCH_ONLY = {
    "lineups",
    "pregame-form",
}

LIVE_ONLY = {
    "live-standings",
    "graph",
}

POSTMATCH_ONLY: set = set()

CONTINUOUS = {
    "statistics",
    "incidents",
    "details",
}
DETAIL_REQUIRED = {
    "momentum",
    "player-statistics",
}

def should_fetch(
    endpoint: str,
    event_status: str,
    detail_id: Optional[int],
    is_editor: bool,
) -> bool:
    """
    Decide whether endpoint should be fetched.

    Rules:
    - isEditor=true is always blocked
    - detail_id=None does not automatically mean unavailable
    - endpoint lifecycle matters
    """

    # Hard ban editor events
    if is_editor:
        return False
    
    if endpoint in DETAIL_REQUIRED:
        return detail_id is not None

    # Continuous endpoints
    if endpoint in CONTINUOUS:
        return True

    # Prematch endpoints
    if endpoint in PREMATCH_ONLY:
        return event_status == "notstarted"

    # Live only endpoints
    if endpoint in LIVE_ONLY:
        return event_status == "inprogress"

    # Post-match endpoints
    if endpoint in POSTMATCH_ONLY:
        return event_status == "finished"

    # Unknown endpoints:
    # allow probing carefully
    return True