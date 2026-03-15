"""Tests for webenc.compat — webencodings compatibility shim."""

from webenc.compat import (
    ASCII_WHITESPACE,
    Encoding,
    decode,
    encode,
    iter_decode,
    iter_encode,
    lookup,
)


class TestLookup:
    """Test compat lookup returns Encoding objects."""

    def test_returns_encoding(self) -> None:
        enc = lookup("utf-8")
        assert enc is not None
        assert isinstance(enc, Encoding)
        assert enc.name == "UTF-8"

    def test_returns_none_for_unknown(self) -> None:
        assert lookup("bogus") is None

    def test_encoding_repr(self) -> None:
        enc = lookup("utf-8")
        assert enc is not None
        assert repr(enc) == "<Encoding UTF-8>"

    def test_codec_name(self) -> None:
        enc = lookup("ascii")
        assert enc is not None
        assert enc.codec_name == "cp1252"


class TestDecode:
    """Test compat decode function."""

    def test_utf8_decode(self) -> None:
        output, enc = decode(b"hello")
        assert output == "hello"
        assert enc == "UTF-8"

    def test_bom_detection(self) -> None:
        data = b"\xef\xbb\xbfhello"
        output, enc = decode(data, fallback_encoding="ascii")
        assert output == "hello"
        assert enc == "UTF-8"

    def test_fallback_encoding(self) -> None:
        data = b"\xe9"  # é in windows-1252
        output, enc = decode(data, fallback_encoding="windows-1252")
        assert output == "\u00e9"
        assert enc == "windows-1252"

    def test_utf16le_bom(self) -> None:
        data = b"\xff\xfeh\x00i\x00"
        output, enc = decode(data)
        assert enc == "UTF-16LE"
        assert output == "hi"


class TestEncode:
    """Test compat encode function."""

    def test_utf8_encode(self) -> None:
        output, enc = encode("hello")
        assert output == b"hello"
        assert enc == "UTF-8"

    def test_specified_encoding(self) -> None:
        output, enc = encode("hello", encoding="utf-8")
        assert output == b"hello"
        assert enc == "UTF-8"


class TestIterDecode:
    """Test compat iter_decode function."""

    def test_basic(self) -> None:
        chunks = [b"hel", b"lo"]
        results = list(iter_decode(chunks))
        assert len(results) == 2
        text = "".join(r[0] for r in results)
        assert text == "hello"
        assert all(r[1] == "UTF-8" for r in results)

    def test_bom_in_first_chunk(self) -> None:
        chunks = [b"\xef\xbb\xbfhi", b" there"]
        results = list(iter_decode(chunks))
        text = "".join(r[0] for r in results)
        assert text == "hi there"


class TestIterEncode:
    """Test compat iter_encode function."""

    def test_basic(self) -> None:
        chunks = ["hel", "lo"]
        results = list(iter_encode(chunks))
        assert len(results) == 2
        data = b"".join(r[0] for r in results)
        assert data == b"hello"
        assert all(r[1] == "UTF-8" for r in results)


class TestAsciiWhitespace:
    """Test ASCII_WHITESPACE constant."""

    def test_value(self) -> None:
        assert ASCII_WHITESPACE == "\t\n\x0c\r "
