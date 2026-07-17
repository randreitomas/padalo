from __future__ import annotations

import re

from padalo_agent.schemas.models import AgentStreamEvent


def encode_sse(event: AgentStreamEvent) -> str:
    return f"event: {event.event}\ndata: {event.model_dump_json()}\n\n"


class StructuredMessageExtractor:
    """Streams the message value from a strict JSON response without showing JSON chrome."""

    def __init__(self, field_name: str = "message") -> None:
        self._pattern = re.compile(rf'"{re.escape(field_name)}"\s*:\s*"')
        self._buffer = ""
        self._index = 0
        self._started = False
        self._complete = False

    def feed(self, chunk: str) -> str:
        if self._complete:
            return ""

        self._buffer += chunk
        if not self._started:
            match = self._pattern.search(self._buffer)
            if match is None:
                return ""
            self._started = True
            self._index = match.end()

        output: list[str] = []
        while self._index < len(self._buffer):
            character = self._buffer[self._index]
            if character == '"':
                self._index += 1
                self._complete = True
                break
            if character != "\\":
                output.append(character)
                self._index += 1
                continue

            decoded, consumed = self._decode_escape()
            if consumed == 0:
                break
            output.append(decoded)
            self._index += consumed

        return "".join(output)

    def _decode_escape(self) -> tuple[str, int]:
        if self._index + 1 >= len(self._buffer):
            return "", 0

        escaped = self._buffer[self._index + 1]
        replacements = {
            '"': '"',
            "\\": "\\",
            "/": "/",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }
        if escaped in replacements:
            return replacements[escaped], 2
        if escaped != "u":
            return "", 0
        if self._index + 5 >= len(self._buffer):
            return "", 0

        hex_value = self._buffer[self._index + 2 : self._index + 6]
        if not re.fullmatch(r"[0-9a-fA-F]{4}", hex_value):
            return "", 0
        return chr(int(hex_value, 16)), 6
