"""BOM (Byte Order Mark) sniffing per the WHATWG Encoding Standard."""

from __future__ import annotations

# BOM byte sequences.
BOM_UTF8 = b"\xef\xbb\xbf"
BOM_UTF16_BE = b"\xfe\xff"
BOM_UTF16_LE = b"\xff\xfe"


def detect_bom(data: bytes) -> tuple[str, bytes] | None:
    """Detect a BOM at the start of *data*.

    Returns a ``(encoding, remaining_bytes)`` tuple if a BOM is found,
    where *encoding* is the canonical WHATWG encoding name and
    *remaining_bytes* is *data* with the BOM stripped.

    Returns ``None`` if no BOM is detected.

    The check order follows the WHATWG spec: UTF-8, then UTF-16BE, then
    UTF-16LE.
    """
    if data[:3] == BOM_UTF8:
        return ("UTF-8", data[3:])
    if data[:2] == BOM_UTF16_BE:
        return ("UTF-16BE", data[2:])
    if data[:2] == BOM_UTF16_LE:
        return ("UTF-16LE", data[2:])
    return None
