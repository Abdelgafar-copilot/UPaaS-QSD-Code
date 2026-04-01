import json
from typing import Dict, List
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import pandas as pd

def draw_wafer(ax: Axes, wafer_diam_mm: float, edge_clear_mm: float):
    R_full = wafer_diam_mm / 2.0
    R_use = R_full - edge_clear_mm
    ax.add_patch(Circle((0, 0), R_full, fill=False, linewidth=1.0, alpha=0.4, edgecolor="black"))
    ax.add_patch(Circle((0, 0), R_use, fill=False, linewidth=1.2, edgecolor="black"))

def build_palette(n: int):
    base = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
        "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]
    return [base[i % len(base)] for i in range(n)]

def die_color(row: pd.Series, mode: str, palette_map: Dict[str, str]) -> str:
    if mode == "yield":
        val = str(row.get("Pass", "0"))
        if val in ["None", "nan"]:
            return "#B0B0B0"
        return "#2ca02c" if val == "1" else "#d62728"
    elif mode == "hbin":
        return palette_map.get(str(row.get("HBIN", "")), "#B0B0B0")
    elif mode == "sbin":
        return palette_map.get(str(row.get("SBIN", "")), "#B0B0B0")
    return "#B0B0B0"

def make_legend(ax: Axes, mode: str, palette_map: Dict[str, str]):
    handles: List[Rectangle] = []

    if mode == "yield":
        handles = [
            Rectangle((0,0),1,1, facecolor="#B0B0B0", edgecolor="black", label="UNT"),
            Rectangle((0,0),1,1, facecolor="#2ca02c", edgecolor="black", label="PASS"),
            Rectangle((0,0),1,1, facecolor="#d62728", edgecolor="black", label="FAIL"),
        ]
    else:
        handles = [Rectangle((0,0),1,1, facecolor="#B0B0B0", edgecolor="black", label="UNT")]
        for code, col in palette_map.items():
            handles.append(Rectangle((0,0),1,1, facecolor=col, edgecolor="black", label=code))
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8) # type: ignore

def plot_wafer_df(df: pd.DataFrame, meta_path: str, mode: str = "yield", save_path: str | None = None, title: str | None = None):
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

        wafer_diam_mm = float(meta.get("Diameter", meta.get("wafer_diam_mm", 300)))
        edge_clear_mm = float(meta.get("edge_clear_mm", 3.0))

        fig, ax = plt.subplots(figsize=(7,7)) # type: ignore
        draw_wafer(ax, wafer_diam_mm, edge_clear_mm)

        palette_map = {}
        if mode in ("hbin", "sbin"):
            key = "HBIN" if mode == "hbin" else "SBIN"
            codes = sorted(df[key].dropna().unique().tolist())
            colors = build_palette(len(codes))
            palette_map = {str(c): colors[i] for i, c in enumerate(codes)}

        meta_w = float(df.get("die_w_mm", pd.Series([10.0])).iloc[0])
        meta_h = float(df.get("die_h_mm", pd.Series([10.0])).iloc[0])

        for _, row in df.iterrows():
            x0 = float(row["die_x_mm"])
            y0 = float(row["die_y_mm"])
            w  = float(row.get("die_w_mm", meta_w))
            h  = float(row.get("die_h_mm", meta_h))
            color = die_color(row, mode, palette_map)
            ax.add_patch(Rectangle((x0, y0), w, h, linewidth=0.3, edgecolor="black", facecolor=color))

        R_full = wafer_diam_mm / 2.0
        ax.set_aspect("equal")
        ax.set_xlim(-R_full * 1.05, R_full * 1.05)
        ax.set_ylim(-R_full * 1.05, R_full * 1.05)
        ax.set_title(title or meta.get("WaferId", "Wafer"), fontsize=11) # type: ignore
        ax.set_xlabel("X [mm]") # type: ignore
        ax.set_ylabel("Y [mm]") # type: ignore

        make_legend(ax, mode, palette_map)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=200) # type: ignore
        else:
            plt.show() # type: ignore
        plt.close(fig)

def plot_wafer(csv_path: str, meta_path: str, mode: str = "yield", save_path: str | None = None, title: str | None = None):
    df = pd.read_csv(csv_path) # type: ignore
    plot_wafer_df(df, meta_path, mode=mode, save_path=save_path, title=title)
    