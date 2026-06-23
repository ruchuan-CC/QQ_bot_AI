# Configuration

配置集中在 `.env`，参考 `.env.example`。

关键项：

- `QQ_APP_ID`：QQ 官方机器人 AppID。
- `QQ_CLIENT_SECRET`：获取 AccessToken 使用。
- `QQ_BOT_SECRET`：Webhook 验证使用。
- `AI_API_KEY`：xAI 或 OpenAI-compatible API key。
- `AI_BASE_URL`：默认 `https://api.x.ai/v1`。
- `AI_MODEL`：默认 `grok-4.3`。
- `AI_API_STYLE`：默认 `responses`；只支持 Chat Completions 的兼容服务可改为 `chat_completions`。
- `QQ_WEBHOOK_PATH`：默认 `/qq/callback`。
- `BOT_PERSONA_FILE`：persona Markdown 文件路径。
- `DATABASE_URL`：默认 `sqlite+aiosqlite:///./data/bot.db`。
