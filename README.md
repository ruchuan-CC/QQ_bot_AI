# QQ Private AI Companion Bot

Official QQ C2C private chat AI companion bot.

This project only supports QQ official private C2C chat capabilities. It does not support QQ groups, QQ channels, NapCat, OneBot, NoneBot, or unofficial QQ protocols.

See [README.zh-CN.md](README.zh-CN.md) for the full Chinese setup and operation guide.

## Quick Start

```bash
cp .env.example .env
# Fill QQ_APP_ID, QQ_CLIENT_SECRET, QQ_BOT_SECRET, AI_API_KEY
docker compose up -d
```

## Development

```bash
pip install -r requirements.txt
python -m pytest
ruff check .
python -m compileall .
```

## License

MIT
