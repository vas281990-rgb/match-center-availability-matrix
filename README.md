# Match Center Availability Matrix

## Goal

Research SofaScore match-center endpoint availability
across different event lifecycle states:

- notstarted
- inprogress
- finished

The task focuses on:
- endpoint lifecycle behavior
- upstream reliability
- availability patterns
- production-safe probing

---

# Selected Events

Events were selected from:
- top leagues
- regular professional leagues
- lower/amateur competitions where available

At least 3 events per status were analyzed.

---

# Probe Strategy

The probe script uses:

- request timeout
- retry logic
- rate limiting
- endpoint policy filtering
- JSONL structured logging

The script intentionally distinguishes:

- 200 useful
- 200 empty
- 404
- timeout

instead of relying only on HTTP status codes.

---

# Endpoint Matrix

| Endpoint | notstarted | inprogress | finished |
|---|---|---|---|
| statistics | 200 useful | 200 useful | 200 useful |
| incidents | 200 empty | 200 useful | 200 useful |
| lineups | 200 useful | 200 useful | 200 useful |
| graph | 200 empty | 200 useful | 404 |
| momentum | 200 empty | 200 useful | 404 |
| player-statistics | 404 | 200 empty | 200 useful |

---

# Key Findings

## Continuous endpoints

These endpoints exist during most event stages:

- statistics
- incidents
- details

Good candidates for continuous polling.

---

## Prematch-oriented endpoints

These endpoints are useful before kickoff:

- lineups
- pregame-form

Availability varies by tournament quality.

---

## Live-oriented endpoints

These endpoints become useful only during live matches:

- graph
- momentum

Should not be aggressively queried outside live state.

---

## Post-match endpoints

Useful mostly after completion:

- player-statistics

---

# Important Observations

## 200 empty != unavailable

Some endpoints return:
- HTTP 200
- empty body
- partial JSON

This should not be interpreted as permanent absence.

---

## detailId=None does not mean no data

Some events still expose useful endpoints even when
detailId is null.

---

## isEditor=true

Editor events should be hard-blocked
from polling logic.

---

# Limitations

- Small event sample size
- Availability differs between tournaments
- Lower leagues often have partial coverage
- Some endpoints appear conditionally

---

# Reproducibility

## Install

```bash
pip install -r requirements.txt# Match Center Availability Matrix

## Goal

Research SofaScore match-center endpoint availability
across different event lifecycle states:

- notstarted
- inprogress
- finished

The task focuses on:
- endpoint lifecycle behavior
- upstream reliability
- availability patterns
- production-safe probing

---

# Selected Events

Events were selected from:
- top leagues
- regular professional leagues
- lower/amateur competitions where available

At least 3 events per status were analyzed.

---

# Probe Strategy

The probe script uses:

- request timeout
- retry logic
- rate limiting
- endpoint policy filtering
- JSONL structured logging

The script intentionally distinguishes:

- 200 useful
- 200 empty
- 404
- timeout

instead of relying only on HTTP status codes.

---

# Endpoint Matrix

| Endpoint | notstarted | inprogress | finished |
|---|---|---|---|
| statistics | 200 useful | 200 useful | 200 useful |
| incidents | 200 empty | 200 useful | 200 useful |
| lineups | 200 useful | 200 useful | 200 useful |
| graph | 200 empty | 200 useful | 404 |
| momentum | 200 empty | 200 useful | 404 |
| player-statistics | 404 | 200 empty | 200 useful |

---

# Key Findings

## Continuous endpoints

These endpoints exist during most event stages:

- statistics
- incidents
- details

Good candidates for continuous polling.

---

## Prematch-oriented endpoints

These endpoints are useful before kickoff:

- lineups
- pregame-form

Availability varies by tournament quality.

---

## Live-oriented endpoints

These endpoints become useful only during live matches:

- graph
- momentum

Should not be aggressively queried outside live state.

---

## Post-match endpoints

Useful mostly after completion:

- player-statistics

---

# Important Observations

## 200 empty != unavailable

Some endpoints return:
- HTTP 200
- empty body
- partial JSON

This should not be interpreted as permanent absence.

---

## detailId=None does not mean no data

Some events still expose useful endpoints even when
detailId is null.

---

## isEditor=true

Editor events should be hard-blocked
from polling logic.

---

# Limitations

- Small event sample size
- Availability differs between tournaments
- Lower leagues often have partial coverage
- Some endpoints appear conditionally

---

# Reproducibility

## Install

```bash
pip install -r requirements.txt