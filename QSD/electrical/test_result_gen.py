from typing import List, Tuple, TypedDict
import pandas as pd
from schemas.full_schema import DieResult
from electrical.map_populator import populate_wafer_map

class WaferResult(TypedDict):
    quantity_in: int
    quantity_out: int
    yield_passed: float
    yield_fab: float
    die_results: List[DieResult]

class WaferSummary(TypedDict):
    quantity_in: int
    quantity_out: int
    yield_passed: float
    yield_fab: float

def generate_wafer_test_result(
        df_blank: pd.DataFrame,
        usable_radius_mm: float,
        base_yield: float
) -> Tuple[WaferResult, pd.DataFrame, WaferSummary]:
    """
    Populate wafer map and compute fab yields.
    """

    # Populate wafer map
    df_filled, summary = populate_wafer_map(
        df_blank=df_blank,
        usable_radius_mm=usable_radius_mm,
        base_yield=base_yield
    )

    # Extract values from summary
    quantity_in = summary["quantity_in"]
    quantity_out = summary["quantity_out"]
    yield_passed = summary["yield_passed"]
    yield_fab = summary["yield_fab"]

    # Convert dies to dataclasses
    die_results = [
        DieResult(
            DieId=row['DieId'],
            HBIN=row['HBIN'],
            SBIN=row['SBIN'],
            Pass=row['Pass'],
            DieLocation=row["DieLocation"]
        )
        for _, row in df_filled.iterrows()
    ]

    # Return results
    wafer_result = WaferResult(
        quantity_in=quantity_in,
        quantity_out=quantity_out,
        yield_passed=yield_passed,
        yield_fab=yield_fab,
        die_results=die_results
    )

    # Typed WaferSummary
    wafer_summary = WaferSummary(
        quantity_in=quantity_in,
        quantity_out=quantity_out,
        yield_passed=yield_passed,
        yield_fab=yield_fab
    )

    return wafer_result, df_filled, wafer_summary
