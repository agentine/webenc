# webenc — WHATWG Encoding Standard for Python

**Replaces:** `webencodings` (92M monthly downloads, abandoned since 2017)
**Package name:** `webenc` (verified available on PyPI)
**Language:** Python 3.10+
**License:** MIT
**Zero dependencies**

## Problem

`webencodings` implements the WHATWG Encoding Standard but has not had a commit in 8+ years or a release in 9 years. The WHATWG spec was last updated December 2025. The package has 6 unreviewed PRs, 7 unanswered issues, and still lists Python 2.6/2.7 in its metadata. It is a transitive dependency of html5lib, tinycss2, bleach, and indirectly pip — affecting ~92M monthly downloads.

No maintained alternative exists.

## Scope

Implement the WHATWG Encoding Standard (https://encoding.spec.whatwg.org/) for Python:

1. **Encoding label lookup** — case-insensitive label-to-encoding mapping per the spec's encoding index
2. **BOM sniffing** — detect UTF-8/UTF-16BE/UTF-16LE byte order marks
3. **Codec wrappers** — `IncrementalDecoder`/`IncrementalEncoder` with web-compatible error handling
4. **TextDecoder/TextEncoder API** — Pythonic equivalents of the web platform API
5. **Encoding index** — complete label-to-name mapping table from the current WHATWG spec (Dec 2025)

## Architecture

```
webenc/
├── __init__.py          # Public API: lookup(), TextDecoder, TextEncoder
├── labels.py            # WHATWG encoding label → name mapping table
├── codecs.py            # IncrementalDecoder/Encoder with web error modes
├── bom.py               # BOM sniffing utilities
├── py.typed             # PEP 561 marker
└── _version.py          # Version string
```

### Key Design Decisions

- **Pure Python, zero dependencies** — no C extensions, no system library requirements
- **Spec-compliant** — encoding labels and mappings from the current WHATWG spec, not the 2017 snapshot
- **Type-annotated** — full type annotations, PEP 561 compliant
- **Drop-in compatible** — provide a `webencodings` compatibility shim for easy migration
- **Three error modes** — `replacement` (U+FFFD), `fatal` (raise), `html` (numeric character references)

## Deliverables

1. Core library with full WHATWG encoding label support
2. BOM sniffing per spec
3. Web-compatible error handling (replacement, fatal, html modes)
4. Compatibility API matching `webencodings` for migration
5. Comprehensive test suite (label lookup, BOM detection, error modes, round-trip encoding)
6. pyproject.toml with modern Python packaging
7. README with migration guide from `webencodings`

## Non-Goals

- Implementing actual codec algorithms (defer to Python's `codecs` stdlib module)
- Supporting Python < 3.10
- GUI or CLI tools
