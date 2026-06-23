# Configuration

配置集中在 `.env`，参考 `.env.example`。

关键项：

- `QQ_APP_ID`：QQ 官方机器人 AppID。
- `QQ_CLIENT_SECRET`：获取 AccessToken 使用。
- `QQ_BOT_SECRET`：Webhook 验证使用。
- `AI_API_KEY`：xAI 或 OpenAI-compatible API key。
- `AI_BASE_URL`：默认 `https://api.x.ai/v1`。
- `QQ_ENABLE_GROUP=false` 与 `QQ_ENABLE_GUILD=false` 必须保持关闭。
- `PROACTIVE_ENABLED=false` 默认关闭互动召回。
