EMOTION_RECOGNITION_PROMPT = """识别用户当前情绪，只返回 JSON，不要解释。

返回格式：
{
  "mood": "低落",
  "valence": -0.6,
  "arousal": 0.4,
  "need": "comfort",
  "reason": "用户表达了压力和疲惫",
  "should_followup": true,
  "followup_after_hours": 6
}

字段要求：
- mood：简短中文情绪词。无法判断时用 "unknown"。
- valence：-1 到 1，负面为负，正面为正。
- arousal：-1 到 1，平静偏低，激动/焦虑偏高。
- need：comfort、listen、advice、celebrate、space、none 中选一个。
- reason：从用户消息概括原因，不能编造。
- should_followup：用户明显需要之后继续关心时为 true。
- followup_after_hours：主动关心的建议间隔，没有需要则为 0。"""
