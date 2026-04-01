import random, math
from typing import Any, Dict, List, Tuple, TypedDict
import pandas as pd

class DieRecord(TypedDict):
    DieId: str
    Pass: str
    HBIN: str
    SBIN: str
    DieLocation: str
    die_x_mm: float
    die_y_mm: float
    die_w_mm: float
    die_h_mm: float

# Hard and Soft BIN definitions
HARD_BINS = {
    "PASS": "HBIN_1", # fully functional die
    "CONTACT_FAIL": "HBIN_2", # contact/probe issue
    "FUNC_FAIL": "HBIN_3", # logic/functional fail
    "PARAM_FAIL": "HBIN_4" # parametric spec fail
}

SOFT_BINS = {
    "CONTACT_FAIL": [
        "SBIN_CONT_GND", # contact to ground
        "SBIN_OPEN_PAD", # open pad
        "SBIN_PROBE_WEAR" # worn probe tip
    ],
    "FUNC_FAIL": [
        "SBIN_LOGIC_ERR", # logic fail
        "SBIN_TIMING_ERR", # clock/timing issue
        "SBIN_PWR_ERR", # power rail unstable
    ],
    "PARAM_FAIL": [
        "SBIN_VTH_DRIFT", # threshold voltage drift
        "SBIN_IDDQ_HIGH", # leakage current high
        "SBIN_GAIN_LOW"  # analog gain below spec
    ],
    "PASS": ["SBIN_PASS"]
}

def populate_wafer_map(
        df_blank: pd.DataFrame,
        usable_radius_mm: float,
        base_yield: float = 0.95
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Populate wafer map with pass/fail results.
    Dies near the edge have lower yield probability.

    Args:
        df_blank: blank wafer map DataFrame from wafer_opt
        (must contain die_x_mm, die_y_mm, die_w_mm, die_h_mm)
        usable_radius_mm: wafer usable radius (from optimize_rect_packing)
        base_yield: nominal pass probability for dies in the center
        edge_penalty: yield reduction factor for dies near the edge
        cluster_prob: chance to add a local defect cluster
        cluster_radius_mm: cluster radius (mm)
    Returns:
        df_filled: wafer map with DieId, Pass, HBIN, SBIN, DieLocation
        summary: dict with quantity_in/out and yield metrics
    """

    die_records: List[DieRecord] = []
    passed_cnt = 0

    for idx, (_, row) in enumerate(df_blank.iterrows(), start=1):
        cx = row['die_x_mm'] + row['die_w_mm'] / 2.0
        cy = row['die_y_mm'] + row['die_h_mm'] / 2.0

        # Radial distance from wafer center
        r_norm = min(1.0, math.sqrt(cx**2 + cy**2) / usable_radius_mm)
        edge_effect = max(0.20, 1 - (r_norm ** 4) * 0.8)

        # Edge effect on pass probability
        p_pass = base_yield * edge_effect

        # Random local defect
        if random.random() < 0.02:
            p_pass *= 0.25

        passed = random.random() < p_pass

        # Bin assignment
        if passed:
            hbin = HARD_BINS["PASS"]
            sbin = SOFT_BINS["PASS"][0]
        else:
            fail_type = random.choices(
                ["CONTACT_FAIL", "FUNC_FAIL", "PARAM_FAIL"],
                weights=[0.5, 0.3, 0.2],
                k=1
            )[0]
            hbin = HARD_BINS[fail_type]
            sbin = random.choice(SOFT_BINS[fail_type])

        if passed:
            passed_cnt += 1

        die_rec: DieRecord = {
            "DieId": f"d{idx}",
            "Pass": "1" if passed else "0",
            "HBIN": hbin,
            "SBIN": sbin,
            "DieLocation": f"{cx:.2f},{cy:.2f}",
            "die_x_mm": float(row["die_x_mm"]),
            "die_y_mm": float(row["die_y_mm"]),
            "die_w_mm": float(row["die_w_mm"]),
            "die_h_mm": float(row["die_h_mm"])
        }

        die_records.append(die_rec)

    df_filled = pd.DataFrame(die_records)
    total_dies = len(df_filled)
    yield_passed = round(passed_cnt / total_dies, 4)
    yield_fab = round(yield_passed * random.uniform(0.97, 0.99), 4)

    summary: Dict[str, Any] = {
        "quantity_in": total_dies,
        "quantity_out": passed_cnt,
        "yield_passed": yield_passed,
        "yield_fab": yield_fab
    }

    return df_filled, summary
    