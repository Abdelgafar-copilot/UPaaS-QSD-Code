from typing import Tuple
import pandas as pd
from electrical.test_result_gen import WaferSummary
from metadata.lot_context import LotContext
from metadata.metadata_gen import generate_wafer_metadata
from electrical.electrical_testing_gen import generate_wafer_electrical_testing
from schemas.full_schema import QualifiedSyntheticData

def generate_qsd(
        lot_number: int, 
        wafer_number: int, 
        batch_id: str, 
        lot: LotContext,
        base_yield: float = 0.95
) -> Tuple[QualifiedSyntheticData, pd.DataFrame, WaferSummary]:

    # Generate metadata
    lot_info, wafer_map_df, wafer_summary = generate_wafer_metadata(
        lot_number=lot_number,
        wafer_number=wafer_number,
        batch_id=batch_id,
        lot=lot
    )

    usable_radius = wafer_summary["usable_radius_mm"]

    # Generate electrical testing data
    electrical_test, df_filled, test_summary = generate_wafer_electrical_testing(
        df_blank=wafer_map_df,
        usable_radius_mm=usable_radius,
        base_yield=base_yield
    )

    qsd = QualifiedSyntheticData(
        meta=lot_info,
        electrical_test=electrical_test
    )

    return qsd, df_filled, test_summary
