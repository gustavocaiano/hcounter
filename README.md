# Hourbot

Telegram-first hour tracking bot (Python 3.12+) for personal daily logging with SQLite persistence.

## Bot commands

See [`commands.md`](commands.md) for the full list of Telegram commands and accepted input formats.

## Local run (MVP: Telegram long polling)

After a fresh clone, or after `git pull`, run:

```bash
make setup
```

Then edit `.env` with your real `BOT_TOKEN` and `OWNER_CHAT_ID`, and start:

```bash
make run
```

Useful helper:

```bash
make test
```

Required environment variables:
- `BOT_TOKEN`
- `TZ` (example: `America/Sao_Paulo`)
- `DB_PATH` (example: `/opt/hourbot/data/hourbot.db`)
- `REMINDER_HOUR`
- `REMINDER_MINUTE`
- `OWNER_CHAT_ID`

## Mini NUC deployment (`systemd`)

Example unit file (`/etc/systemd/system/hourbot.service`):

```ini
[Unit]
Description=Hourbot Telegram worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=hourbot
Group=hourbot
WorkingDirectory=/opt/hourbot/app
EnvironmentFile=/opt/hourbot/app/.env
ExecStart=/opt/hourbot/app/.venv/bin/python -m hourbot.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and manage:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hourbot.service
sudo systemctl status hourbot.service
journalctl -u hourbot.service -f
```

## SQLite backup guidance

- Keep `DB_PATH` on persistent disk (not `/tmp`).
- Run periodic backups with `sqlite3` `.backup` to avoid partial copies.
- Keep timestamped files and prune old backups with a retention policy.

Example backup script:

```bash
#!/usr/bin/env bash
set -euo pipefail

DB_PATH="/opt/hourbot/data/hourbot.db"
BACKUP_DIR="/opt/hourbot/backups"
STAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/hourbot_$STAMP.db'"

# keep last 14 backups
ls -1t "$BACKUP_DIR"/hourbot_*.db | tail -n +15 | xargs -r rm -f
```

You can schedule this with `cron` or a `systemd` timer.

## Optional (non-MVP): HTTPS webhook mode

Long polling is the MVP and works without HTTPS. Webhook mode is optional for internet-exposed setups.

If you switch to webhooks later:
- Place the bot behind an HTTPS reverse proxy (for example Nginx/Caddy + Let's Encrypt), or
- Use a secure tunnel provider that offers stable HTTPS endpoints.

Typical path:
1. Expose a stable HTTPS URL.
2. Add webhook handling in app runtime.
3. Register Telegram webhook to that URL.
4. Keep firewall rules tight and rotate secrets/tokens as needed.

Do not treat webhook setup as required for MVP deployment on a Mini NUC.
