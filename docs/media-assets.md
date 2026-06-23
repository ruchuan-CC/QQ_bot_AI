# Media Assets

私聊中的附件元信息会保存为 `material` 长期记忆。文本里出现的创作设定、图片/音频/视频线索会交给长期记忆抽取。

如果后续需要发送本地素材，可按下面目录组织：

```text
assets/comfort
assets/happy
assets/cute
assets/meme
assets/cyberpunk
assets/custom
```

支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`mp3`、`wav`、`mp4`。QQ 官方富媒体发送需要先上传 `/v2/users/{openid}/files` 获取 `file_info`，再通过 C2C 消息接口发送 media payload。当前主流程默认只发送文本。
