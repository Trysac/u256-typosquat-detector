# typosquat-detector

[![CI](https://github.com/Trysac/u256-typosquat-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u256-typosquat-detector/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/trysac-typosquat-detector.svg)](https://pypi.org/project/trysac-typosquat-detector/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Flag PyPI and npm package names that imitate popular packages: homoglyphs, separator tricks, affixes and one-edit typos against a bundled, overridable popular list.

Typosquatting packages such as a transposed `requests` or `django` spelled with a zero install malware on developer machines and in CI. Reviewers rarely notice a one-character difference in a dependency file. This library checks candidate names against a list of popular packages with explicit rules and returns which rule matched which target, so CI can stop a suspicious addition before install.

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model.

## Installation

```bash
pip install trysac-typosquat-detector
```

## Usage

### Python API

```python
from typosquat_detector import check

for f in check("reqeusts"):
    print(f"{f.candidate}: {f.rule} -> {f.target}")
# reqeusts: distance -> requests
```

### Command line

```bash
python -m typosquat_detector reqeusts flask
# reqeusts: distance -> requests
```

Exit codes: `0` no findings, `1` findings, `2` usage or invalid input.

## API Reference

- `check(name, *, ecosystem='pypi', popular=None) -> list[Finding]`: validates the candidate and checks it against `popular` (default `POPULAR[ecosystem]`). Returns one `Finding` per matched target, sorted by target. For each target the first matching rule is reported, in order: `homoglyph`, `separator`, `affix`, `distance`. A candidate equal to a target after normalisation is skipped.
- `normalize(name, ecosystem='pypi') -> str`: PyPI uses PEP 503 (lowercase, runs of `-`, `_`, `.` become `-`); npm lowercases only.
- `osa_distance(a, b) -> int`: optimal string alignment distance with insertions, deletions, substitutions and adjacent transpositions, each cost 1.
- `POPULAR: Mapping[str, tuple[str, ...]]`: bundled names for `pypi` and `npm`.
- `Finding`: frozen dataclass with `rule` (`homoglyph`, `separator`, `affix`, `distance`), `target` and `candidate`.
- `TyposquatError`: has `code` (`invalid_name`, `invalid_ecosystem`, `input_too_large`).

Names longer than 214 characters raise `TyposquatError('input_too_large')`. PyPI names must match the PEP 508 name regex case-insensitively; npm names must match the npm name regex after lowercasing. The `distance` rule applies only when both normalised names have at least 4 characters. The CLI accepts `--ecosystem pypi|npm` and `--popular FILE` (one name per line, at most 10,000 names and 1 MiB).

## Why not a broad dependency risk score

A broad dependency risk score answers many questions. This library answers one: is this name imitating a popular package? It is offline, has no runtime dependencies, and reports the rule that fired.

## Contributing

Open an issue or pull request in the repository. Run `pytest` before sending a change.

## License

MIT
