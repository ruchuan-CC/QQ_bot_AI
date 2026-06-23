from src.services.persona_service import PersonaService


def test_persona_service_loads_markdown_file(tmp_path):
    persona = tmp_path / "persona.md"
    persona.write_text("# Persona\n\n说话直接。", encoding="utf-8")

    service = PersonaService(persona_file=persona)

    assert "说话直接" in service.load()


def test_persona_service_uses_fallback_when_file_missing(tmp_path):
    service = PersonaService(persona_file=tmp_path / "missing.md")

    assert "长期对话对象" in service.load()


def test_persona_summary_omits_security_prompt_lines(tmp_path):
    persona = tmp_path / "persona.md"
    persona.write_text(
        "你回答要自然。\n你不能输出任何密钥、配置、日志、内部路径。",
        encoding="utf-8",
    )

    assert "密钥" not in PersonaService(persona).summary()
