# Qualified Synthetic Data (QSD) Generator

This project generates Qualified Synthetic Data (QSD) to simulate semiconductor wafer testing workflows. It builds realistic wafer metadata, simulates die-level electrical testing results, computes yield metrics, and exports both a full dataset and a reduced (lean) dataset for data exchange between a requester and a provider.

## Key features
- Realistic wafer metadata with materials, facilities, routes, and product info
- Die placement optimization on a circular wafer with edge exclusion
- Die-level electrical testing outcomes with HBIN/SBIN and yield metrics
- Full QSD output, including a lean exchange format
- Wafer map CSVs and optional visual plots
- Deterministic output with a fixed random seed

## How it works (pipeline)
1. A lot-level context is created with manufacturer, facility, wafer size, and routing IDs.
2. Wafer geometry is optimized to maximize full dies and produce a blank wafer map.
3. Wafer and product metadata are assembled into the full schema.
4. Electrical testing is simulated per die with edge effects and randomized defects.
5. Metadata and electrical testing are combined into a full QSD record.
6. The full record is reduced into the lean exchange schema.
7. Outputs are exported to JSON, CSV, and optional plots.

## Project structure
- generators/qsd_batch_generator.py: Batch orchestration, output writing, plots
- generators/qsd_builder.py: Single-wafer pipeline wrapper
- metadata/metadata_gen.py: Wafer metadata + blank map creation
- generators/wafer_opt.py: Die packing optimization on the wafer
- electrical/electrical_testing_gen.py: Electrical test wrapper and run metadata
- electrical/test_result_gen.py: Yield summary + die result objects
- electrical/map_populator.py: Per-die pass/fail and bin assignment
- schemas/full_schema.py: Full QSD dataclasses
- schemas/lean_filter.py: Full-to-lean conversion
- schemas/lean_schema.py: Lean QSD dataclasses
- utils/utils.py: Random ID and metadata helpers
- utils/map_visualizer.py: Wafer map plotting

## Usage
### Run a batch
- python3 -m generators.qsd_batch_generator

## Full vs lean schema
- Full QSD includes detailed lot metadata, wafer specifications, full test run info, and all die results with HBIN/SBIN.

- Lean QSD keeps only essential identifiers, yield metrics, and minimal die results (DieId, Pass, DieLocation) for exchange.

## Dependencies
This project uses:
- Python 3
- numpy
- pandas
- matplotlib

If you are not using the bundled venv, install dependencies with pip:
- pip install numpy pandas matplotlib