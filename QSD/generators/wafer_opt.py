from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, TypedDict
import pandas as pd

# Constant
EPS = 1e-12

# Type aliases
Die = Tuple[float, float, str] # (x, y, "FULL"/"PART")

class PackingResult(TypedDict):
    summary: Dict[str, Any]
    wafer_map_df: pd.DataFrame

# Input specification dataclass
@dataclass
class WaferSpecRect:
    # Wafer geometry
    wafer_diam_mm: float                 # wafer diameter in mm (e.g., 150 / 200 / 300)
    edge_clear_mm: float                 # edge exclusion ring in mm
    notch_height_mm: float = 0.0         # notch/flat depth from outer edge in mm (0 = no notch)

    # Die geometry and scribe lanes
    die_w_mm: float = 10.0               # die width in mm
    die_h_mm: float = 10.0               # die height in mm
    spacing_x_mm: float = 0.2            # scribe lane in X direction (mm)
    spacing_y_mm: float = 0.2            # scribe lane in Y direction (mm)

    # Brute-force stepping
    step_mm: float = 0.5                 # offset step size in mm

# Geometry helpers
def _corners(x0: float, y0: float, w: float, h: float) -> List[Tuple[float, float]]:
    """Return the four corners of a rectangle with lower-left corner (x0, y0)."""
    return [(x0, y0), (x0 + w, y0), (x0, y0 + h), (x0 + w, y0 + h)]

def _inside_circle(x: float, y: float, R: float) -> bool:
    """Check if point (x, y) lies inside a circle of radius R centered at (0, 0)."""
    return (x * x + y * y) <= (R * R)

def _die_fully_inside(x0: float, y0: float, w: float, h: float, R_use: float) -> bool:
    """True if all four corners are inside usable circle (with edge exclusion)."""
    return all(_inside_circle(x, y, R_use) for (x, y) in _corners(x0, y0, w, h))

def _die_partially_inside(x0: float, y0: float, w: float, h: float, R_full: float) -> bool:
    """True if at least one corner is inside the full wafer circle (without edge exclusion)."""
    return any(_inside_circle(x, y, R_full) for (x, y) in _corners(x0, y0, w, h))

def _above_notch(y0: float, h: float, notch_y: float) -> Tuple[bool, bool]:
    """
    Check position relative to horizontal notch line y=notch_y.
    fully  — bottom edge of die is above notch line,
    partly — at least the top edge of die is above notch line.
    """
    lower = y0
    upper = y0 + h
    fully = (lower >= notch_y)
    partly = (upper >= notch_y)
    return fully, partly

# Main optimization function
def optimize_rect_packing(spec: WaferSpecRect) -> PackingResult:
    """
    Brute-force rectangular die packing on a circular wafer.
    Offsets (h,v) are scanned within one pitch_x * pitch_y period with step=step_mm.
    For each offset, generate die grid and count how many FULL dies (completely usable) fit.
    Return the configuration with the maximum number of FULL dies and a blank wafer map.
    """
    # Radii
    R_full = spec.wafer_diam_mm / 2.0
    R_use  = R_full - spec.edge_clear_mm

    # Die parameters and pitches
    w = spec.die_w_mm
    h = spec.die_h_mm
    pitch_x = spec.die_w_mm + spec.spacing_x_mm
    pitch_y = spec.die_h_mm + spec.spacing_y_mm
    step = spec.step_mm

    # Notch line (horizontal cut at bottom). Notch depth measured from outer edge.
    notch_from_outer = max(0.0, spec.notch_height_mm - spec.edge_clear_mm)
    notch_y = -R_use + notch_from_outer  # dies below this line are cut off

    # Bounding box for die lower-left corner search
    x_min = -R_full - w
    x_max =  R_full
    y_min = -R_full - h
    y_max =  R_full

    best: Dict[str, Any] = {
        "count": 0, 
        "partial": 0, 
        "hoff_mm": 0.0, 
        "voff_mm": 0.0, 
        "dies": []
    }

    # Iterate over offsets within one period in X and Y
    h_off = 0.0
    while h_off < (pitch_x) - EPS:
        v_off = 0.0
        while v_off < (pitch_y) - EPS:
            dies: List[Tuple[float, float, str]] = []
            count_full = 0
            count_part = 0

            # Sweep grid with this offset
            x0 = x_min + h_off
            while x0 <= (x_max - w + EPS):
                y0 = y_min + v_off
                while y0 <= (y_max - h + EPS):
                    fully, partly = _above_notch(y0, h, notch_y)
                    if fully:
                        if _die_fully_inside(x0, y0, w, h, R_use):
                            dies.append((x0, y0, "FULL")); count_full += 1
                        elif _die_partially_inside(x0, y0, w, h, R_full):
                            dies.append((x0, y0, "PART")); count_part += 1
                    elif partly:
                        if _die_partially_inside(x0, y0, w, h, R_full):
                            dies.append((x0, y0, "PART")); count_part += 1
                    y0 += pitch_y
                x0 += pitch_x

            if count_full > best["count"]:
                best = {
                    "count": count_full,
                    "partial": count_part,
                    "hoff_mm": round(h_off, 6),
                    "voff_mm": round(v_off, 6),
                    "dies": dies
                }
            v_off += step
        h_off += step

    # Build wafer map (blank) with only FULL dies of best config
    rows: List[Dict[str, Any]] = []

    for (x, y, kind) in best["dies"]:
        if kind == "FULL":
            rows.append({
                "die_x_mm": round(x, 6),         # lower-left corner of die
                "die_y_mm": round(y, 6),
                "die_w_mm": w,
                "die_h_mm": h,
                "status": "UNT",                  # blank/unfilled
                "passed": None,
                "hbin": None,
                "sbin": None
            })

    wafer_map_df = pd.DataFrame(rows)

    summary: Dict[str, Any] = {
        "usable_radius_mm": R_use,
        "notch_y_mm": notch_y,
        "die_w_mm": w,
        "die_h_mm": h,
        "pitch_x_mm": pitch_x,
        "pitch_y_mm": pitch_y,
        "best_offsets_mm": {
            "h": best["hoff_mm"], 
            "v": best["voff_mm"]
        },
        "max_full_dies": best["count"],
        "max_partial_dies": best["partial"]
    }

    return {
        "summary": summary, 
        "wafer_map_df": wafer_map_df
    }
    