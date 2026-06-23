from src.qq.events import EventType, parse_event


def test_parse_c2c_message_event_extracts_openid_content_and_message_id():
    event = parse_event(
        {
            "id": "event-1",
            "t": "C2C_MESSAGE_CREATE",
            "d": {
                "author": {"user_openid": "openid-1"},
                "content": "hello",
                "id": "msg-1",
                "attachments": [{"id": "file-1"}],
            },
        }
    )

    assert event.type == EventType.C2C_MESSAGE_CREATE
    assert event.openid == "openid-1"
    assert event.content == "hello"
    assert event.msg_id == "msg-1"
    assert event.event_id == "event-1"
    assert event.attachments == [{"id": "file-1"}]


def test_parse_group_event_is_marked_out_of_scope():
    event = parse_event({"id": "event-2", "t": "GROUP_AT_MESSAGE_CREATE", "d": {}})

    assert event.is_c2c is False
    assert event.out_of_scope is True
