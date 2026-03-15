"""Tests for webenc.labels — WHATWG encoding label lookup."""

import pytest

from webenc.labels import lookup


class TestLookup:
    """Test label-to-encoding lookup."""

    @pytest.mark.parametrize(
        "label, expected",
        [
            ("utf-8", "UTF-8"),
            ("UTF-8", "UTF-8"),
            ("utf8", "UTF-8"),
            ("unicode-1-1-utf-8", "UTF-8"),
            ("ascii", "windows-1252"),
            ("us-ascii", "windows-1252"),
            ("iso-8859-1", "windows-1252"),
            ("latin1", "windows-1252"),
            ("windows-1252", "windows-1252"),
            ("gbk", "GBK"),
            ("gb2312", "GBK"),
            ("big5", "Big5"),
            ("euc-jp", "EUC-JP"),
            ("shift_jis", "Shift_JIS"),
            ("euc-kr", "EUC-KR"),
            ("iso-2022-jp", "ISO-2022-JP"),
            ("koi8-r", "KOI8-R"),
            ("macintosh", "macintosh"),
            ("x-user-defined", "x-user-defined"),
            ("gb18030", "gb18030"),
        ],
    )
    def test_known_labels(self, label: str, expected: str) -> None:
        assert lookup(label) == expected

    @pytest.mark.parametrize(
        "label, expected",
        [
            ("UTF-8", "UTF-8"),
            ("Utf-8", "UTF-8"),
            ("ASCII", "windows-1252"),
            ("Ascii", "windows-1252"),
            ("GBK", "GBK"),
            ("Gbk", "GBK"),
            ("SHIFT_JIS", "Shift_JIS"),
            ("EUC-KR", "EUC-KR"),
        ],
    )
    def test_case_insensitive(self, label: str, expected: str) -> None:
        assert lookup(label) == expected

    @pytest.mark.parametrize(
        "label",
        [
            "  utf-8  ",
            "\tutf-8\t",
            "\nutf-8\n",
            "\r\nutf-8\r\n",
            "\x0cutf-8\x0c",
        ],
    )
    def test_whitespace_stripping(self, label: str) -> None:
        assert lookup(label) == "UTF-8"

    @pytest.mark.parametrize(
        "label",
        [
            "not-an-encoding",
            "",
            "utf-7",
            "utf-32",
            "ebcdic",
        ],
    )
    def test_unknown_returns_none(self, label: str) -> None:
        assert lookup(label) is None

    def test_replacement_encodings(self) -> None:
        """Labels that map to the replacement encoding per WHATWG."""
        for label in ["csiso2022kr", "hz-gb-2312", "iso-2022-cn",
                       "iso-2022-cn-ext", "iso-2022-kr"]:
            assert lookup(label) == "replacement"

    def test_utf16_labels(self) -> None:
        assert lookup("utf-16le") == "UTF-16LE"
        assert lookup("utf-16be") == "UTF-16BE"
        assert lookup("utf-16") == "UTF-16LE"
        assert lookup("unicode") == "UTF-16LE"
