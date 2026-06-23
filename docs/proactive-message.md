# Proactive Message And Wakeup

当前主流程只记录主动关心线索，不默认主动发送消息。情绪识别认为需要后续关心时，会把线索保存为 `proactive` 长期记忆。

后续如果开启发送，不实现旧式普通主动推送，只能使用 QQ 官方互动召回口径。

真实发送必须同时满足：

- `PROACTIVE_ENABLED=true`
- QQ 官方允许主动消息
- 当前不在 quiet hours
- 未超过项目月限流
- 命中官方 wakeup window
- payload 使用 `is_wakeup=true`

主动消息默认关闭。
