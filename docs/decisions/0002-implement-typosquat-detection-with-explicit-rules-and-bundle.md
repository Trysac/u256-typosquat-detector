# Implement typosquat detection with explicit rules and bundled popular list

Status: accepted (generated, pending human review)

## Context

Need to flag package names that imitate popular PyPI/npm packages to prevent supply chain attacks.

## Decision

Implement a pure Python library with four ordered rules (homoglyph, separator, affix, distance) against a bundled, overridable popular list, plus a CLI. No runtime dependencies.

## Consequences

The detector is offline, deterministic, and easily integrated into CI. The popular list must be maintained periodically. It does not cover Unicode confusables or registry queries.
