"""Sensor reading validation and CSV loading."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SensorReading:
    """One validated IoT sensor reading."""

    sensor_id: str
    metric: str
    value: float
    unit: str

    def __post_init__(self) -> None:
        if not self.sensor_id.strip():
            raise ValueError("sensor_id must not be empty")
        if not self.metric.strip():
            raise ValueError("metric must not be empty")
        if self.value != self.value:  # NaN check, without importing math
            raise ValueError("value must not be NaN")


def parse_timestamp(text: str) -> str:
    """Validate an ISO 8601 timestamp and return it unchanged."""
    datetime.fromisoformat(text)  # raises ValueError on bad input
    return text


def load_csv(path: str | Path) -> list[tuple[str, SensorReading]]:
    """Load ``(timestamp, reading)`` pairs from a CSV file.

    Expected columns: ``timestamp,sensor_id,metric,value,unit``.
    """
    rows: list[tuple[str, SensorReading]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "sensor_id", "metric", "value", "unit"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV must have columns: {sorted(required)}")
        for line_no, row in enumerate(reader, start=2):
            try:
                rows.append(
                    (
                        parse_timestamp(row["timestamp"].strip()),
                        SensorReading(
                            sensor_id=row["sensor_id"].strip(),
                            metric=row["metric"].strip(),
                            value=float(row["value"]),
                            unit=row["unit"].strip(),
                        ),
                    )
                )
            except (ValueError, KeyError) as exc:
                raise ValueError(f"CSV line {line_no}: {exc}") from exc
    if not rows:
        raise ValueError("CSV contains no readings")
    return rows
