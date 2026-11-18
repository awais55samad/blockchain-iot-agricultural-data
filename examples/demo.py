"""Demo: build a chain from the sample CSV, verify it, then tamper with it."""

from pathlib import Path

from agri_chain import Chain
from agri_chain.chain import Block
from agri_chain.sensors import load_csv

ROOT = Path(__file__).resolve().parent


def main() -> None:
    chain = Chain()
    for timestamp, reading in load_csv(ROOT / "sample_readings.csv"):
        chain.add(reading, timestamp=timestamp)

    ok, message = chain.verify()
    print(message)
    print(f"last block hash: {chain.blocks[-1].hash}")

    # Tamper with the first block and show verification fails.
    tampered = Chain()
    tampered.blocks = [
        Block(
            index=0,
            timestamp=chain.blocks[0].timestamp,
            reading=chain.blocks[0].reading,
            previous_hash=chain.blocks[0].previous_hash,
        ),
        *chain.blocks[1:],
    ]
    # Change the value in block 0 by rebuilding it (hash changes).
    from agri_chain import SensorReading

    tampered.blocks[0] = Block(
        index=0,
        timestamp=chain.blocks[0].timestamp,
        reading=SensorReading(sensor_id="soil-01", metric="soil_moisture", value=99.9, unit="%"),
        previous_hash="0" * 64,
    )
    ok, message = tampered.verify()
    print(f"after tampering: ok={ok} — {message}")


if __name__ == "__main__":
    main()
