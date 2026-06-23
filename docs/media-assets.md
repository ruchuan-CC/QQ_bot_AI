# Media Assets

素材目录：

```text
assets/comfort
assets/happy
assets/cute
assets/meme
assets/cyberpunk
assets/custom
```

支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`mp3`、`wav`、`mp4`。发送时先上传 `/v2/users/{openid}/files` 获取 `file_info`，再通过 C2C 消息接口发送 media payload。失败时降级为文本。
