"""Tests for webenc.codecs — web error mode decoders and encoders."""

import pytest

from webenc.codecs import DecodeError, EncodeError, WebDecoder, WebEncoder


class TestWebDecoder:
    """Test WebDecoder with replacement and fatal modes."""

    def test_utf8_decode(self) -> None:
        dec = WebDecoder("utf-8")
        assert dec.decode(b"hello", final=True) == "hello"

    def test_utf8_decode_multibyte(self) -> None:
        dec = WebDecoder("utf-8")
        assert dec.decode("\u00e9".encode("utf-8"), final=True) == "\u00e9"

    def test_encoding_property(self) -> None:
        dec = WebDecoder("ascii")
        assert dec.encoding == "windows-1252"

    def test_replacement_mode_default(self) -> None:
        dec = WebDecoder("utf-8")
        result = dec.decode(b"\xff\xfe", final=True)
        assert "\ufffd" in result

    def test_replacement_mode_explicit(self) -> None:
        dec = WebDecoder("utf-8", errors="replacement")
        result = dec.decode(b"\x80\x81", final=True)
        assert "\ufffd" in result

    def test_fatal_mode_raises(self) -> None:
        dec = WebDecoder("utf-8", errors="fatal")
        with pytest.raises(DecodeError):
            dec.decode(b"\xff\xfe", final=True)

    def test_fatal_mode_valid(self) -> None:
        dec = WebDecoder("utf-8", errors="fatal")
        assert dec.decode(b"hello", final=True) == "hello"

    def test_invalid_error_mode(self) -> None:
        with pytest.raises(ValueError, match="Invalid error mode"):
            WebDecoder("utf-8", errors="ignore")

    def test_unknown_encoding(self) -> None:
        with pytest.raises(LookupError, match="Unknown encoding"):
            WebDecoder("not-real")

    def test_replacement_encoding_rejected(self) -> None:
        with pytest.raises(LookupError, match="replacement encoding"):
            WebDecoder("hz-gb-2312")

    def test_incremental_decode(self) -> None:
        dec = WebDecoder("utf-8")
        # Multi-byte char split across chunks: \xc3\xa9 = é
        part1 = dec.decode(b"\xc3", final=False)
        part2 = dec.decode(b"\xa9", final=True)
        assert part1 + part2 == "\u00e9"

    def test_reset(self) -> None:
        dec = WebDecoder("utf-8")
        dec.decode(b"\xc3", final=False)
        dec.reset()
        assert dec.decode(b"a", final=True) == "a"

    def test_shift_jis_decode(self) -> None:
        dec = WebDecoder("shift_jis")
        assert dec.encoding == "Shift_JIS"
        result = dec.decode("\u3053\u3093\u306b\u3061\u306f".encode("shift_jis"), final=True)
        assert result == "\u3053\u3093\u306b\u3061\u306f"

    def test_gbk_decode(self) -> None:
        dec = WebDecoder("gbk")
        result = dec.decode("\u4f60\u597d".encode("gbk"), final=True)
        assert result == "\u4f60\u597d"

    def test_case_insensitive_encoding(self) -> None:
        dec = WebDecoder("UTF-8")
        assert dec.encoding == "UTF-8"


class TestWebEncoder:
    """Test WebEncoder with html and fatal modes."""

    def test_utf8_encode(self) -> None:
        enc = WebEncoder("utf-8")
        assert enc.encode("hello", final=True) == b"hello"

    def test_encoding_property(self) -> None:
        enc = WebEncoder("utf-8")
        assert enc.encoding == "UTF-8"

    def test_html_mode_default(self) -> None:
        enc = WebEncoder("ascii")
        result = enc.encode("\u00e9", final=True)
        # windows-1252 can encode é directly as 0xe9
        assert result == b"\xe9"

    def test_html_mode_ncr(self) -> None:
        enc = WebEncoder("ascii")
        # windows-1252 can't encode CJK
        result = enc.encode("\u4f60", final=True)
        assert b"&#" in result

    def test_fatal_mode_raises(self) -> None:
        enc = WebEncoder("shift_jis", errors="fatal")
        with pytest.raises(EncodeError):
            enc.encode("\U0001f600", final=True)  # Emoji not in Shift_JIS

    def test_fatal_mode_valid(self) -> None:
        enc = WebEncoder("utf-8", errors="fatal")
        assert enc.encode("hello", final=True) == b"hello"

    def test_invalid_error_mode(self) -> None:
        with pytest.raises(ValueError, match="Invalid error mode"):
            WebEncoder("utf-8", errors="ignore")

    def test_unknown_encoding(self) -> None:
        with pytest.raises(LookupError, match="Unknown encoding"):
            WebEncoder("not-real")

    def test_utf8_encode_multibyte(self) -> None:
        enc = WebEncoder("utf-8")
        assert enc.encode("\u00e9", final=True) == b"\xc3\xa9"

    def test_reset(self) -> None:
        enc = WebEncoder("utf-8")
        enc.encode("test", final=False)
        enc.reset()
        assert enc.encode("a", final=True) == b"a"
