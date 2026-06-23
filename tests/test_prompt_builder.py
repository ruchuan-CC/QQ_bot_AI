from src.prompts.chat_prompt import ChatPromptBuilder


def test_prompt_builder_combines_persona_memory_emotion_style_history_and_message():
    prompt = ChatPromptBuilder().build(
        persona="你是希恩X。",
        memories=["用户喜欢赛博朋克风格图片"],
        emotion={"mood": "低落", "need": "comfort"},
        style="简洁直接",
        history=[{"role": "user", "content": "上次聊图像风格"}],
        current_message="今天有点累",
    )

    assert "你是希恩X" in prompt
    assert "赛博朋克" in prompt
    assert "低落" in prompt
    assert "简洁直接" in prompt
    assert "今天有点累" in prompt
