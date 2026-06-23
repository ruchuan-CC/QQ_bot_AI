# Installation

## Docker

```bash
cp .env.example .env
docker compose up -d
```

## Local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python bot.py
```

## systemd

复制 `deploy/qq-private-ai-companion-bot.service` 到 `/etc/systemd/system/`，确认 `WorkingDirectory`、`ExecStart` 和 `EnvironmentFile` 与实际路径一致。
