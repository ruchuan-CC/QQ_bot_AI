# QQ Private AI Companion Bot

一个完整、可开源、可部署、可复用的官方 QQ 机器人平台 C2C 私聊 AI Companion Bot。

本项目只支持 QQ 官方 C2C 私聊，不支持 QQ 群聊、QQ 频道、NapCat、OneBot、NoneBot 或任何非官方协议。

## 功能特性

- 官方 QQ Bot C2C 私聊 Webhook 接入。
- 可选 WebSocket Gateway 配置入口。
- C2C 消息发送、富媒体上传、撤回和分享链接接口封装。
- xAI / OpenAI-compatible AI Provider。
- 自定义 persona Markdown。
- 用户 style、长期记忆、情绪识别。
- 官方互动召回口径的 wakeup window。
- Docker、本地 Python、systemd 部署。
- pytest、ruff、compileall、Docker build CI。

## 为什么只支持 QQ 私聊

Companion Bot 的核心是长期一对一对话。群聊和频道会引入不同的权限、上下文、风控和隐私边界，因此本项目只实现官方 C2C 单聊。所有群聊、频道事件都会被忽略，不回复。

## 官方 QQ 机器人平台准备

1. 在 QQ 机器人官方平台创建应用。
2. 获取 `AppID`，写入 `QQ_APP_ID`。
3. 获取 `ClientSecret`，写入 `QQ_CLIENT_SECRET`。
4. 获取 `BotSecret`，写入 `QQ_BOT_SECRET`。
5. 配置 Webhook 回调地址：`https://your-domain.com/qq/callback`。
6. 只订阅 C2C 私聊、好友添加、好友删除、主动消息授权相关事件。

## 配置 xAI 或其他模型

默认配置：

```env
AI_PROVIDER=xai
AI_BASE_URL=https://api.x.ai/v1
AI_MODEL=grok-4.20-0309-non-reasoning
AI_API_KEY=
```

其他 OpenAI-Compatible 模型只需要替换 `AI_BASE_URL`、`AI_MODEL` 和 `AI_API_KEY`。

## Docker 部署

```bash
git clone https://github.com/ruchuan-CC/QQ_bot_AI.git
cd QQ_bot_AI
cp .env.example .env
# 编辑 .env
docker compose up -d
```

## 本地部署

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python bot.py
```

## systemd 部署

```bash
sudo cp deploy/qq-private-ai-companion-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now qq-private-ai-companion-bot
```

确认 service 文件中的 `/opt/qq-private-ai-companion-bot` 与实际部署路径一致。

## HTTPS / Nginx

参考 `deploy/nginx.example.conf`。QQ 官方 Webhook 需要公网 HTTPS 地址。

## .env 配置说明

核心配置见 `.env.example`：

- `QQ_APP_ID`：QQ 官方机器人 AppID。
- `QQ_CLIENT_SECRET`：用于获取 AccessToken。
- `QQ_BOT_SECRET`：用于 Webhook 回调验证。
- `QQ_EVENT_MODE`：默认 `webhook`，可设为 `websocket`。
- `QQ_ENABLE_C2C=true`：保持开启。
- `QQ_ENABLE_GROUP=false`、`QQ_ENABLE_GUILD=false`：必须保持关闭。
- `AI_API_KEY`：AI 模型 key。
- `AI_MODEL`：默认 `grok-4.20-0309-non-reasoning`。
- `BOT_PERSONA_FILE`：persona Markdown 文件路径。
- `DATABASE_URL`：默认 SQLite。
- `PROACTIVE_ENABLED=false`：主动消息默认关闭。

## 人格文件

默认文件：`persona/default.md`。

可复制 `persona/examples/` 下的模板并修改 `.env`：

```env
BOT_PERSONA_FILE=./persona/examples/concise-professional.md
```

`/style 风格描述` 只影响当前用户，不修改全局 persona。

## 用户命令

- `/help`：显示命令。
- `/status`：显示状态，不输出密钥。
- `/reset`：清空短期上下文。
- `/memory`：显示长期记忆摘要。
- `/forget 关键词`：删除相关记忆。
- `/proactive on`：同意进入互动召回候选。
- `/proactive off`：关闭主动联系。
- `/persona`：显示人格摘要。
- `/style 风格描述`：设置当前用户回复风格。
- `/style reset`：恢复默认风格。
- `/assets`：显示素材统计。
- `/share`：生成机器人分享链接。
- `/ping`：返回 pong。

## 长期记忆

记忆抽取只保存长期有价值的信息，例如偏好、长期目标、项目和常用工具。不保存无意义闲聊、纯表情或一次性状态。用户可通过 `/forget` 删除自己的记忆。

## 情绪识别

情绪识别输出 mood、valence、arousal、need、reason、should_followup 和 followup_after_hours，用于调整回复语气、判断是否需要 comfort 类素材和是否进入 wakeup 候选。

## 主动消息 / 互动召回

本项目只实现官方互动召回口径，不实现旧式普通主动推送。

发送必须满足：

- `PROACTIVE_ENABLED=true`
- 用户 `/proactive on`
- QQ 官方允许主动消息
- 当前不在 quiet hours
- 未超过项目月限流
- 命中 wakeup window
- payload 使用 `is_wakeup=true`

## 官方频率限制

项目不会绕过 QQ 官方限制。C2C 消息、富媒体上传、撤回、互动召回均以官方平台当前限制为准。`docs/qq-official-api-matrix.md` 记录本项目能力矩阵。

## 图片 / 富媒体素材

素材目录：

```text
assets/comfort
assets/happy
assets/cute
assets/meme
assets/cyberpunk
assets/custom
```

支持 jpg、jpeg、png、gif、webp、mp3、wav、mp4。发送失败会降级为文本。

## 数据库备份

默认 SQLite 文件是 `data/bot.db`。备份时停止服务后复制该文件即可。PostgreSQL 可通过 `DATABASE_URL` 配置，首版默认以 SQLite 验收。

## 日志查看

Docker：

```bash
docker compose logs -f
```

systemd：

```bash
journalctl -u qq-private-ai-companion-bot -f
```

## 安全注意事项

- 不提交 `.env`。
- 不提交真实 key。
- 不保存 QQ 密码。
- 不读取宿主机敏感文件。
- 不允许 QQ 用户执行服务器命令。
- 日志必须脱敏 `QQ_CLIENT_SECRET`、`QQ_BOT_SECRET`、`AI_API_KEY` 和 AccessToken。

## 开发说明

```bash
pip install -r requirements.txt
make test
make lint
python -m compileall .
```

## 测试说明

测试不需要真实 QQ 或 AI key。当前覆盖配置、token 缓存、Webhook 签名、事件解析、群聊忽略、payload 构造、persona、prompt、memory、emotion、wakeup、素材、分段和脱敏。

## 常见问题

### 可以接群聊吗？

不可以。本项目不会实现群聊。

### 可以用 NapCat / OneBot 吗？

不可以。本项目只使用 QQ 官方机器人平台。

### 主动消息为什么默认关闭？

主动联系涉及用户体验和官方规则。项目默认关闭，用户同意后也只进入互动召回候选，并继续遵守官方窗口和频控。
