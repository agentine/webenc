# webenc

WHATWG Encoding Standard implementation for Python — drop-in replacement for [webencodings](https://github.com/gsnedders/python-webencodings).

- Complete WHATWG encoding label index (~200 labels)
- BOM sniffing (UTF-8, UTF-16BE, UTF-16LE)
- Web-compatible error modes: replacement (U+FFFD), fatal, HTML NCRs
- `TextDecoder` / `TextEncoder` APIs matching the web platform
- `webencodings` compatibility shim for easy migration
- Pure Python, zero dependencies, Python 3.10+
- Fully typed (PEP 561, mypy --strict clean)

## Install

```
pip install webenc
```

## Quick Start

```python
from webenc import TextDecoder, TextEncoder, lookup

# Encoding label lookup
lookup("ascii")        # "windows-1252" (per WHATWG spec)
lookup("utf-8")        # "UTF-8"
lookup("bogus")        # None

# Decode bytes
decoder = TextDecoder("utf-8")
decoder.decode(b"\xc3\xa9")  # "é"

# Decode with BOM stripping (default)
decoder.decode(b"\xef\xbb\xbfhello")  # "hello"

# Fatal mode
decoder = TextDecoder("utf-8", fatal=True)
# decoder.decode(b"\xff") → raises DecodeError

# Encode to UTF-8
encoder = TextEncoder()
encoder.encode("hello")  # b"hello"
```

## Migrating from webencodings

`webenc` provides a compatibility shim that mirrors the `webencodings` API:

```python
# Before
import webencodings

# After — use the compat shim
from webenc import compat as webencodings
```

The shim provides the same functions:

```python
from webenc import compat as webencodings

# Lookup returns an Encoding object
enc = webencodings.lookup("utf-8")
enc.name        # "UTF-8"
enc.codec_name  # "utf-8"

# Decode with BOM sniffing
output, encoding = webencodings.decode(b"\xef\xbb\xbfhello")
# output="hello", encoding="UTF-8"

# Encode
output, encoding = webencodings.encode("hello", encoding="utf-8")
# output=b"hello", encoding="UTF-8"

# Incremental decode/encode
for text, enc in webencodings.iter_decode([b"he", b"llo"]):
    print(text)

for data, enc in webencodings.iter_encode(["he", "llo"]):
    print(data)
```

## License

MIT
