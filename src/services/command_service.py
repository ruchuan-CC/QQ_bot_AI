from __future__ import annotations

from src.services.memory_service import MemoryService
from src.services.user_service import UserService

HELP_TEXT = """可用命令：
/help
/status
/reset
/memory
/forget 关键词
/proactive on
/proactive off
/persona
/style 风格描述
/style reset
/assets
/share
/ping"""


class CommandService:
    def __init__(
        self,
        *,
        user_service: UserService,
        memory_service: MemoryService,
        persona_summary: str = "当前人格摘要将在配置 persona 后显示。",
        asset_summary: str = "素材库为空。",
        share_url: str = "分享链接需要配置 QQ 官方接口后生成。",
    ) -> None:
        self.user_service = user_service
        self.memory_service = memory_service
        self.persona_summary = persona_summary
        self.asset_summary = asset_summary
        self.share_url = share_url

    async def handle(self, qq_openid: str, content: str) -> str | None:
        text = content.strip()
        if not text.startswith("/"):
            return None
        if text == "/ping":
            return "pong"
        if text == "/help":
            return HELP_TEXT
        if text == "/status":
            user = await self.user_service.get_or_create(qq_openid)
            return (
                "Bot status\n"
                "QQ event mode: webhook\n"
                "memory enabled: true\n"
                "emotion enabled: true\n"
                f"current user proactive: {str(user.allow_proactive).lower()}"
            )
        if text == "/reset":
            return "已清空当前短期上下文，长期记忆不会删除。"
        if text == "/memory":
            return await self.memory_service.summary(qq_openid)
        if text.startswith("/forget "):
            keyword = text.removeprefix("/forget ").strip()
            deleted = await self.memory_service.forget(qq_openid, keyword)
            return f"已删除 {deleted} 条相关记忆。"
        if text == "/proactive on":
            await self.user_service.set_proactive(qq_openid, True)
            return "已开启互动召回候选。实际发送仍会遵守官方窗口、频控和安静时段。"
        if text == "/proactive off":
            await self.user_service.set_proactive(qq_openid, False)
            return "已关闭主动联系。"
        if text == "/persona":
            return self.persona_summary
        if text == "/style reset":
            await self.user_service.delete_setting(qq_openid, "style")
            return "已恢复默认回复风格。"
        if text.startswith("/style "):
            style = text.removeprefix("/style ").strip()
            await self.user_service.set_setting(qq_openid, "style", style)
            return f"已将你的回复风格设置为：{style}"
        if text == "/assets":
            return self.asset_summary
        if text == "/share":
            return self.share_url
        return "未知命令。发送 /help 查看可用命令。"
