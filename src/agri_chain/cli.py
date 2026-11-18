"""Command-line interface: ``agri-chain build|add|verify``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .chain import Chain
from .sensors import SensorReading, load_csv


def _load_chain(path: Path) -> Chain:
    return Chain.from_json(path.read_text(encoding="utf-8"))


def _save_chain(chain: Chain, path: Path) -> None:
    path.write_text(chain.to_json() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agri-chain",
        description="Hash-chained agricultural sensor records.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build a chain from a CSV file")
    build.add_argument("--csv", required=True, help="Input CSV file")
    build.add_argument("--out", required=True, help="Output chain JSON file")

    add = sub.add_parser("add", help="Add one reading to a chain")
    add.add_argument("--chain", required=True, help="Chain JSON file")
    add.add_argument("--sensor", required=True)
    add.add_argument("--metric", required=True)
    add.add_argument("--value", required=True, type=float)
    add.add_argument("--unit", required=True)
    add.add_argument("--timestamp", default=None)
    add.add_argument("--out", required=True, help="Output chain JSON file")

    verify = sub.add_parser("verify", help="Verify a chain")
    verify.add_argument("--chain", required=True, help="Chain JSON file")

    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            chain = Chain()
            for timestamp, reading in load_csv(args.csv):
                chain.add(reading, timestamp=timestamp)
            _save_chain(chain, Path(args.out))
            print(f"built chain with {len(chain.blocks)} block(s) -> {args.out}")
            return 0

        if args.command == "add":
            chain = _load_chain(Path(args.chain))
            block = chain.add(
                SensorReading(
                    sensor_id=args.sensor,
                    metric=args.metric,
                    value=args.value,
                    unit=args.unit,
                ),
                timestamp=args.timestamp,
            )
            _save_chain(chain, Path(args.out))
            print(f"added block {block.index} ({block.hash[:12]}...) -> {args.out}")
            return 0

        if args.command == "verify":
            chain = _load_chain(Path(args.chain))
            ok, message = chain.verify()
            print(message)
            return 0 if ok else 1
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
