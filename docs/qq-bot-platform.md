# QQ Bot Platform

1. 在 QQ 机器人官方平台创建机器人应用。
2. 获取 AppID 和 ClientSecret，写入 `.env` 的 `QQ_APP_ID` 与 `QQ_CLIENT_SECRET`。
3. 获取 BotSecret，写入 `QQ_BOT_SECRET`，用于 Webhook 回调验证。
4. 只订阅 C2C 私聊、好友添加、好友删除和主动消息授权相关事件。
5. 不启用群聊、频道或非官方协议能力。
