# Webhook

事件接入使用 Webhook：

```env
QQ_WEBHOOK_PATH=/qq/callback
```

公网回调地址通常是：

```text
https://your-domain.com/qq/callback
```

QQ 官方回调验证使用 BotSecret 派生 Ed25519 签名。本项目按官方示例对 `event_ts + plain_token` 生成响应签名。
