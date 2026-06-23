# WebSocket Gateway

WebSocket Gateway 是可选模式：

```env
QQ_EVENT_MODE=websocket
QQ_ENABLE_WEBSOCKET=true
```

首版保留 gateway session 结构和配置入口，事件处理仍复用 C2C-only dispatcher。生产使用优先推荐 Webhook。
