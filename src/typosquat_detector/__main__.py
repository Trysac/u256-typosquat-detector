"""Command-line interface for the typosquat detector."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import TyposquatError, check


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return an exit code (0 none, 1 findings, 2 usage/error)."""
    parser = argparse.ArgumentParser(prog="typosquat-detector")
    parser.add_argument("names", nargs="*", help="package names to check")
    parser.add_argument("--ecosystem", choices=["pypi", "npm"], default="pypi")
    parser.add_argument("--popular", type=Path, help="file with one popular name per line")
    args = parser.parse_args(argv)

    if not args.names:
        parser.print_usage()
        return 2

    popular = None
    if args.popular:
        try:
            stat = args.popular.stat()
            if stat.st_size > 1 * 1024 * 1024:
                print("popular file exceeds 1 MiB", file=sys.stderr)
                return 2
            with args.popular.open("r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if len(lines) > 10_000:
                print("popular file has more than 10,000 lines", file=sys.stderr)
                return 2
            popular = lines
        except (OSError, UnicodeDecodeError) as e:
            print(f"error reading popular file: {e}", file=sys.stderr)
            return 2

    found = False
    for name in args.names:
        try:
            findings = check(name, ecosystem=args.ecosystem, popular=popular)
            for f in findings:
                print(f"{name}: {f.rule} -> {f.target}")
                found = True
        except TyposquatError as e:
            print(f"invalid name '{name}': {e}", file=sys.stderr)
            return 2
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
