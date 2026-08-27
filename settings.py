import os
import sys


def _require(name):
    value = os.getenv(name)
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def _parse_int(name, value):
    try:
        return int(value)
    except (TypeError, ValueError):
        print(f"Environment variable {name} must be an integer, got: {value!r}", file=sys.stderr)
        sys.exit(1)


def _parse_emoji(value):
    stripped = value.strip().strip("'\"")
    try:
        return chr(int(stripped, 0))
    except ValueError:
        return stripped


_REQUIRED = (
    "SEEN_EMOJI_LONG_ID",
    "DOODLE_CHANNEL_ID",
    "DOODLE_SEEN_REACTION",
    "NOTIFY_ROLE_ID",
    "DISCORD_CLIENT_TOKEN",
    "DOODLE_LINKS",
)

_missing = [name for name in _REQUIRED if _require(name) is None]
if _missing:
    print("Missing required environment variables: " + ", ".join(_missing), file=sys.stderr)
    sys.exit(1)

seen_emoji_long_id = _require("SEEN_EMOJI_LONG_ID")
doodle_channel_id = _parse_int("DOODLE_CHANNEL_ID", _require("DOODLE_CHANNEL_ID"))
doodle_seen_reaction = _parse_emoji(_require("DOODLE_SEEN_REACTION"))
notify_role_id = _parse_int("NOTIFY_ROLE_ID", _require("NOTIFY_ROLE_ID"))
client_token = _require("DISCORD_CLIENT_TOKEN")
doodle_links = [link.strip() for link in _require("DOODLE_LINKS").split(",") if link.strip()]
