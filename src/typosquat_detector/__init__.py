"""Typosquat detector for PyPI and npm package names.

This module identifies package names that imitate popular packages using
homoglyphs, separator tricks, affixes, or one-edit typos. It is intended for
use in CI pipelines to catch potentially malicious dependencies before they
are installed.

Threat model:
  Defended against:
    - one-edit typos and adjacent transpositions (distance rule)
    - separator confusion (removing -, _, .)
    - ASCII homoglyphs (0->o, 1->l, 3->e, 5->s, rn->m, vv->w)
    - affix squats of a popular name (e.g., requests-python)
  Not defended against:
    - Unicode confusables (registry names are ASCII)
    - packages missing from the popular list
    - dependency confusion between private and public indexes
    - malicious code in correctly named packages

Popular list (checked 2026-11-09):
  The bundled names are dated data and can be overridden through the
  ``popular`` argument. 18 of the PyPI names are in the top 40 of the hugovk
  top-pypi-packages ranking of monthly downloads
  (https://hugovk.dev/top-pypi-packages/, data of 2026-11-01; for example
  boto3 rank 1, requests rank 8, pandas rank 38), and django (rank 466) and
  flask (rank 162) are added as frequently imitated names. Every npm name had
  more than 50 million downloads from 2026-10-10 to 2026-11-08 according to
  the npm downloads API
  (https://api.npmjs.org/downloads/point/last-month/<name>).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Literal

__all__ = [
    "POPULAR",
    "Finding",
    "TyposquatError",
    "check",
    "normalize",
    "osa_distance",
]

Rule = Literal["homoglyph", "separator", "affix", "distance"]
ErrorCode = Literal["invalid_name", "invalid_ecosystem", "input_too_large"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass(frozen=True)
class Finding:
    """A single typosquat detection result."""

    rule: Rule
    target: str
    candidate: str


class TyposquatError(Exception):
    """Base error for the typosquat detector."""

    def __init__(self, code: ErrorCode, message: str = "") -> None:
        super().__init__(message)
        self.code = code


POPULAR: Mapping[str, tuple[str, ...]] = {
    "pypi": (
        "requests",
        "urllib3",
        "numpy",
        "pandas",
        "boto3",
        "botocore",
        "setuptools",
        "certifi",
        "idna",
        "charset-normalizer",
        "python-dateutil",
        "six",
        "packaging",
        "pyyaml",
        "django",
        "flask",
        "cryptography",
        "pydantic",
        "typing-extensions",
        "attrs",
    ),
    "npm": (
        "lodash",
        "react",
        "express",
        "chalk",
        "commander",
        "axios",
        "debug",
        "typescript",
        "webpack",
        "moment",
        "uuid",
        "yargs",
        "dotenv",
        "vue",
        "jquery",
    ),
}

_HOMOGLYPH_MAP = {"0": "o", "1": "l", "3": "e", "5": "s", "rn": "m", "vv": "w"}

# fullmatch avoids the ``$`` pitfall of matching before a trailing newline.
_PYPI_NAME_RE = re.compile(
    r"[A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9]",
    re.IGNORECASE,
)
_NPM_NAME_RE = re.compile(r"(@[a-z0-9-~][a-z0-9-._~]*/)?[a-z0-9-~][a-z0-9-._~]*")


def _validate_name(name: str, ecosystem: str) -> None:
    """Validate that a name is well-formed and not too long."""
    if len(name) > 214:
        raise TyposquatError("input_too_large", "name exceeds 214 characters")
    if ecosystem == "pypi":
        if _PYPI_NAME_RE.fullmatch(name) is None:
            raise TyposquatError("invalid_name", "name does not match PyPI naming rules")
    elif ecosystem == "npm":
        if _NPM_NAME_RE.fullmatch(name.lower()) is None:
            raise TyposquatError("invalid_name", "name does not match npm naming rules")
    else:
        raise TyposquatError("invalid_ecosystem", f"unsupported ecosystem: {ecosystem}")


def normalize(name: str, ecosystem: str = "pypi") -> str:
    """Normalize a package name according to the ecosystem's rules.

    PyPI (PEP 503): lowercase, runs of ``-``, ``_``, ``.`` become ``-``.
    npm: lowercase only.
    """
    _validate_name(name, ecosystem)
    if ecosystem == "pypi":
        return re.sub(r"[-_.]+", "-", name.lower())
    elif ecosystem == "npm":
        return name.lower()
    else:  # pragma: no cover - already validated
        raise TyposquatError("invalid_ecosystem")


def osa_distance(a: str, b: str) -> int:
    """Optimal string alignment distance.

    Allows insertions, deletions, substitutions and adjacent transpositions,
    each with cost 1.
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # DP table
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # deletion
                d[i][j - 1] + 1,  # insertion
                d[i - 1][j - 1] + cost,  # substitution
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)  # transposition
    return d[len(a)][len(b)]


