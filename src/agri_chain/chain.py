"""A small append-only hash chain for agricultural sensor readings.

Each block contains one sensor reading and the SHA-256 hash of the
previous block. Changing any earlier reading changes its hash, which
no longer matches the ``previous_hash`` stored in the next block, so
:func:`Chain.verify` reports the chain as broken.

This is a teaching / prototyping implementation, not a production
blockchain: there is no consensus, no peer-to-peer network, and no
protection against an attacker who rewrites the whole chain.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

from .sensors import SensorReading


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Block:
    """One chained sensor reading."""

    index: int
    timestamp: str
    reading: SensorReading
    previous_hash: str
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        payload = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "reading": asdict(self.reading),
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        object.__setattr__(self, "hash", _sha256_hex(payload))

    def to_dict(self) -> dict:
        data = asdict(self)
        data["reading"] = asdict(self.reading)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        block = cls(
            index=int(data["index"]),
            timestamp=str(data["timestamp"]),
            reading=SensorReading(**data["reading"]),
            previous_hash=str(data["previous_hash"]),
        )
        if block.hash != data["hash"]:
            raise ValueError(f"block {block.index}: stored hash does not match content")
        return block


class Chain:
    """An append-only chain of :class:`Block` objects."""

    def __init__(self) -> None:
        self.blocks: list[Block] = []

    def add(self, reading: SensorReading, timestamp: str | None = None) -> Block:
        """Append a reading and return the new block."""
        ts = timestamp or datetime.now().isoformat(timespec="seconds")
        previous_hash = self.blocks[-1].hash if self.blocks else "0" * 64
        block = Block(
            index=len(self.blocks),
            timestamp=ts,
            reading=reading,
            previous_hash=previous_hash,
        )
        self.blocks.append(block)
        return block

    def verify(self) -> tuple[bool, str]:
        """Check the whole chain. Returns ``(ok, message)``."""
        previous_hash = "0" * 64
        for block in self.blocks:
            if block.previous_hash != previous_hash:
                return False, f"block {block.index}: previous_hash mismatch"
            # Recompute the hash from the stored content.
            rebuilt = Block(
                index=block.index,
                timestamp=block.timestamp,
                reading=block.reading,
                previous_hash=block.previous_hash,
            )
            if rebuilt.hash != block.hash:
                return False, f"block {block.index}: content hash mismatch (tampered?)"
            previous_hash = block.hash
        for i, block in enumerate(self.blocks):
            if block.index != i:
                return False, f"block at position {i} has index {block.index}"
        return True, f"chain OK: {len(self.blocks)} block(s) verified"

    def to_dict(self) -> dict:
        return {"version": 1, "blocks": [b.to_dict() for b in self.blocks]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict) -> "Chain":
        chain = cls()
        chain.blocks = [Block.from_dict(b) for b in data["blocks"]]
        return chain

    @classmethod
    def from_json(cls, text: str) -> "Chain":
        return cls.from_dict(json.loads(text))
