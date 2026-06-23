from src.services.emotion_service import parse_emotion_json


def test_parse_emotion_json_clamps_scores_and_preserves_followup():
    state = parse_emotion_json(
        '{"mood": "低落", "valence": -2, "arousal": 2, "need": "comfort", '
        '"reason": "压力大", "should_followup": true, "followup_after_hours": 6}'
    )

    assert state.mood == "低落"
    assert state.valence == -1.0
    assert state.arousal == 1.0
    assert state.should_followup is True
    assert state.followup_after_hours == 6