def _homoglyph_equal(a: str, b: str) -> bool:
    """Return True if the two names are equal after applying the homoglyph map."""

    def map_str(s: str) -> str:
        s = s.lower()
        # multi-character replacements first
        s = s.replace("rn", "m").replace("vv", "w")
        for old, new in _HOMOGLYPH_MAP.items():
            if len(old) == 1:
                s = s.replace(old, new)
        return s

    return map_str(a) == map_str(b)


def _separator_equal(a: str, b: str) -> bool:
    """Return True if names are equal after removing -, _, ."""
    remove = str.maketrans("", "", "-_ .")
    return a.translate(remove) == b.translate(remove)


def _affix_equal(candidate: str, target: str, ecosystem: str) -> bool:
    """Return True if candidate is target plus a known prefix or suffix."""
    prefixes: tuple[str, ...]
    suffixes: tuple[str, ...]
    if ecosystem == "pypi":
        prefixes = ("python-", "py-", "py")
        suffixes = ("-python", "-py", "py", "-dev", "-lib")
    else:
        prefixes = ("node-", "js-")
        suffixes = ("-js", ".js", "js", "-node")

    for pref in prefixes:
        if candidate.startswith(pref) and candidate[len(pref) :] == target:
            return True
    return any(candidate.endswith(suff) and candidate[: -len(suff)] == target for suff in suffixes)


def check(
    name: str,
    *,
    ecosystem: Literal["pypi", "npm"] = "pypi",
    popular: Collection[str] | None = None,
) -> list[Finding]:
    """Check a candidate name against the popular list.

    Returns a list of :class:`Finding` objects, one per matched target,
    sorted by target alphabetically. The first matching rule per target
    (in order: homoglyph, separator, affix, distance) is reported.
    """
    if ecosystem not in ("pypi", "npm"):
        raise TyposquatError("invalid_ecosystem", f"unsupported ecosystem: {ecosystem}")
    _validate_name(name, ecosystem)

    targets = POPULAR[ecosystem] if popular is None else tuple(popular)

    norm_candidate = normalize(name, ecosystem)
    findings: list[Finding] = []

    for target in targets:
        norm_target = normalize(target, ecosystem)
        # Skip if candidate is the same package after normalisation.
        if norm_target == norm_candidate:
            continue

        # Registry semantics are case-insensitive, so all rules compare the
        # normalised forms of both names.
        a = norm_candidate
        b = norm_target

        # homoglyph
        if _homoglyph_equal(a, b):
            findings.append(Finding(rule="homoglyph", target=target, candidate=name))
            continue
        # separator
        if _separator_equal(a, b):
            findings.append(Finding(rule="separator", target=target, candidate=name))
            continue
        # affix
        if _affix_equal(a, b, ecosystem):
            findings.append(Finding(rule="affix", target=target, candidate=name))
            continue
        # distance
        if len(a) >= 4 and len(b) >= 4 and osa_distance(a, b) == 1:
            findings.append(Finding(rule="distance", target=target, candidate=name))
            continue

    findings.sort(key=lambda f: f.target)
    return findings
