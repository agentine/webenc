"""Tests for webenc.bom — BOM sniffing utilities."""

from webenc.bom import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, detect_bom


class TestDetectBom:
    """Test BOM detection."""

    def test_utf8_bom(self) -> None:
        data = BOM_UTF8 + b"hello"
        result = detect_bom(data)
        assert result is not None
        encoding, remaining = result
        assert encoding == "UTF-8"
        assert remaining == b"hello"

    def test_utf16be_bom(self) -> None:
        data = BOM_UTF16_BE + b"\x00h\x00i"
        result = detect_bom(data)
        assert result is not None
        encoding, remaining = result
        assert encoding == "UTF-16BE"
        assert remaining == b"\x00h\x00i"

    def test_utf16le_bom(self) -> None:
        data = BOM_UTF16_LE + b"h\x00i\x00"
        result = detect_bom(data)
        assert result is not None
        encoding, remaining = result
        assert encoding == "UTF-16LE"
        assert remaining == b"h\x00i\x00"

    def test_no_bom(self) -> None:
        assert detect_bom(b"hello") is None

    def test_empty_data(self) -> None:
        assert detect_bom(b"") is None

    def test_partial_utf8_bom(self) -> None:
        """Only first 2 bytes of UTF-8 BOM — should not match UTF-8."""
        assert detect_bom(b"\xef\xbb") is None

    def test_single_byte(self) -> None:
        assert detect_bom(b"\xef") is None

    def test_utf8_bom_only(self) -> None:
        result = detect_bom(BOM_UTF8)
        assert result is not None
        assert result == ("UTF-8", b"")

    def test_utf16be_bom_only(self) -> None:
        result = detect_bom(BOM_UTF16_BE)
        assert result is not None
        assert result == ("UTF-16BE", b"")

    def test_utf16le_bom_only(self) -> None:
        result = detect_bom(BOM_UTF16_LE)
        assert result is not None
        assert result == ("UTF-16LE", b"")

    def test_utf8_takes_priority(self) -> None:
        """UTF-8 BOM starts with 0xEF which doesn't conflict, but verify order."""
        data = BOM_UTF8 + b"test"
        result = detect_bom(data)
        assert result is not None
        assert result[0] == "UTF-8"

    def test_bom_constants(self) -> None:
        assert BOM_UTF8 == b"\xef\xbb\xbf"
        assert BOM_UTF16_BE == b"\xfe\xff"
        assert BOM_UTF16_LE == b"\xff\xfe"
