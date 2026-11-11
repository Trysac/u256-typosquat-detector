# typosquat-detector

[![PyPI version](https://img.shields.io/pypi/v/trysac-typosquat-detector)](https://pypi.org/project/trysac-typosquat-detector/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-typosquat-detector)](LICENSE)
[![CI](https://github.com/Trysac/u256-typosquat-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u256-typosquat-detector/actions/workflows/ci.yml)

Flag PyPI and npm package names that imitate popular packages: homoglyphs, separator tricks, affixes and one-edit typos against a bundled, overridable popular list

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-typosquat-detector
# or
uv add trysac-typosquat-detector
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import typosquat_detector

# normalize() trims surrounding whitespace and lower-cases the text.
print(typosquat_detector.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    typosquat_detector.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
