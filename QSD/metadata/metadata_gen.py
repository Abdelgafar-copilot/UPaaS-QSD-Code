from typing import Tuple, TypedDict
import pandas as pd
from generators.wafer_opt import WaferSpecRect, optimize_rect_packing
from schemas.full_schema import (
    LotInfo,
    WaferSpecifications,
    ProductInformation
)
from metadata.lot_context import LotContext

class WaferMetadataSummary(TypedDict):
    max_full_dies: int
    usable_radius_mm: float
    wafer_diam_mm: float
    die_w_mm: float
    die_h_mm: float

def generate_wafer_metadata(
        lot_number: int, 
        wafer_number: int, 
        batch_id: str,
        lot: LotContext
) -> Tuple[LotInfo, pd.DataFrame, WaferMetadataSummary]:
    """Generate wafer metadata."""
    
    lot_id = f"{batch_id}{lot_number}"
    wafer_id = f"{lot_id}.{wafer_number}"

    # Wafer geometry and chip layout
    spec = WaferSpecRect(
        wafer_diam_mm=lot.Diameter,
        edge_clear_mm=3.0,
        notch_height_mm=0.0,
        die_w_mm=lot.DieWidth,
        die_h_mm=lot.DieHeight,
        spacing_x_mm=0.2,
        spacing_y_mm=0.2,
        step_mm=0.5
    )

    wafer_result = optimize_rect_packing(spec)
    summary = wafer_result["summary"]
    summary_typed: WaferMetadataSummary = {
    "max_full_dies": summary["max_full_dies"],
    "usable_radius_mm": summary["usable_radius_mm"],
    "wafer_diam_mm": spec.wafer_diam_mm,
    "die_w_mm": spec.die_w_mm,
    "die_h_mm": spec.die_h_mm
}
    wafer_map_df = wafer_result["wafer_map_df"]

    chips_per_wafer = summary["max_full_dies"]
    chip_size = f"{spec.die_w_mm}x{spec.die_h_mm} mm"

    # WaferSpecifications dataclass
    wafer_spec = WaferSpecifications(
        Diameter=lot.Diameter,
        BaseMaterial=lot.BaseMaterial,
        thicknessRaw=lot.ThicknessRaw,
        thicknessFinished=lot.ThicknessFinished,
        Dopant=lot.Dopant,
        IngotPulling=lot.IngotPulling,
        ResistivityClass=lot.ResistivityClass
    )

    # ProductInformation dataclass
    product_info = ProductInformation(
        ProductNumber=lot.ProductNumber,
        Technology=lot.Technology,
        BasicType=lot.BasicType,
        chipsPerWafer=chips_per_wafer,
        chipSize=chip_size
    )

    # LotInfo dataclass
    lot_info = LotInfo(
        LotId=lot_id,
        BatchId=batch_id,
        WaferId=wafer_id,
        LotPosition=f"{lot_number:02d}",
        BatchPosition="01",
        Manufacturer=lot.Manufacturer,
        WaferSupplier=lot.WaferSupplier,
        ProductionSite=lot.ProductionSite,
        Facility=lot.Facility,
        FacilityId=lot.FacilityId,
        Location=lot.Location,
        LocationId=lot.LocationId,
        workRouteId=lot.workRouteId,
        operationId=lot.operationId,
        equipId=lot.equipId,
        lastUpdate=lot.LastUpdate,
        globalRouteId=lot.globalRouteId,
        WaferSpecifications=wafer_spec,
        ProductInformation=product_info
    )

    return lot_info, wafer_map_df, summary_typed
