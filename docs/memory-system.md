# Memory System

长期记忆用于保存用户在私聊中透露的 persona、偏好、长期目标、项目、常用工具、素材线索和反复出现的情绪模式。

原始用户消息永久保存在 `messages` 表；抽取后的长期资料保存在 `memories` 表。低价值临时信息通常不会进入抽取记忆，但原始消息仍可用于审计和后续分析。

主要类型：

- `persona`
- `emotion`
- `proactive`
- `material`
- `preference`
- `relationship`
- `fact`
- `note`
