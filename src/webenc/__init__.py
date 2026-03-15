"""webenc — WHATWG Encoding Standard for Python.

Drop-in replacement for ``webencodings``.  Implements the WHATWG Encoding
Standard: label lookup, BOM sniffing, web-compatible error handling, and
``TextDecoder`` / ``TextEncoder`` APIs.
"""

from __future__ import annotations

from webenc._version import __version__
from webenc.bom import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, detect_bom
from webenc.codecs import (
    DecodeError,
    EncodeError,
    WebDecoder,
    WebEncoder,
)
from webenc.labels import lookup

__all__ = [
    "__version__",
    "BOM_UTF8",
    "BOM_UTF16_BE",
    "BOM_UTF16_LE",
    "DecodeError",
    "EncodeError",
    "TextDecoder",
    "TextEncoder",
    "WebDecoder",
    "WebEncoder",
    "detect_bom",
    "lookup",
]


class TextDecoder:
    """Web-platform-style ``TextDecoder``.

    Parameters
    ----------
    encoding:
        Any WHATWG encoding label.  Defaults to ``"utf-8"``.
    fatal:
        If ``True``, raise :class:`DecodeError` on invalid input.
        If ``False`` (default), replace invalid bytes with U+FFFD.
    ignore_bom:
        If ``True``, do **not** strip a leading BOM.
        If ``False`` (default), strip a leading BOM when present.
    """

    def __init__(
        self,
        encoding: str = "utf-8",
        *,
        fatal: bool = False,
        ignore_bom: bool = False,
    ) -> None:
        errors = "fatal" if fatal else "replacement"
        self._decoder = WebDecoder(encoding, errors=errors)
        self._fatal = fatal
        self._ignore_bom = ignore_bom
        self._bom_seen = False

    @property
    def encoding(self) -> str:
        """The canonical WHATWG encoding name (lowercase)."""
        return self._decoder.encoding.lower()

    @property
    def fatal(self) -> bool:
        """Whether the decoder raises on invalid input."""
        return self._fatal

    @property
    def ignore_bom(self) -> bool:
        """Whether to keep a leading BOM in the output."""
        return self._ignore_bom

    def decode(self, data: bytes = b"", *, stream: bool = False) -> str:
        """Decode *data* and return the resulting string.

        Parameters
        ----------
        data:
            Bytes to decode.
        stream:
            If ``True``, the decoder expects more chunks.  If ``False``
            (default), this is the final (or only) chunk and the decoder
            is reset afterward.
        """
        result = self._decoder.decode(data, final=not stream)

        # Strip BOM on first non-empty decode unless ignore_bom is set.
        if not self._ignore_bom and not self._bom_seen and result:
            self._bom_seen = True
            if result[0] == "\ufeff":
                result = result[1:]

        if not stream:
            self._decoder.reset()
            self._bom_seen = False

        return result


class TextEncoder:
    """Web-platform-style ``TextEncoder``.

    Always encodes to UTF-8 per the WHATWG specification.
    """

    def __init__(self) -> None:
        self._encoder = WebEncoder("utf-8", errors="fatal")

    @property
    def encoding(self) -> str:
        """Always ``"utf-8"``."""
        return "utf-8"

    def encode(self, text: str = "") -> bytes:
        """Encode *text* to UTF-8 bytes."""
        return self._encoder.encode(text, final=True)
