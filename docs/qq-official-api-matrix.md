# QQ Official API Matrix

更新时间：2026-06-23。实现前已核验 QQ 机器人官方文档中与服务端 API、Webhook、WebSocket Gateway、消息收发、单聊富媒体、撤回、分享链接和事件相关的页面。本文档只作为本项目能力边界，不替代官方文档。

## C2C 私聊能力

| 能力 | 官方路径 / 事件 | 方法 | 状态 | 特殊权限 | 只支持私聊 | 频率限制 | 项目模块 | 测试覆盖 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 获取 AccessToken | `https://bots.qq.com/app/getAppAccessToken` | POST | implemented | AppID + ClientSecret | 否 | token 有效期 | `src/qq/auth.py` | `test_qq_auth.py` |
| C2C 文本/Markdown/Ark/Embed/Media 消息 | `/v2/users/{openid}/messages` | POST | implemented | C2C 消息权限 | 是 | 官方 C2C 消息频控 | `src/qq/client.py` | `test_message_payloads.py` |
| C2C 富媒体上传 | `/v2/users/{openid}/files` | POST | implemented | 富媒体权限 | 是 | 官方媒体频控 | `src/qq/client.py` | `test_message_payloads.py` |
| C2C 消息撤回 | `/v2/users/{openid}/messages/{message_id}` | DELETE | implemented | 只能撤回机器人消息 | 是 | 官方撤回窗口 | `src/qq/client.py` | compile/test import |
| 机器人分享链接 | `/v2/generate_url_link` | POST | implemented | 分享链接权限 | 否 | 官方接口频控 | `src/qq/client.py` | docs |
| C2C 私聊消息事件 | `C2C_MESSAGE_CREATE` | Event | implemented | 事件订阅 | 是 | 被动回复窗口 | `src/qq/events.py` | `test_c2c_event.py` |
| 好友添加 | `FRIEND_ADD` | Event | implemented | 事件订阅 | 是 | 无项目内发送默认 | `src/qq/events.py` | `test_c2c_event.py` |
| 好友删除 | `FRIEND_DEL` | Event | implemented | 事件订阅 | 是 | 不发送 | `src/qq/events.py` | `test_c2c_event.py` |
| 主动消息允许/拒绝 | 官方主动消息授权事件 | Event | implemented | 用户授权 | 是 | 官方规则 | `src/qq/events.py` | event/proactive tests |
| 互动召回 | `is_wakeup=true` | POST | implemented | 官方 wakeup 窗口 | 是 | same_day / day_1_3 / day_3_7 / day_7_30 | `src/services/proactive_service.py` | `test_wakeup_windows.py` |
| Webhook 回调验证 | Webhook validation payload | POST | implemented | BotSecret | 否 | 无 | `src/qq/webhook.py` | signature tests |
| WebSocket Gateway | Gateway / Identify / Heartbeat / Resume | WS | scaffolded | Gateway 权限 | 否 | 官方 WS 规则 | `src/qq/websocket_gateway.py` | compile/test import |

## Out Of Scope

| 能力 | 官方路径 / 事件 | 状态 | 原因 |
| --- | --- | --- | --- |
| 群聊事件 | `GROUP_AT_MESSAGE_CREATE`、`GROUP_MSG_RECEIVE` 等 | out-of-scope | 本项目只做 C2C 私聊 |
| 频道事件 | guild/channel 相关事件 | out-of-scope | 本项目不做 QQ 频道 |
| 频道私信 | direct message 相关能力 | out-of-scope | 不是 C2C 单聊 |
| 群管理 | group/member 管理接口 | out-of-scope | 不实现群逻辑 |
| NapCat / OneBot / NoneBot | 非官方协议或框架 | forbidden | 必须使用 QQ 官方平台 |

收到 out-of-scope 事件时，服务只记录 debug 日志并返回 ignored，不回复用户。
