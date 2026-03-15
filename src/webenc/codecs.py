"""Incremental decoder/encoder with web-compatible error handling.

Wraps Python's stdlib ``codecs`` module, adding WHATWG-specified error modes:

- **replacement** — replace undecodable bytes with U+FFFD (default for decoding)
- **fatal** — raise :class:`DecodeError` / :class:`EncodeError`
- **html** — replace unencodable characters with HTML numeric character
  references ``&#xHHHH;`` (for encoding)
"""

from __future__ import annotations

import codecs

from webenc.labels import lookup

# Maps WHATWG canonical names to Python codec names where they differ.
_WHATWG_TO_PYTHON: dict[str, str] = {
    "IBM866": "cp866",
    "ISO-8859-2": "iso8859-2",
    "ISO-8859-3": "iso8859-3",
    "ISO-8859-4": "iso8859-4",
    "ISO-8859-5": "iso8859-5",
    "ISO-8859-6": "iso8859-6",
    "ISO-8859-7": "iso8859-7",
    "ISO-8859-8": "iso8859-8",
    "ISO-8859-8-I": "iso8859-8",
    "ISO-8859-10": "iso8859-10",
    "ISO-8859-13": "iso8859-13",
    "ISO-8859-14": "iso8859-14",
    "ISO-8859-15": "iso8859-15",
    "ISO-8859-16": "iso8859-16",
    "KOI8-R": "koi8-r",
    "KOI8-U": "koi8-u",
    "macintosh": "mac-roman",
    "windows-874": "cp874",
    "windows-1250": "cp1250",
    "windows-1251": "cp1251",
    "windows-1252": "cp1252",
    "windows-1253": "cp1253",
    "windows-1254": "cp1254",
    "windows-1255": "cp1255",
    "windows-1256": "cp1256",
    "windows-1257": "cp1257",
    "windows-1258": "cp1258",
    "x-mac-cyrillic": "mac-cyrillic",
    "GBK": "gbk",
    "gb18030": "gb18030",
    "Big5": "big5hkscs",
    "EUC-JP": "euc-jp",
    "ISO-2022-JP": "iso2022-jp",
    "Shift_JIS": "shift_jis",
    "EUC-KR": "euc-kr",
    "UTF-8": "utf-8",
    "UTF-16BE": "utf-16-be",
    "UTF-16LE": "utf-16-le",
    "x-user-defined": "latin-1",
}


class DecodeError(ValueError):
    """Raised when decoding fails in ``fatal`` mode."""


class EncodeError(ValueError):
    """Raised when encoding fails in ``fatal`` mode."""


def _python_codec(encoding: str) -> str:
    """Convert a WHATWG encoding name to a Python codec name."""
    return _WHATWG_TO_PYTHON.get(encoding, encoding)


def _resolve_encoding(encoding: str) -> str:
    """Resolve an encoding label to a canonical WHATWG name.

    Raises ``LookupError`` if the label is unknown.
    """
    name = lookup(encoding)
    if name is None:
        raise LookupError(f"Unknown encoding label: {encoding!r}")
    if name == "replacement":
        raise LookupError(
            f"The encoding label {encoding!r} maps to the replacement "
            f"encoding, which is not usable for decoding/encoding"
        )
    return name


class WebDecoder:
    """Incremental decoder with web-compatible error handling.

    Parameters
    ----------
    encoding:
        Any WHATWG encoding label (e.g. ``"utf-8"``, ``"ascii"``,
        ``"shift_jis"``).
    errors:
        Error mode — ``"replacement"`` (default, replaces bad bytes with
        U+FFFD), or ``"fatal"`` (raises :class:`DecodeError`).
    """

    def __init__(self, encoding: str, errors: str = "replacement") -> None:
        self._encoding = _resolve_encoding(encoding)
        if errors not in ("replacement", "fatal"):
            raise ValueError(
                f"Invalid error mode {errors!r}; use 'replacement' or 'fatal'"
            )
        self._errors = errors
        codec_name = _python_codec(self._encoding)
        py_errors = "replace" if errors == "replacement" else "strict"
        self._decoder = codecs.getincrementaldecoder(codec_name)(py_errors)

    @property
    def encoding(self) -> str:
        """The canonical WHATWG encoding name."""
        return self._encoding

    def decode(self, data: bytes, final: bool = False) -> str:
        """Decode a chunk of bytes.

        Parameters
        ----------
        data:
            The bytes to decode.
        final:
            Set to ``True`` for the last chunk to flush any buffered state.

        Returns
        -------
        The decoded string.

        Raises
        ------
        DecodeError
            If *errors* is ``"fatal"`` and invalid bytes are encountered.
        """
        try:
            return self._decoder.decode(data, final)
        except UnicodeDecodeError as exc:
            raise DecodeError(str(exc)) from exc

    def reset(self) -> None:
        """Reset the decoder state."""
        self._decoder.reset()


class WebEncoder:
    """Incremental encoder with web-compatible error handling.

    Parameters
    ----------
    encoding:
        Any WHATWG encoding label (e.g. ``"utf-8"``, ``"ascii"``).
    errors:
        Error mode — ``"html"`` (default, replaces unencodable characters
        with ``&#xHHHH;`` numeric character references), or ``"fatal"``
        (raises :class:`EncodeError`).
    """

    def __init__(self, encoding: str, errors: str = "html") -> None:
        self._encoding = _resolve_encoding(encoding)
        if errors not in ("html", "fatal"):
            raise ValueError(
                f"Invalid error mode {errors!r}; use 'html' or 'fatal'"
            )
        self._errors = errors
        codec_name = _python_codec(self._encoding)
        py_errors = "xmlcharrefreplace" if errors == "html" else "strict"
        self._encoder = codecs.getincrementalencoder(codec_name)(py_errors)

    @property
    def encoding(self) -> str:
        """The canonical WHATWG encoding name."""
        return self._encoding

    def encode(self, text: str, final: bool = False) -> bytes:
        """Encode a chunk of text.

        Parameters
        ----------
        text:
            The string to encode.
        final:
            Set to ``True`` for the last chunk to flush any buffered state.

        Returns
        -------
        The encoded bytes.

        Raises
        ------
        EncodeError
            If *errors* is ``"fatal"`` and unencodable characters are found.
        """
        try:
            return self._encoder.encode(text, final)
        except UnicodeEncodeError as exc:
            raise EncodeError(str(exc)) from exc

    def reset(self) -> None:
        """Reset the encoder state."""
        self._encoder.reset()
