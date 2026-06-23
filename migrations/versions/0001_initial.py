from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("nickname", sa.String(length=128), nullable=True),
        sa.Column("source_scene", sa.String(length=128), nullable=True),
        sa.Column("source_scene_param", sa.String(length=256), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("allow_proactive", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("qq_allows_proactive", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("quiet_hours_start", sa.String(length=5), nullable=False, server_default="23:30"),
        sa.Column("quiet_hours_end", sa.String(length=5), nullable=False, server_default="08:30"),
        sa.Column("profile_summary", sa.Text(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("qq_openid"),
    )
    op.create_index("ix_users_qq_openid", "users", ["qq_openid"])
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("scene_type", sa.String(length=16), nullable=False, server_default="c2c"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_conversations_qq_openid", "conversations", ["qq_openid"])
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("qq_msg_id", sa.String(length=128), nullable=True),
        sa.Column("qq_event_id", sa.String(length=128), nullable=True),
        sa.Column("qq_message_id_sent", sa.String(length=128), nullable=True),
        sa.Column("msg_seq", sa.Integer(), nullable=True),
        sa.Column("raw_event_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_messages_qq_openid", "messages", ["qq_openid"])
    op.create_index("ix_messages_qq_msg_id", "messages", ["qq_msg_id"])
    op.create_table(
        "memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("memory_type", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_message_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_memories_qq_openid", "memories", ["qq_openid"])
    op.create_table(
        "emotion_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("mood", sa.String(length=64), nullable=False),
        sa.Column("valence", sa.Float(), nullable=False),
        sa.Column("arousal", sa.Float(), nullable=False),
        sa.Column("need", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("should_followup", sa.Boolean(), nullable=False),
        sa.Column("followup_after_hours", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("qq_openid"),
    )
    op.create_index("ix_emotion_states_qq_openid", "emotion_states", ["qq_openid"])
    op.create_table(
        "proactive_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("asset_tag", sa.String(length=64), nullable=True),
        sa.Column("is_wakeup", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("official_window_type", sa.String(length=32), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_proactive_logs_qq_openid", "proactive_logs", ["qq_openid"])
    op.create_table(
        "wakeup_windows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("anchor_user_message_id", sa.Integer(), nullable=True),
        sa.Column("anchor_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_type", sa.String(length=32), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wakeup_windows_qq_openid", "wakeup_windows", ["qq_openid"])
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qq_openid", sa.String(length=128), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_settings_qq_openid", "user_settings", ["qq_openid"])
    op.create_table(
        "api_call_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("endpoint", sa.String(length=256), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "api_call_logs",
        "user_settings",
        "wakeup_windows",
        "proactive_logs",
        "emotion_states",
        "memories",
        "messages",
        "conversations",
        "users",
    ]:
        op.drop_table(table)
