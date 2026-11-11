# Security

## Threat model

The detector identifies package names that imitate popular PyPI or npm packages. It is one layer in a defense-in-depth strategy, not a complete security solution. It works offline and does not query registries.

## Defended against

- One-edit typos and adjacent transpositions, when both normalised names have at least 4 characters (`distance`).
- Separator confusion: names equal after removing `-`, `_`, `.` (the helper also strips spaces, which validated names cannot contain).
- ASCII homoglyphs: names equal after mapping `0->o`, `1->l`, `3->e`, `5->s`, `rn->m`, `vv->w`.
- Affix squats of a popular name. PyPI prefixes: `python-`, `py-`, `py`; suffixes: `-python`, `-py`, `py`, `-dev`, `-lib`. npm prefixes: `node-`, `js-`; suffixes: `-js`, `.js`, `js`, `-node`.

For each popular target, only the first matching rule is reported, in the order homoglyph, separator, affix, distance. A candidate equal to a target after normalisation is skipped.

## Not defended against

- Unicode confusables (registry names are ASCII).
- Packages missing from the popular list.
- Dependency confusion between private and public indexes.
- Malicious code in correctly named packages.

## Limits

- The bundled popular list is dated data checked 2026-11-09. It can be overridden with `check(..., popular=...)` or the CLI `--popular` file.
- Names longer than 214 characters raise `TyposquatError` with code `input_too_large`; this is the npm limit and is also applied to PyPI.
- The `distance` rule only runs when both normalised names have at least 4 characters.
- Scoped npm names are compared as a whole string.
- The CLI rejects a popular file larger than 1 MiB or with more than 10,000 non-empty lines.
- No registry lookups, download counts or lock-file parsing are performed.
