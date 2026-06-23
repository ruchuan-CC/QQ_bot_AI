import pytest

from src.qq.message_types import C2CMessagePayloadBuilder


def test_build_text_message_payload_includes_msg_id_and_msg_seq():
    payload = C2CMessagePayloadBuilder.text(
        content="hello",
        msg_id="inbound-msg",
        msg_seq=3,
    )

    assert payload["content"] == "hello"
    assert payload["msg_id"] == "inbound-msg"
    assert payload["msg_seq"] == 3
    assert "event_id" not in payload


def test_build_wakeup_payload_rejects_passive_reply_ids():
    with pytest.raises(ValueError):
        C2CMessagePayloadBuilder.text(
            content="wake",
            msg_id="inbound-msg",
            msg_seq=1,
            is_wakeup=True,
        )


def test_build_media_payload_uses_file_info():
    payload = C2CMessagePayloadBuilder.media(file_info="file-info-token", msg_seq=8)

    assert payload["msg_type"] == 7
    assert payload["media"]["file_info"] == "file-info-token"
    assert payload["msg_seq"] == 8
