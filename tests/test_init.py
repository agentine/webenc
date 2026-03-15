"""Tests for webenc public API — TextDecoder, TextEncoder, lookup."""

import pytest

import webenc
from webenc import TextDecoder, TextEncoder, lookup


class TestLookup:
    """Test top-level lookup re-export."""

    def test_utf8(self) -> None:
        assert lookup("utf-8") == "UTF-8"

    def test_unknown(self) -> None:
        assert lookup("bogus") is None


class TestTextDecoder:
    """Test the web-platform-style TextDecoder."""

    def test_default_encoding(self) -> None:
        td = TextDecoder()
        assert td.encoding == "utf-8"

    def test_decode_utf8(self) -> None:
        td = TextDecoder("utf-8")
        assert td.decode(b"hello") == "hello"

    def test_decode_multibyte(self) -> None:
        td = TextDecoder("utf-8")
        assert td.decode("\u00e9".encode("utf-8")) == "\u00e9"

    def test_fatal_property(self) -> None:
        td = TextDecoder(fatal=True)
        assert td.fatal is True

    def test_non_fatal_default(self) -> None:
        td = TextDecoder()
        assert td.fatal is False

    def test_fatal_raises(self) -> None:
        td = TextDecoder("utf-8", fatal=True)
        with pytest.raises(webenc.DecodeError):
            td.decode(b"\xff\xfe")

    def test_replacement_default(self) -> None:
        td = TextDecoder("utf-8")
        result = td.decode(b"\xff\xfe")
        assert "\ufffd" in result

    def test_bom_stripped_by_default(self) -> None:
        td = TextDecoder("utf-8")
        data = b"\xef\xbb\xbfhello"
        assert td.decode(data) == "hello"

    def test_ignore_bom(self) -> None:
        td = TextDecoder("utf-8", ignore_bom=True)
        data = b"\xef\xbb\xbfhello"
        assert td.decode(data) == "\ufeffhello"

    def test_ignore_bom_property(self) -> None:
        td = TextDecoder("utf-8", ignore_bom=True)
        assert td.ignore_bom is True

    def test_streaming(self) -> None:
        td = TextDecoder("utf-8")
        # \xc3\xa9 = é split across two chunks
        part1 = td.decode(b"\xc3", stream=True)
        part2 = td.decode(b"\xa9")
        assert part1 + part2 == "\u00e9"

    def test_encoding_label_resolved(self) -> None:
        td = TextDecoder("ascii")
        assert td.encoding == "windows-1252"

    def test_round_trip_utf8(self) -> None:
        text = "Hello, \u4e16\u754c! \U0001f600"
        encoded = TextEncoder().encode(text)
        decoded = TextDecoder("utf-8").decode(encoded)
        assert decoded == text


class TestTextEncoder:
    """Test the web-platform-style TextEncoder."""

    def test_encoding_always_utf8(self) -> None:
        te = TextEncoder()
        assert te.encoding == "utf-8"

    def test_encode_ascii(self) -> None:
        te = TextEncoder()
        assert te.encode("hello") == b"hello"

    def test_encode_multibyte(self) -> None:
        te = TextEncoder()
        assert te.encode("\u00e9") == b"\xc3\xa9"

    def test_encode_empty(self) -> None:
        te = TextEncoder()
        assert te.encode("") == b""

    def test_encode_default_empty(self) -> None:
        te = TextEncoder()
        assert te.encode() == b""

    def test_encode_emoji(self) -> None:
        te = TextEncoder()
        result = te.encode("\U0001f600")
        assert result == "\U0001f600".encode("utf-8")


class TestModuleExports:
    """Verify __all__ exports are accessible."""

    def test_version(self) -> None:
        assert hasattr(webenc, "__version__")
        assert isinstance(webenc.__version__, str)

    def test_all_exports(self) -> None:
        for name in webenc.__all__:
            assert hasattr(webenc, name), f"Missing export: {name}"
