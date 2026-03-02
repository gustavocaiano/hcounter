# Telegram Hour Counter Bot (Python) Plan

## Objective
Implement a minimal Python Telegram-first hour-tracking bot for personal use that:
- Sends a daily reminder asking for worked hours.
- Accepts incremental numeric entries via chat (`1`, `0.5`, `2`).
- Stores entries durably.
- Reports monthly totals, including `get02` for February.

## Constraints
- Empty repository; build from scratch with minimal files and dependencies.
- Practical stack only: Python 3.12+, `python-telegram-bot[job-queue]`, built-in `sqlite3`.
- MVP transport is Telegram long polling on Mini NUC (no HTTPS required).
- Optional HTTPS exposure is documented as non-MVP (webhook + reverse proxy/tunnel).
- No user interaction flow questions; sensible defaults must be encoded.
- Keep architecture easy to extend (single-user default, multi-chat-safe schema).

## Done Criteria
- Bot starts from env config and responds to `/start` and `/help`.
- Plain numeric text entries are accepted and persisted for current date.
- Invalid or negative inputs are rejected with a clear message.
- Daily reminder is scheduled at configured local time and delivered.
- `/month` returns current month total.
- `getMM` format (for example, `get02`) returns that month total for current year.
- Data survives restart (file-backed SQLite).
- Tests exist for parse/validation, `getMM` parsing, and monthly aggregation.
- Dev provides check log output from one verification command.

## Dev Checklist
1. **Project bootstrap (small batch)**
   - Create `pyproject.toml`, `.gitignore`, `.env.example`, `README.md`.
   - Create `src/hourbot/` and `tests/` skeleton.
   - Add dependency: `python-telegram-bot[job-queue]`.

2. **Config + data model (small batch)**
   - Implement `src/hourbot/config.py` with env vars: `BOT_TOKEN`, `TZ`, `DB_PATH`, `REMINDER_HOUR`, `REMINDER_MINUTE`, `OWNER_CHAT_ID`.
   - Implement `src/hourbot/db.py`:
     - table `entries(id, user_id, chat_id, entry_date, hours, raw_text, created_at)`
     - indexes `(user_id, entry_date)` and `(chat_id, entry_date)`
     - functions: init DB, insert entry, aggregate month total.

3. **Domain logic (small batch)**
   - Implement `src/hourbot/service.py`:
     - strict numeric parser (`>= 0`, decimal allowed)
     - `parse_getmm("get02") -> 2` validator
     - month aggregation adapters (current month and selected month)
     - deterministic formatting helpers.

4. **Telegram handlers + routing (small batch)**
   - Implement `src/hourbot/main.py` with:
     - commands: `/start`, `/help`, `/month`
     - text handler for numeric entries (`filters.TEXT & ~filters.COMMAND`)
     - regex handler for `^get(0[1-9]|1[0-2])$`.
   - On successful entry, reply with day subtotal and current month subtotal.

5. **Scheduling (small batch)**
   - Add `JobQueue` daily reminder at configured local time.
   - Reminder text asks for hours and examples (`0`, `0.5`, `1`, `2`).
   - MVP target chat: `OWNER_CHAT_ID` (explicitly documented).

6. **Tests (small batch)**
   - `tests/test_service_parse.py`: valid/invalid numeric inputs.
   - `tests/test_service_getmm.py`: valid/invalid `getMM`.
   - `tests/test_db_aggregation.py`: temp SQLite month sums.

7. **Deployment + ops docs (small batch)**
   - In `README.md`, add:
     - local run instructions
     - Mini NUC `systemd` unit
     - DB backup guidance
     - optional HTTPS/webhook path (reverse proxy/tunnel) clearly marked optional.

8. **Verification**
   - Run one primary check command and include tail output in Dev report:
     - `python -m pytest -q 2>&1 | tail -20`
   - If not runnable, report `Checks: N/A` with reason.

## QA Checklist
1. Confirm scope lock: only planned files/features introduced; no extra frameworks.
2. Validate command paths exist in code: `/start`, `/help`, `/month`, and `getMM`.
3. Validate numeric-entry behavior in logic: decimal acceptance, invalid/negative rejection.
4. Validate persistence and aggregation: SQLite file-backed schema and month total queries are present and coherent.
5. Validate scheduling: `JobQueue` daily reminder uses configured timezone and time.
6. Validate docs: Mini NUC run + systemd + backup + optional HTTPS section exist.
7. Validate test presence and relevance for parser/getMM/aggregation.
8. Validate Dev check logs include command and truncated output with clear PASS/FAIL/N/A gate signal.
