# Changelog

## 0.1.0 — 2026-03-16

Initial release.

### Features

- **Encoding label lookup** — case-insensitive WHATWG encoding label-to-name mapping (~200 labels)
- **BOM sniffing** — detect UTF-8, UTF-16BE, and UTF-16LE byte order marks per spec
- **Web-compatible codecs** — `WebDecoder` / `WebEncoder` with three error modes: `replacement` (U+FFFD), `fatal` (raise), `html` (numeric character references)
- **TextDecoder / TextEncoder** — Pythonic equivalents of the web platform API
- **webencodings compatibility shim** — drop-in migration path from the abandoned `webencodings` package
- **Fully typed** — PEP 561 compliant with strict mypy
- **Zero dependencies** — pure Python, supports Python 3.10–3.13
