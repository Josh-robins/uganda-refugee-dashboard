"""
Uganda Refugee Population Dashboard — Streamlit Edition
Built from refugee_visualisation (1).ipynb
Data: UNHCR Uganda / OPM proGres — 31 March 2026
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from PIL import Image

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uganda Refugee Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand constants ────────────────────────────────────────────────────────
BLUE   = "#185FA5"
TEAL   = "#2A9D8F"
ACCENT = "#D85A30"
TEXT   = "#2C2C2A"
MUTED  = "#888780"
BG     = "#FAFAF8"
GRID   = "#D3D1C7"

AGE_GROUPS = ["0-4", "5-11", "12-17", "18-35", "36-59", "60+"]
AGE_LABELS = ["0–4", "5–11", "12–17", "18–35", "36–59", "60+"]

AGE_COLORS = [
    plt.colormaps["Blues"].resampled(8)(i + 1) for i in range(6)
]

FEM_COLS = ["0-4 Female","5-11 Female","12-17 Female",
            "18-35 Female","36-59 Female","60+ Female"]
MAL_COLS = ["0-4 Male","5-11 Male","12-17 Male",
            "18-35 Male","36-59 Male","60+ Male"]
ALL_DEMO_COLS = FEM_COLS + MAL_COLS

AGE_TOTAL_COLS   = ["0-4 Total", "5-11 Total", "12-17 Total",
                    "18-35 Total", "36-59 Total", "60+ Total"]

ORIGIN_COLS = [
    "South_Sudan", "DRC", "Sudan", "Eritrea", "Somalia",
    "Burundi", "Rwanda", "Ethiopia", "Other"
]
ORIGIN_LABELS = {
    "South_Sudan": "South Sudan", "DRC": "DR Congo",
    "Sudan": "Sudan", "Eritrea": "Eritrea", "Somalia": "Somalia",
    "Burundi": "Burundi", "Rwanda": "Rwanda", "Ethiopia": "Ethiopia",
    "Other": "Other"
}

# ── Region mapping ─────────────────────────────────────────────────────────
REGION_MAP = {
    # Western (DRC corridor + Kiryandongo)
    "Nakivale":    "Western",
    "Kyangwali":   "Western",
    "Kyaka II":    "Western",
    "Rwamwanja":   "Western",
    "Oruchinga":   "Western",
    "Kiryandongo": "Western",
    # West Nile (South Sudan corridor)
    "Adjumani":    "West Nile",
    "Bidibidi":    "West Nile",
    "Palorinya":   "West Nile",
    "Palabek":     "West Nile",
    "Rhino":       "West Nile",
    "Imvepi":      "West Nile",
    "Lobule":      "West Nile",
    # Central
    "Kampala":     "Central",
}

FOOTER = "Source: UNHCR Uganda — Population Summary by Settlement, Gender & Age Group  |  Author: Josh"

# ── Matplotlib global style ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "sans-serif",
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.grid":        True,
    "grid.color":       GRID,
    "grid.linewidth":   0.5,
})


# ═══════════════════════════════════════════════════════════════════════════
# Data loading
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Load both CSVs, add regions and derived columns."""
    df = pd.read_csv("refugee_population_by_settlement.csv")
    df = df[df["Settlement"] != "Total"].reset_index(drop=True)

    df["Total Female"] = df[FEM_COLS].sum(axis=1)
    df["Total Male"]   = df[MAL_COLS].sum(axis=1)
    df["Region"]       = df["Settlement"].map(REGION_MAP)

    # Derived age brackets
    df["Child_0_17"]   = df["0-4 Total"] + df["5-11 Total"] + df["12-17 Total"]
    df["Adult_18_59"]  = df["18-35 Total"] + df["36-59 Total"]
    df["Youth_18_35"]  = df["18-35 Total"]
    df["Elderly_60plus"] = df["60+ Total"]
    df["School_Age"]   = df["5-11 Total"] + df["12-17 Total"]
    df["Working_Age"]  = df["18-35 Total"] + df["36-59 Total"]
    df["Under_5"]      = df["0-4 Total"]

    # ── Country of origin data ────────────────────────────────────────────
    orig = pd.read_csv("refugee_country_of_origin.csv")
    orig["Region"] = orig["Settlement"].map(REGION_MAP)

    def simpsons(row):
        total = row[ORIGIN_COLS].sum()
        proportions = row[ORIGIN_COLS] / total
        return 1 - (proportions ** 2).sum()
    orig["diversity"] = orig.apply(simpsons, axis=1)

    # Origin dominance: largest single nationality %
    orig["dominance"] = orig[ORIGIN_COLS].max(axis=1) / orig["Total"] * 100

    return df, orig


