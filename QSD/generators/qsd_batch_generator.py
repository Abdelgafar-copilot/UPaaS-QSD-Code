import os, shutil, json, random
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict
import numpy as np

from electrical.electrical_testing_gen import generate_wafer_electrical_testing
from schemas.full_schema import QualifiedSyntheticData
from schemas.lean_filter import convert_qsd_to_lean
from utils.map_visualizer import plot_wafer_df

from utils.utils import (
    generate_batch_id, generate_workroute_id, generate_operation_id,
    generate_equip_id, generate_last_update, generate_global_route_id,
    generate_thickness_raw, generate_thickness_finished,
    generate_product_number, generate_basic_type,
    generate_resistivity_class, build_facility_id, build_facility_name
)

from metadata.lot_context import LotContext
from metadata.metadata_gen import generate_wafer_metadata

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Lookup tables
MANUFACTURERS = ["Infineon", "TSMC", "GlobalFoundries"]
SUPPLIERS = {"Infineon": "Siltronic", "TSMC": "SUMCO", "GlobalFoundries": "Shin-Etsu"}
PRODUCTION_SITES = {"Infineon": "Dresden", "TSMC": "Hsinchu", "GlobalFoundries": "Singapore"}
LOCATION_IDS = {"Dresden": "DRS", "Hsinchu": "HSC", "Singapore": "SGP"}
BASE_MATERIAL = ["Si", "SiC", "GaN"]
DOPANT = ["BOR", "PHOS"]
INGOT_PULLING = ["Czochralski method", "Float-zone method", "Bridgman method"]
TECHNOLOGY = ["Sensor", "Power", "RF", "Logic"]
DIAMETER = [150, 200, 300]


def to_dict(obj): # type: ignore
    """Safe recursive converter for dataclasses, lists, dicts, and datetime."""
    if is_dataclass(obj): # type: ignore
        d = asdict(obj) # type: ignore
        for k, v in d.items():
            d[k] = to_dict(v)
        return d
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()} # type: ignore
    elif isinstance(obj, list):
        return [to_dict(v) for v in obj] # type: ignore
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj # type: ignore


def generate_all(num_lots: int = 2, wafers_per_lot: int = 25, out_root: str = "output"):
    # Clean output directory
    if os.path.exists(out_root):
        shutil.rmtree(out_root)

    os.makedirs(os.path.join(out_root, "full"))
    os.makedirs(os.path.join(out_root, "lean"))

    batch_id = generate_batch_id()
    print(f"Generated Batch ID: {batch_id}\n")

    for lot_number in range(1, num_lots + 1):

        # Build base context
        manufacturer = random.choice(MANUFACTURERS)
        wafer_supplier = SUPPLIERS[manufacturer]
        production_site = PRODUCTION_SITES[manufacturer]
        location = production_site
        location_id = LOCATION_IDS[production_site]
        diameter = random.choice(DIAMETER)
        facility = build_facility_name(production_site, diameter)
        facility_id = build_facility_id(location_id, diameter)

        die_w = round(random.uniform(4.0, 6.0), 1)
        die_h = round(random.uniform(4.0, 6.0), 1)

        thickness_raw = generate_thickness_raw()

        lot_dict: Dict[str, Any] = {
            "Manufacturer": manufacturer,
            "WaferSupplier": wafer_supplier,
            "ProductionSite": production_site,
            "Location": location,
            "LocationId": location_id,
            "Facility": facility,
            "FacilityId": facility_id,
            "BaseMaterial": random.choice(BASE_MATERIAL),
            "Dopant": random.choice(DOPANT),
            "IngotPulling": random.choice(INGOT_PULLING),
            "ThicknessRaw": thickness_raw,
            "ThicknessFinished": generate_thickness_finished(thickness_raw),
            "ResistivityClass": generate_resistivity_class("Dopant", "BaseMaterial"),
            "Technology": random.choice(TECHNOLOGY),
            "ProductNumber": generate_product_number(),
            "BasicType": generate_basic_type(),
            "workRouteId": generate_workroute_id(),
            "operationId": generate_operation_id(),
            "equipId": generate_equip_id(),
            "globalRouteId": generate_global_route_id(),
            "LastUpdate": generate_last_update(),
            "Diameter": diameter,
            "DieWidth": die_w,
            "DieHeight": die_h
        }

        lot_ctx = LotContext(**lot_dict)

        # Output dirs
        full_lot_dir = os.path.join(out_root, "full", f"lot_{lot_number:02d}")
        lean_lot_dir = os.path.join(out_root, "lean", f"lot_{lot_number:02d}")
        os.makedirs(full_lot_dir, exist_ok=True)
        os.makedirs(lean_lot_dir, exist_ok=True)

        # Generate wafers
        for wafer_number in range(1, wafers_per_lot + 1):
            wafer_id = f"{batch_id}{lot_number}.{wafer_number:02d}"
            print(f"-> Lot {lot_number:02d}, Wafer {wafer_number:02d} ({wafer_id})")

            lot_info, wafer_map_df, wafer_summary = generate_wafer_metadata(
                lot_number=lot_number,
                wafer_number=wafer_number,
                batch_id=batch_id,
                lot=lot_ctx
            )

            electrical, df_filled, _ = generate_wafer_electrical_testing(
                df_blank=wafer_map_df,
                usable_radius_mm=wafer_summary["usable_radius_mm"],
                base_yield=0.95
            )

            # Build full QSD
            full_qsd = QualifiedSyntheticData(meta=lot_info, electrical_test=electrical)

            # Build lean QSD
            lean_qsd = convert_qsd_to_lean(full_qsd)

            # Save metadata
            meta_path = os.path.join(full_lot_dir, f"{wafer_id}_metadata.json")
            with open(meta_path, "w") as f:
                json.dump(to_dict(full_qsd.meta), f, indent=2)

            # Save electrical testing
            with open(os.path.join(full_lot_dir, f"{wafer_id}_electrical.json"), "w") as f:
                json.dump(to_dict(full_qsd.electrical_test), f, indent=2)

            # Save lean version
            with open(os.path.join(lean_lot_dir, f"{wafer_id}_lean.json"), "w") as f:
                json.dump(to_dict(lean_qsd), f, indent=2)

            # Save wafer map csv
            csv_path = os.path.join(full_lot_dir, f"{wafer_id}_map.csv")
            df_export = df_filled[["DieId", "Pass", "HBIN", "SBIN", "DieLocation"]]
            df_export.to_csv(csv_path, index=False)

            # Wafer map csv and plots saved ONLY for full version
            csv_path = os.path.join(full_lot_dir, f"{wafer_id}_map.csv")
            df_export = df_filled[["DieId", "Pass", "HBIN", "SBIN", "DieLocation"]]
            df_export.to_csv(csv_path, index=False)

            # Plots
            plot_wafer_df(
                df_filled,
                meta_path,
                mode="yield",
                save_path=os.path.join(full_lot_dir, f"{wafer_id}_yield.png"),
                title=f"{wafer_id} (Yield)"
            )

            plot_wafer_df(
                df_filled,
                meta_path,
                mode="hbin",
                save_path=os.path.join(full_lot_dir, f"{wafer_id}_hbin.png"),
                title=f"{wafer_id} (HBIN)"
            )

            plot_wafer_df(
                df_filled,
                meta_path,
                mode="sbin",
                save_path=os.path.join(full_lot_dir, f"{wafer_id}_sbin.png"),
                title=f"{wafer_id} (SBIN)"
            )


    print(f"\nGenerated {num_lots} lots x {wafers_per_lot} wafers.")

if __name__ == "__main__":
    generate_all(num_lots=1, wafers_per_lot=1)
