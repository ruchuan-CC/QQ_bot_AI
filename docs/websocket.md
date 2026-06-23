# WebSocket Gateway

当前部署入口只支持 Webhook。

仓库保留 `src/qq/websocket_gateway.py` 的结构类型，便于后续扩展；clone 后直接使用时不要配置 WebSocket，只需要配置 `QQ_WEBHOOK_PATH` 并在 QQ 机器人平台填写公网 HTTPS 回调地址。