df, orig = load_data()


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def stamp_footer(fig, y=-0.02):
    fig.text(0.5, y, FOOTER, ha="center", fontsize=7.5, color=MUTED)


def fmt_k(x, _=None):
    return f"{x/1000:.0f}k"


def build_active_columns(gender, age_selected, adult_child):
    """Return list of column names from ALL_DEMO_COLS that pass all filters."""
    cols = []

    # Map age group label → column suffix
    age_to_suffix = {
        "0-4": "0-4", "5-11": "5-11", "12-17": "12-17",
        "18-35": "18-35", "36-59": "36-59", "60+": "60+",
    }

    # Adult vs Child overlay
    child_groups = {"0-4", "5-11", "12-17"}
    adult_groups = {"18-35", "36-59", "60+"}

    effective_ages = set(age_selected)
    if adult_child == "Child (0–17)":
        effective_ages = effective_ages & child_groups
    elif adult_child == "Adult (18+)":
        effective_ages = effective_ages & adult_groups

    for age_label in effective_ages:
        suffix = age_to_suffix[age_label]
        if gender in ("All", "Female"):
            cols.append(f"{suffix} Female")
        if gender in ("All", "Male"):
            cols.append(f"{suffix} Male")

    return cols


def computed_filtered_total(df_, active_cols):
    """Return a copy of df_ with a `Filtered_Total` column from active_cols."""
    d = df_.copy()
    if active_cols:
        d["Filtered_Total"] = d[active_cols].sum(axis=1)
    else:
        d["Filtered_Total"] = 0
    return d


# ═══════════════════════════════════════════════════════════════════════════
# Chart functions — all accept a pre-filtered DataFrame
# ═══════════════════════════════════════════════════════════════════════════

