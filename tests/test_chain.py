import json
import unittest
from pathlib import Path

from agri_chain import Chain, SensorReading
from agri_chain.sensors import load_csv


def _reading(value=25.0):
    return SensorReading(sensor_id="soil-01", metric="soil_moisture", value=value, unit="%")


class TestChain(unittest.TestCase):
    def test_empty_chain_verifies(self):
        ok, _ = Chain().verify()
        self.assertTrue(ok)

    def test_add_and_verify(self):
        chain = Chain()
        chain.add(_reading(31.2), timestamp="2025-01-10T08:00:00")
        chain.add(_reading(30.8), timestamp="2025-01-10T09:00:00")
        ok, message = chain.verify()
        self.assertTrue(ok, message)
        self.assertEqual(len(chain.blocks), 2)
        self.assertEqual(chain.blocks[1].previous_hash, chain.blocks[0].hash)

    def test_tampering_is_detected(self):
        chain = Chain()
        chain.add(_reading(31.2), timestamp="2025-01-10T08:00:00")
        chain.add(_reading(30.8), timestamp="2025-01-10T09:00:00")
        # Simulate tampering: rebuild the first block with a changed value,
        # keeping the second block's stored previous_hash.
        tampered = Chain()
        tampered.blocks = [
            # Re-create block 0 with a different value.
            __import__("agri_chain.chain", fromlist=["Block"]).Block(
                index=0,
                timestamp="2025-01-10T08:00:00",
                reading=_reading(99.9),
                previous_hash="0" * 64,
            ),
            chain.blocks[1],
        ]
        ok, _ = tampered.verify()
        self.assertFalse(ok)

    def test_json_round_trip(self):
        chain = Chain()
        chain.add(_reading(31.2), timestamp="2025-01-10T08:00:00")
        restored = Chain.from_json(chain.to_json())
        self.assertEqual([b.hash for b in restored.blocks], [b.hash for b in chain.blocks])
        ok, _ = restored.verify()
        self.assertTrue(ok)

    def test_csv_loading(self):
        rows = load_csv(Path(__file__).resolve().parent.parent / "examples" / "sample_readings.csv")
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0][1].sensor_id, "soil-01")


if __name__ == "__main__":
    unittest.main()
