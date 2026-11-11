# Project record

## Objective

Flag PyPI and npm package names that imitate popular packages: homoglyphs, separator tricks, affixes and one-edit typos against a bundled, overridable popular list.

## Scope

In scope: the Python package `typosquat_detector` (import name) distributed as `trysac-typosquat-detector`, with no runtime dependencies beyond the standard library. It provides `check`, `normalize`, `osa_distance`, `POPULAR`, `Finding` and `TyposquatError`, covering PyPI and npm names and the rules homoglyph, separator, affix and distance. The bundled popular list is dated data and can be overridden through `check(..., popular=...)` or the CLI `--popular` file. The CLI is `python -m typosquat_detector`.

Out of scope: registry lookups, download counts, parsing lock files. Also out of scope: Unicode confusables (registry names are ASCII), packages missing from the popular list, dependency confusion between private and public indexes, and malicious code in correctly named packages.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays 'pending measurement'.

| Metric | Value |
|---|---|
| Tokens (input / output) | 702232 / 61173 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.0876 |

## Factory run u256 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | generation | deepseek-v4-pro | yes | 3947 | 17415 | 0 | 1280 | 0.0371 |
| 2026-11-11 | fix-1 | deepseek-flash | no | 8039 | 860 | 0 | 43136 | 0.0019 |
| 2026-11-11 | audit | deepseek-flash | no | 18616 | 26790 | 0 | 381824 | 0.0200 |
| 2026-11-11 | fix-2 | deepseek-flash | no | 8572 | 6884 | 0 | 121088 | 0.0058 |
| 2026-11-11 | docs | deepseek-flash | no | 115474 | 9224 | 0 | 256 | 0.0229 |

Total: $0.0876. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
