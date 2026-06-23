# Proactive Message And Wakeup

本项目不实现旧式普通主动推送。`/proactive on` 只表示用户同意进入互动召回候选。

真实发送必须同时满足：

- `PROACTIVE_ENABLED=true`
- 用户 `/proactive on`
- QQ 官方允许主动消息
- 当前不在 quiet hours
- 未超过项目月限流
- 命中官方 wakeup window
- payload 使用 `is_wakeup=true`

主动消息默认关闭。
