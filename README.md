# Blockchain-IoT Agricultural Data

Transparent and tamper-resistant agricultural data with a blockchain-style
hash chain and IoT sensor records.

This is an **original, independent implementation inspired by** the 2025 paper
*“AN INTELLIGENT BLOCKCHAIN-IOT MODEL FOR TRANSPARENT AND TAMPER-RESISTANT
AGRICULTURAL DATA”*. It is **not** the official code from that paper, and it
does not claim to reproduce its results. It implements the core idea in a
small, readable form: sensor readings are chained together so that changing
an earlier reading breaks verification of every later one.

## What it does

- Records IoT sensor readings (temperature, humidity, soil moisture, etc.)
  as blocks in an append-only hash chain.
- Each block stores the SHA-256 hash of the previous block, so tampering is
  detectable.
- Verifies a whole chain and reports the first broken block, if any.
- Exports / imports chains as JSON, and reads sensor readings from CSV.
- Ships with a small command-line tool and tests. No blockchain node,
  no cryptocurrency, and no network service are required.

## Quick start

```bash
python3 -m pip install -e .
python3 examples/demo.py
```

That creates a short demo chain from `examples/sample_readings.csv`,
verifies it, then shows that changing one reading is detected.

### Command line

```bash
# Start a chain from a CSV file
agri-chain build --csv examples/sample_readings.csv --out chain.json

# Verify a chain
agri-chain verify --chain chain.json

# Add one reading
agri-chain add --chain chain.json --sensor soil-01 \
  --metric soil_moisture --value 31.2 --unit "%" --out chain.json
```

CSV columns: `timestamp,sensor_id,metric,value,unit`
Timestamp format: ISO 8601, for example `2025-01-10T08:00:00`.

## Project layout

```
src/agri_chain/
  chain.py    # Block, Chain, hashing, verification
  sensors.py  # SensorReading validation and CSV loading
  cli.py      # Command-line interface
examples/
  sample_readings.csv
  demo.py
tests/
  test_chain.py
```

## Tests

```bash
python3 -m pytest -q
# or, without pytest:
python3 -m unittest discover -s tests -v
```

## Author

**Engr. Muhammad Awais Khan** — Bahauddin Zakariya University, Multan (Pakistan)
Research interests: Machine Learning and Deep Learning, Cognitive Radio
Networks (CRNs), Wireless Sensor Networks (WSNs).

Google Scholar profile: https://scholar.google.com/citations?hl=en&user=c4UawvgAAAAJ

## Status

Experimental research code, version 0.1.0. It is a teaching and prototyping
implementation of a hash chain, not a production blockchain, and it has not
been audited for security. Do not use it as the sole record for decisions
where data integrity has legal or safety consequences.

## License

MIT — see `LICENSE`.