def chart_settlement_totals(df_, total_col="Grand Total"):
    settled = df_.sort_values(total_col, ascending=True)
    colors  = [ACCENT if v == settled[total_col].max() else BLUE
               for v in settled[total_col]]
    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(settled)))
    ax.set_facecolor(BG)
    bars = ax.barh(settled["Settlement"], settled[total_col],
                   color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, settled[total_col]):
        ax.text(bar.get_width() + 1500, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}", va="center", fontsize=9, color=TEXT)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax.set_xlabel("Total population", fontsize=10, color=MUTED)
    ax.set_title("Total refugees per settlement", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_age_pyramid(df_):
    fem_vals = df_[FEM_COLS].sum().values
    mal_vals = df_[MAL_COLS].sum().values
    grand    = df_["Grand Total"].sum()
    y        = np.arange(len(AGE_GROUPS))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor(BG)
    ax.barh(y, [-v for v in fem_vals], color=BLUE, height=0.6,
            edgecolor="none", label="Female")
    ax.barh(y,  mal_vals,               color=TEAL, height=0.6,
            edgecolor="none", label="Male")

    max_val = max(max(fem_vals), max(mal_vals))
    ax.set_xlim(-max_val * 1.18, max_val * 1.18)

    for i, (f, m) in enumerate(zip(fem_vals, mal_vals)):
        ax.text(-f - 6000, i, f"{f/grand*100:.1f}%",
                va="center", ha="right", fontsize=8, color=BLUE)
        ax.text( m + 6000, i, f"{m/grand*100:.1f}%",
                va="center", ha="left",  fontsize=8, color=MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels(AGE_GROUPS, fontsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{abs(x)/1000:.0f}k"))
    ax.axvline(0, color=TEXT, linewidth=0.8)
    ax.set_title("Age & gender pyramid — all settlements", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_age_composition(df_):
    x      = np.arange(len(df_))
    bottom = np.zeros(len(df_))

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor(BG)

    for col, lbl, clr in zip(AGE_TOTAL_COLS, AGE_LABELS, AGE_COLORS):
        ax.bar(x, df_[col], bottom=bottom, label=lbl,
               color=clr, edgecolor="none", width=0.65)
        bottom += df_[col].values

    ax.set_xticks(x)
    ax.set_xticklabels(df_["Settlement"], rotation=35, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax.set_ylabel("Population", fontsize=10, color=MUTED)
    ax.set_title("Age composition — all settlements", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.legend(title="Age group", fontsize=9, title_fontsize=9,
              frameon=False, loc="upper right", ncol=2)
    ax.grid(axis="x", visible=False)
    stamp_footer(fig, y=-0.04)
    plt.tight_layout()
    return fig


def chart_female_vs_male(df_):
    x = np.arange(len(df_))
    w = 0.38

    fig, ax = plt.subplots(figsize=(11, 0.5 + 0.45 * len(df_)))
    ax.set_facecolor(BG)
    ax.bar(x - w/2, df_["Total Female"], width=w, color=BLUE,
           edgecolor="none", label="Female")
    ax.bar(x + w/2, df_["Total Male"],   width=w, color=TEAL,
           edgecolor="none", label="Male")

    ax.set_xticks(x)
    ax.set_xticklabels(df_["Settlement"], rotation=35, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax.set_ylabel("Population", fontsize=10, color=MUTED)
    ax.set_title("Female vs male — all settlements", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="x", visible=False)
    stamp_footer(fig, y=-0.04)
    plt.tight_layout()
    return fig


def chart_age_donut(df_):
    age_totals = [df_[c].sum() for c in AGE_TOTAL_COLS]

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    wedges, texts, autotexts = ax.pie(
        age_totals, labels=AGE_LABELS, autopct="%1.1f%%",
        colors=AGE_COLORS, startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=1.5),
    )
    for t  in texts:     t.set_fontsize(11)
    for at in autotexts: at.set_fontsize(9); at.set_color(TEXT)

    ax.text(0, 0, f"{int(sum(age_totals)):,}\ntotal",
            ha="center", va="center", fontsize=11,
            fontweight="bold", color=TEXT)
    ax.set_title("Overall age-group share", fontsize=13,
                 fontweight="bold", pad=14, color=TEXT)
    stamp_footer(fig, y=0.01)
    plt.tight_layout()
    return fig


def chart_gender_summary(df_):
    total_f = df_["Total Female"].sum()
    total_m = df_["Total Male"].sum()

    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.set_facecolor(BG)
    ax.barh([1, 0], [total_f, total_m],
            color=[BLUE, TEAL], height=0.5, edgecolor="none")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Male", "Female"], fontsize=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M"))
    ax.text(total_f + 5000, 1, f"{total_f/1e6:.2f}M", va="center", fontsize=9, color=BLUE)
    ax.text(total_m + 5000, 0, f"{total_m/1e6:.2f}M", va="center", fontsize=9, color=MUTED)
    ax.set_title("Gender total", fontsize=12, fontweight="bold", pad=6, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    plt.tight_layout()
    return fig


# ── Country-of-origin charts ───────────────────────────────────────────────

def chart_country_of_origin(orig_):
    origin_totals = {c: orig_[c].sum() for c in ORIGIN_COLS}
    sorted_ctry = sorted(origin_totals.items(), key=lambda x: x[1])
    labels = [ORIGIN_LABELS[k] for k, _ in sorted_ctry]
    values = [v for _, v in sorted_ctry]
    colors  = [ACCENT if v == max(values) else BLUE for v in values]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor(BG)
    bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, values):
        pct = val / sum(values) * 100
        ax.text(bar.get_width() + 2000, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}  ({pct:.1f}%)", va="center", fontsize=9, color=TEXT)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax.set_xlabel("Number of refugees", fontsize=10, color=MUTED)
    ax.set_title("Refugees by country of origin", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_nationality_composition(orig_):
    comp = orig_.set_index("Settlement")[ORIGIN_COLS].copy()
    comp = comp.div(comp.sum(axis=1), axis=0) * 100
    comp = comp.sort_values("South_Sudan", ascending=False)
    col_labels = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]

    cmap   = plt.colormaps["tab10"].resampled(len(ORIGIN_COLS))
    colors = [cmap(i) for i in range(len(ORIGIN_COLS))]

    fig, ax = plt.subplots(figsize=(14, 0.5 + 0.45 * len(comp)))
    ax.set_facecolor(BG)
    x = np.arange(len(comp))
    bottom = np.zeros(len(comp))
    for j, (col, lbl) in enumerate(zip(ORIGIN_COLS, col_labels)):
        vals = comp[col].values
        ax.barh(x, vals, left=bottom, height=0.6, color=colors[j],
                edgecolor="none", label=lbl)
        bottom += vals

    ax.set_yticks(x)
    ax.set_yticklabels(comp.index, fontsize=9)
    ax.set_xlabel("% share of settlement population", fontsize=10, color=MUTED)
    ax.set_title("Nationality composition — % share per settlement", fontsize=13,
                 fontweight="bold", pad=10, color=TEXT)
    ax.legend(title="Country of Origin", fontsize=9, title_fontsize=10,
              frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5))
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_heatmap(orig_):
    heat = orig_.set_index("Settlement")[ORIGIN_COLS].copy()
    heat = heat.div(heat.sum(axis=1), axis=0) * 100
    heat = heat.sort_values("South_Sudan", ascending=False)
    col_labels = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]

    fig, ax = plt.subplots(figsize=(12, 0.5 + 0.5 * len(heat)))
    im = ax.imshow(heat.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=100)
    ax.set_xticks(range(len(ORIGIN_COLS)))
    ax.set_xticklabels(col_labels, fontsize=9, rotation=30, ha="right")
    ax.set_yticks(range(len(heat)))
    ax.set_yticklabels(heat.index, fontsize=9)

    for i in range(len(heat)):
        for j in range(len(ORIGIN_COLS)):
            val = heat.values[i, j]
            if val > 1:
                txt_color = "white" if val > 55 else TEXT
                ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                        fontsize=8, color=txt_color)

    plt.colorbar(im, ax=ax, label="% share of settlement population",
                 shrink=0.6, pad=0.02)
    ax.set_title("Nationality Concentration Heatmap — Settlement × Country of Origin",
                 fontsize=12, fontweight="bold", pad=10, color=TEXT)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_diversity_index(orig_):
    div_sorted = orig_.sort_values("diversity", ascending=True)
    norm   = plt.Normalize(div_sorted["diversity"].min(), div_sorted["diversity"].max())
    cmap   = plt.cm.RdYlBu_r
    colors = [cmap(norm(v)) for v in div_sorted["diversity"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(div_sorted)))
    ax.set_facecolor(BG)
    bars = ax.barh(div_sorted["Settlement"], div_sorted["diversity"],
                   color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, div_sorted["diversity"]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9, color=TEXT)
    ax.axvline(0.2, color="#AAAAAA", linewidth=0.8, linestyle="--")
    ax.axvline(0.5, color="#AAAAAA", linewidth=0.8, linestyle="--")
    ax.text(0.2, -0.8, "Low diversity",  fontsize=7.5, color=MUTED, ha="center")
    ax.text(0.5, -0.8, "Moderate",       fontsize=7.5, color=MUTED, ha="center")
    ax.set_xlim(0, 0.85)
    ax.set_xlabel("Simpson's Diversity Index (0 = homogeneous, 1 = fully diverse)",
                  fontsize=9, color=MUTED)
    ax.set_title("Settlement Diversity Index — Nationality Mix",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig, y=-0.03)
    plt.tight_layout()
    return fig


def chart_origin_dominance(orig_):
    """Largest single nationality as % of settlement total."""
    dom_sorted = orig_.sort_values("dominance", ascending=True)
    colors = [ACCENT if v == dom_sorted["dominance"].max() else TEAL
              for v in dom_sorted["dominance"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(dom_sorted)))
    ax.set_facecolor(BG)
    bars = ax.barh(dom_sorted["Settlement"], dom_sorted["dominance"],
                   color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, dom_sorted["dominance"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color=TEXT)
    ax.set_xlim(0, 105)
    ax.set_xlabel("% from largest single nationality", fontsize=10, color=MUTED)
    ax.set_title("Origin dominance — largest nationality share per settlement",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


# ── New demographic insight charts ─────────────────────────────────────────

def chart_youth_bulge(df_):
    """Youth (18-35) as % of total per settlement."""
    d = df_.copy()
    d["Youth_Pct"] = d["Youth_18_35"] / d["Grand Total"] * 100
    d = d.sort_values("Youth_Pct", ascending=True)
    colors = [ACCENT if v == d["Youth_Pct"].max() else BLUE for v in d["Youth_Pct"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(d)))
    ax.set_facecolor(BG)
    bars = ax.barh(d["Settlement"], d["Youth_Pct"], color=colors,
                   height=0.6, edgecolor="none")
    for bar, val in zip(bars, d["Youth_Pct"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color=TEXT)
    ax.set_xlabel("% of settlement population", fontsize=10, color=MUTED)
    ax.set_title("Youth bulge — 18–35 age group as % of settlement",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_child_share(df_):
    """Children (0-17) as % of total per settlement."""
    d = df_.copy()
    d["Child_Pct"] = d["Child_0_17"] / d["Grand Total"] * 100
    d = d.sort_values("Child_Pct", ascending=True)
    colors = [ACCENT if v == d["Child_Pct"].max() else BLUE for v in d["Child_Pct"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(d)))
    ax.set_facecolor(BG)
    bars = ax.barh(d["Settlement"], d["Child_Pct"], color=colors,
                   height=0.6, edgecolor="none")
    for bar, val in zip(bars, d["Child_Pct"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color=TEXT)
    ax.set_xlabel("% of settlement population", fontsize=10, color=MUTED)
    ax.set_title("Child share — under 18 as % of settlement",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_elderly_share(df_):
    """Elderly (60+) as % of total per settlement."""
    d = df_.copy()
    d["Elderly_Pct"] = d["Elderly_60plus"] / d["Grand Total"] * 100
    d = d.sort_values("Elderly_Pct", ascending=True)
    colors = [ACCENT if v == d["Elderly_Pct"].max() else BLUE for v in d["Elderly_Pct"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(d)))
    ax.set_facecolor(BG)
    bars = ax.barh(d["Settlement"], d["Elderly_Pct"], color=colors,
                   height=0.6, edgecolor="none")
    for bar, val in zip(bars, d["Elderly_Pct"]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color=TEXT)
    ax.set_xlabel("% of settlement population", fontsize=10, color=MUTED)
    ax.set_title("Elderly share — 60+ as % of settlement",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_gender_parity(df_):
    """Female % of total per settlement — reference line at 50%."""
    d = df_.copy()
    d["Fem_Pct"] = d["Total Female"] / d["Grand Total"] * 100
    d = d.sort_values("Fem_Pct", ascending=True)
    colors = [BLUE if v >= 50 else TEAL for v in d["Fem_Pct"]]

    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(d)))
    ax.set_facecolor(BG)
    bars = ax.barh(d["Settlement"], d["Fem_Pct"], color=colors,
                   height=0.6, edgecolor="none")
    for bar, val in zip(bars, d["Fem_Pct"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color=TEXT)
    ax.axvline(50, color=TEXT, linewidth=1.2, linestyle="--")
    ax.set_xlabel("% female", fontsize=10, color=MUTED)
    ax.set_title("Gender parity — female % of settlement population",
                 fontsize=13, fontweight="bold", pad=10, color=TEXT)
    ax.tick_params(labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


def chart_ngo_targeting(df_):
    edu_sorted  = df_.sort_values("School_Age",  ascending=True)
    live_sorted = df_.sort_values("Working_Age", ascending=True)
    edu_total   = df_["School_Age"].sum()
    live_total  = df_["Working_Age"].sum()

    fig, (ax_edu, ax_live) = plt.subplots(1, 2, figsize=(16, 0.5 + 0.5 * len(df_)))

    ax_edu.set_facecolor(BG)
    bars_edu = ax_edu.barh(edu_sorted["Settlement"], edu_sorted["School_Age"],
                           color=BLUE, height=0.6, edgecolor="none")
    for bar, val in zip(bars_edu, edu_sorted["School_Age"]):
        pct = val / edu_total * 100
        ax_edu.text(bar.get_width() + 1000, bar.get_y() + bar.get_height() / 2,
                    f"{val:,.0f}  ({pct:.1f}%)", va="center", fontsize=8, color=TEXT)
    ax_edu.set_title("School-Age Children (5–17 yrs)", fontsize=11,
                     fontweight="bold", pad=8, color=TEXT)
    ax_edu.set_xlabel("Number of children", fontsize=9, color=MUTED)
    ax_edu.xaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax_edu.tick_params(labelsize=8)
    ax_edu.grid(axis="x", color=GRID, linewidth=0.5)
    ax_edu.grid(axis="y", visible=False)
    ax_edu.text(0.97, 0.02, f"Total school-age: {edu_total:,.0f}",
                transform=ax_edu.transAxes, ha="right", fontsize=8, color=MUTED,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax_live.set_facecolor(BG)
    bars_live = ax_live.barh(live_sorted["Settlement"], live_sorted["Working_Age"],
                              color=ACCENT, height=0.6, edgecolor="none")
    for bar, val in zip(bars_live, live_sorted["Working_Age"]):
        pct = val / live_total * 100
        ax_live.text(bar.get_width() + 1000, bar.get_y() + bar.get_height() / 2,
                     f"{val:,.0f}  ({pct:.1f}%)", va="center", fontsize=8, color=TEXT)
    ax_live.set_title("Working-Age Adults (18–59 yrs)", fontsize=11,
                      fontweight="bold", pad=8, color=TEXT)
    ax_live.set_xlabel("Number of adults", fontsize=9, color=MUTED)
    ax_live.xaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
    ax_live.tick_params(labelsize=8)
    ax_live.grid(axis="x", color=GRID, linewidth=0.5)
    ax_live.grid(axis="y", visible=False)
    ax_live.text(0.97, 0.02, f"Total working-age: {live_total:,.0f}",
                 transform=ax_live.transAxes, ha="right", fontsize=8, color=MUTED,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor="#CCCCCC", alpha=0.9))

    fig.suptitle("NGO Programme Targeting — Education & Livelihoods Priority Settlements",
                 fontsize=13, fontweight="bold", color=TEXT, y=1.01)
    stamp_footer(fig)
    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Sidebar — all filters
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    try:
        logo = Image.open("Logos/wcc.png")
        st.image(logo, width=120)
    except Exception:
        pass

    st.title("Refugee Dashboard")
    st.caption("Uganda — 31 March 2026")
    st.markdown("---")

    # ── Region ────────────────────────────────────────────────────────────
    st.subheader("Region")
    all_regions = ["Western", "West Nile", "Central"]
    sel_regions = st.multiselect(
        "Select regions:", options=all_regions, default=all_regions,
    )
    # Option A: empty = all
    if not sel_regions:
        sel_regions = all_regions

    # ── Country of origin ─────────────────────────────────────────────────
    st.subheader("Country of Origin")
    sel_origins = st.multiselect(
        "Select origin countries:",
        options=[ORIGIN_LABELS[c] for c in ORIGIN_COLS],
        default=[ORIGIN_LABELS[c] for c in ORIGIN_COLS],
    )
    # Option A: empty = all
    if not sel_origins:
        sel_origins = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]
    label_to_col = {v: k for k, v in ORIGIN_LABELS.items()}
    sel_origin_cols = [label_to_col[l] for l in sel_origins]

    st.markdown("---")

    # ── Gender ────────────────────────────────────────────────────────────
    st.subheader("Gender")
    sel_gender = st.radio(
        "Population to show:", ["All", "Female", "Male"],
        index=0, horizontal=True,
    )

    # ── Age group ─────────────────────────────────────────────────────────
    st.subheader("Age Group")
    sel_ages = st.multiselect(
        "Select age brackets:",
        options=AGE_GROUPS, default=AGE_GROUPS,
    )

    # ── Adult vs Child ────────────────────────────────────────────────────
    st.subheader("Adult vs Child")
    sel_adult_child = st.radio(
        "Focus:", ["All", "Child (0–17)", "Adult (18+)"],
        index=0, horizontal=True,
    )

    st.markdown("---")
    st.caption("Data: UNHCR Uganda / OPM proGres")
    st.caption("Snapshot: 31 March 2026")


# ═══════════════════════════════════════════════════════════════════════════
# Apply filters
# ═══════════════════════════════════════════════════════════════════════════

# 1. Region → filter both dataframes
df_filtered = df[df["Region"].isin(sel_regions)].copy()
orig_filtered = orig[orig["Region"].isin(sel_regions)].copy()

# 2. Country of origin — keep only settlements that have refugees from
#    selected origins
if sel_origin_cols:
    has_origin = orig_filtered[sel_origin_cols].sum(axis=1) > 0
    valid_settlements = orig_filtered.loc[has_origin, "Settlement"].tolist()
    df_filtered = df_filtered[df_filtered["Settlement"].isin(valid_settlements)]
    orig_filtered = orig_filtered[orig_filtered["Settlement"].isin(valid_settlements)]

# 3. Demographic filters — build active column list for age/gender charts
active_cols = build_active_columns(sel_gender, sel_ages, sel_adult_child)

# 4. Compute filtered totals for the demographic-focused view
if active_cols:
    df_filtered["Demo_Total"] = df_filtered[active_cols].sum(axis=1)
else:
    df_filtered["Demo_Total"] = 0

demo_total = df_filtered["Demo_Total"].sum()


# ═══════════════════════════════════════════════════════════════════════════
# KPI metric cards
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("## Key Indicators")

# Row 1 — core demographics
ft_grand  = df_filtered["Grand Total"].sum()
ft_female = df_filtered["Total Female"].sum()
ft_male   = df_filtered["Total Male"].sum()
ft_youth  = df_filtered["Youth_18_35"].sum()
ft_elderly = df_filtered["Elderly_60plus"].sum()
ft_child  = df_filtered["Child_0_17"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Refugees", f"{ft_grand:,.0f}")
k2.metric("Female", f"{ft_female:,.0f}")
k3.metric("Male", f"{ft_male:,.0f}")
k4.metric("Settlements", f"{len(df_filtered)}")
k5.metric("Youth (18–35)", f"{ft_youth:,.0f}",
          delta=f"{ft_youth/ft_grand*100:.1f}%" if ft_grand else None)
k6.metric("Elderly (60+)", f"{ft_elderly:,.0f}",
          delta=f"{ft_elderly/ft_grand*100:.1f}%" if ft_grand else None)

# Row 2 — country of origin
fo_ss  = orig_filtered["South_Sudan"].sum()
fo_drc = orig_filtered["DRC"].sum()
fo_sud = orig_filtered["Sudan"].sum()
fo_other = orig_filtered[ORIGIN_COLS].sum().sum() - fo_ss - fo_drc - fo_sud

o1, o2, o3, o4, o5, o6 = st.columns(6)
o1.metric("South Sudan", f"{fo_ss:,.0f}",
          delta=f"{fo_ss/ft_grand*100:.1f}%" if ft_grand else None)
o2.metric("DR Congo", f"{fo_drc:,.0f}",
          delta=f"{fo_drc/ft_grand*100:.1f}%" if ft_grand else None)
o3.metric("Sudan", f"{fo_sud:,.0f}",
          delta=f"{fo_sud/ft_grand*100:.1f}%" if ft_grand else None)
o4.metric("Other Origins", f"{fo_other:,.0f}",
          delta=f"{fo_other/ft_grand*100:.1f}%" if ft_grand else None)
o5.metric("Children (0–17)", f"{ft_child:,.0f}",
          delta=f"{ft_child/ft_grand*100:.1f}%" if ft_grand else None)
# Demo-total from gender/age filters
o6.metric("Filtered Pop.", f"{demo_total:,.0f}",
          delta=f"{demo_total/ft_grand*100:.1f}% of total" if ft_grand else None)

st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════
# Helper — safe chart display with empty-state fallback
# ═══════════════════════════════════════════════════════════════════════════

def show_chart(chart_fn, df_, empty_msg="No data matches the current filters."):
    """Display a chart or a clean info message if the DataFrame is empty."""
    if len(df_) == 0:
        st.info(empty_msg)
    else:
        st.pyplot(chart_fn(df_))


# ═══════════════════════════════════════════════════════════════════════════
# Tabs
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Age & Gender",
    "Country of Origin",
    "Demographic Insights",
    "Programme Targeting",
])

# ── TAB 1: Overview ───────────────────────────────────────────────────────
with tab1:
    st.markdown("### Settlement Totals & Population Pyramid")

    if len(df_filtered) == 0:
        st.info("No settlements match the current filters.")
    else:
        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.pyplot(chart_settlement_totals(df_filtered))

        with col_right:
            st.pyplot(chart_gender_summary(df_filtered))
            st.pyplot(chart_age_donut(df_filtered))

        st.markdown("---")
        st.pyplot(chart_age_pyramid(df_filtered))

# ── TAB 2: Age & Gender ───────────────────────────────────────────────────
with tab2:
    st.markdown("### Age Composition & Gender Comparison")
    show_chart(chart_age_composition, df_filtered)
    st.markdown("---")
    show_chart(chart_female_vs_male, df_filtered)

# ── TAB 3: Country of Origin ──────────────────────────────────────────────
with tab3:
    if len(orig_filtered) == 0:
        st.info("No settlements match the current filters.")
    else:
        st.markdown("### Country of Origin Distribution")
        col_a, col_b = st.columns([1, 1.5])
        with col_a:
            st.pyplot(chart_country_of_origin(orig_filtered))
        with col_b:
            st.pyplot(chart_diversity_index(orig_filtered))

        st.markdown("---")
        st.markdown("### Origin Dominance")
        st.pyplot(chart_origin_dominance(orig_filtered))

        st.markdown("---")
        st.markdown("### Nationality Composition & Heatmap")
        st.pyplot(chart_nationality_composition(orig_filtered))
        st.markdown("---")
        st.pyplot(chart_heatmap(orig_filtered))

# ── TAB 4: Demographic Insights ───────────────────────────────────────────
with tab4:
    st.markdown("### Demographic Indicators per Settlement")
    show_chart(chart_youth_bulge, df_filtered)
    show_chart(chart_child_share, df_filtered)
    st.markdown("---")
    show_chart(chart_elderly_share, df_filtered)
    show_chart(chart_gender_parity, df_filtered)

# ── TAB 5: Programme Targeting ────────────────────────────────────────────
with tab5:
    st.markdown("### Education & Livelihoods Priority Settlements")
    show_chart(chart_ngo_targeting, df_filtered)

    if len(df_filtered) == 0:
        st.info("No settlements match the current filters.")
    else:
        st.markdown("---")
        st.markdown("### Key Conclusions")

        f_grand   = df_filtered["Grand Total"].sum()
        f_school  = df_filtered["School_Age"].sum()
        f_working = df_filtered["Working_Age"].sum()
        f_under5  = df_filtered["Under_5"].sum()
        f_child   = df_filtered["Child_0_17"].sum()
        f_youth   = df_filtered["Youth_18_35"].sum()
        f_elderly = df_filtered["Elderly_60plus"].sum()

        fo = orig_filtered
        f_ss   = fo["South_Sudan"].sum()
        f_drc  = fo["DRC"].sum()
        f_sud  = fo["Sudan"].sum()
        if len(fo) > 0:
            f_div_most  = fo.loc[fo["diversity"].idxmax(), "Settlement"]
            f_div_least = fo.loc[fo["diversity"].idxmin(), "Settlement"]
            f_dom_most  = fo.loc[fo["dominance"].idxmax(), "Settlement"]
        else:
            f_div_most = f_div_least = f_dom_most = "N/A"

        f_top3_edu  = df_filtered.nlargest(3, "School_Age")[["Settlement", "School_Age"]]
        f_top3_live = df_filtered.nlargest(3, "Working_Age")[["Settlement", "Working_Age"]]
        f_top3_youth = df_filtered.nlargest(3, "Youth_18_35")[["Settlement", "Youth_18_35"]]
        f_top3_child = df_filtered.nlargest(3, "Child_0_17")[["Settlement", "Child_0_17"]]

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("#### Population Overview")
            st.markdown(f"""
            - **Total refugees:** {f_grand:,.0f}
            - **South Sudan:** {f_ss:,.0f} ({f_ss/f_grand*100:.1f}%) &nbsp;|&nbsp;
              **DR Congo:** {f_drc:,.0f} ({f_drc/f_grand*100:.1f}%)
            - **Sudan:** {f_sud:,.0f} ({f_sud/f_grand*100:.1f}%)
            - **Combined top 3:** {(f_ss+f_drc+f_sud)/f_grand*100:.1f}%
            """)

            st.markdown("#### Demographics")
            st.markdown(f"""
            - **Youth (18–35):** {f_youth:,.0f} ({f_youth/f_grand*100:.1f}%)
            - **Children (0–17):** {f_child:,.0f} ({f_child/f_grand*100:.1f}%)
            - **Elderly (60+):** {f_elderly:,.0f} ({f_elderly/f_grand*100:.1f}%)
            """)

            st.markdown("#### Education")
            st.markdown(f"""
            - **School-age children (5–17):** {f_school:,.0f} ({f_school/f_grand*100:.1f}%)
            - **Under-5 (ECD priority):** {f_under5:,.0f}
            """)
            st.markdown("**Top 3 for education:**")
            for _, row in f_top3_edu.iterrows():
                st.markdown(f"- {row['Settlement']}: {row['School_Age']:,.0f} children")

            st.markdown("**Top 3 for child-focused programming:**")
            for _, row in f_top3_child.iterrows():
                st.markdown(f"- {row['Settlement']}: {row['Child_0_17']:,.0f} children (0–17)")

        with col_c2:
            st.markdown("#### Livelihoods")
            st.markdown(f"""
            - **Working-age adults (18–59):** {f_working:,.0f} ({f_working/f_grand*100:.1f}%)
            """)
            st.markdown("**Top 3 for livelihoods:**")
            for _, row in f_top3_live.iterrows():
                st.markdown(f"- {row['Settlement']}: {row['Working_Age']:,.0f} adults")

            st.markdown("**Top 3 for youth employment:**")
            for _, row in f_top3_youth.iterrows():
                st.markdown(f"- {row['Settlement']}: {row['Youth_18_35']:,.0f} youth (18–35)")

            st.markdown("#### Diversity & Dominance")
            st.markdown(f"""
            - **Most diverse:** {f_div_most}
            - **Most homogeneous:** {f_div_least}
            - **Highest single-nationality dominance:** {f_dom_most}
            """)

        st.markdown("---")
        st.caption(FOOTER)


# ═══════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption(
    "Uganda Refugee Population Dashboard — Built with Streamlit. "
    "Data: UNHCR Uganda / OPM proGres Registration System, 31 March 2026. "
    "Author: Josh"
)
