# FAQ

## 为什么不支持群聊？

本项目定位是官方 QQ C2C 私聊 AI Companion Bot。群聊、频道和非官方协议都会扩大权限、上下文和安全边界，因此明确 out-of-scope。

## 可以使用 OpenAI 之外的模型吗？

可以。默认使用 Responses API；只兼容 OpenAI Chat Completions API 的服务，把 `AI_API_STYLE` 改为 `chat_completions`，再配置 `AI_BASE_URL`、`AI_API_KEY` 和 `AI_MODEL`。

## 没有真实 QQ Key 能测试吗？

可以。测试使用 mock 和纯本地解析，不需要真实 QQ 或 AI key。
