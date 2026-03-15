"""Compatibility shim for ``webencodings``.

Provides the same top-level API as the original ``webencodings`` package so
that libraries migrating from ``webencodings`` can switch to ``webenc`` with
minimal changes::

    # Before
    import webencodings
    encoding = webencodings.lookup("utf-8")

    # After
    from webenc import compat as webencodings
    encoding = webencodings.lookup("utf-8")
"""

from __future__ import annotations

from typing import Generator

from webenc.codecs import WebDecoder, WebEncoder, _resolve_encoding
from webenc.labels import lookup as _label_lookup

# Re-export ASCII whitespace chars used in the WHATWG spec.
ASCII_WHITESPACE = "\t\n\x0c\r "


class Encoding:
    """Represents a WHATWG encoding — compatible with ``webencodings.Encoding``.

    Attributes
    ----------
    name : str
        The canonical encoding name.
    codec_name : str
        The name usable with Python's ``codecs`` module.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def codec_name(self) -> str:
        """Python codec name for this encoding."""
        from webenc.codecs import _python_codec

        return _python_codec(self.name)

    def __repr__(self) -> str:
        return f"<Encoding {self.name}>"


def lookup(label: str) -> Encoding | None:
    """Look up an encoding by label.

    Returns an :class:`Encoding` object, or ``None`` if the label is
    unknown.  Compatible with ``webencodings.lookup()``.
    """
    name = _label_lookup(label)
    if name is None:
        return None
    return Encoding(name)


def decode(
    input: bytes,  # noqa: A002
    fallback_encoding: str = "utf-8",
    errors: str = "replace",
) -> tuple[str, str]:
    """Decode *input* bytes and return ``(output, encoding_name)``.

    BOM sniffing is performed first.  If no BOM is found,
    *fallback_encoding* is used.  Compatible with
    ``webencodings.decode()``.
    """
    from webenc.bom import detect_bom

    bom_result = detect_bom(input)
    if bom_result is not None:
        encoding_name, data = bom_result
    else:
        encoding_name = _resolve_encoding(fallback_encoding)
        data = input

    py_errors = "replace" if errors == "replace" else "strict"
    dec = WebDecoder(encoding_name, errors="replacement" if py_errors == "replace" else "fatal")
    output = dec.decode(data, final=True)
    return output, encoding_name


def encode(
    input: str,  # noqa: A002
    encoding: str = "utf-8",
    errors: str = "strict",
) -> tuple[bytes, str]:
    """Encode *input* text and return ``(output, encoding_name)``.

    Compatible with ``webencodings.encode()``.
    """
    encoding_name = _resolve_encoding(encoding)
    enc_errors = "fatal" if errors == "strict" else "html"
    enc = WebEncoder(encoding_name, errors=enc_errors)
    output = enc.encode(input, final=True)
    return output, encoding_name


def iter_decode(
    input: list[bytes],  # noqa: A002
    fallback_encoding: str = "utf-8",
    errors: str = "replace",
) -> Generator[tuple[str, str], None, None]:
    """Incrementally decode chunks.  Yields ``(output, encoding_name)``.

    Compatible with ``webencodings.iter_decode()``.
    """
    from webenc.bom import detect_bom

    encoding_name: str | None = None
    dec: WebDecoder | None = None

    for i, chunk in enumerate(input):
        if encoding_name is None:
            bom_result = detect_bom(chunk)
            if bom_result is not None:
                encoding_name, chunk = bom_result
            else:
                encoding_name = _resolve_encoding(fallback_encoding)

            py_errors = "replacement" if errors == "replace" else "fatal"
            dec = WebDecoder(encoding_name, errors=py_errors)

        assert dec is not None
        final = i == len(input) - 1
        output = dec.decode(chunk, final=final)
        yield output, encoding_name


def iter_encode(
    input: list[str],  # noqa: A002
    encoding: str = "utf-8",
    errors: str = "strict",
) -> Generator[tuple[bytes, str], None, None]:
    """Incrementally encode chunks.  Yields ``(output, encoding_name)``.

    Compatible with ``webencodings.iter_encode()``.
    """
    encoding_name = _resolve_encoding(encoding)
    enc_errors = "fatal" if errors == "strict" else "html"
    enc = WebEncoder(encoding_name, errors=enc_errors)

    for i, chunk in enumerate(input):
        final = i == len(input) - 1
        output = enc.encode(chunk, final=final)
        yield output, encoding_name
