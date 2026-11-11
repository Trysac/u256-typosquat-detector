# Architecture

## Overview

The typosquat detector examines candidate package names against a list of
popular names using four ordered rules: `homoglyph`, `separator`, `affix`,
`distance`. For each popular target, the first matching rule is reported.

## Components

- `check`: core function orchestrating validation and rule application.
- `normalize`: ecosystem-specific normalisation (PEP 503 for PyPI, lowercase for npm).
- `osa_distance`: optimal string alignment distance with adjacent transpositions.
- `POPULAR`: bundled mapping of ecosystem to a tuple of popular names.
- `TyposquatError`: typed error with machine-readable `code`.
- CLI (`__main__`): uses `argparse`, supports custom popular list file.

## Rules

1. **homoglyph**: map both names (`0->o`, `1->l`, `3->e`, `5->s`, `rn->m`, `vv->w`) and compare equality.
2. **separator**: remove `-`, `_`, `.` and compare.
3. **affix**: check known prefix/suffix combinations that still yield the target.
4. **distance**: `osa_distance == 1` and both names have length >= 4.

## Popular list

The bundled list is dated (checked 2026-11-09). It is overridable via the
`popular` parameter or CLI `--popular` file. See source for sources.

## Error handling

All validation failures raise `TyposquatError` with a stable code.
Length limit is 214 characters (npm limit, also applied to PyPI).
