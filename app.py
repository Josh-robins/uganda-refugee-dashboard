"""
Uganda Refugee Population Dashboard — Streamlit Edition
Built from refugee_visualisation (1).ipynb
Data: UNHCR Uganda / OPM proGres — 31 March 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sequential, qualitative
from PIL import Image

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uganda Refugee Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto",
)

# WarChild red styling for region KPI cards
st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        .metric-warchild {
            margin-bottom: 10px !important;
        }
    }
    .metric-warchild {
        background: #D01030;
        color: white;
        padding: 14px 12px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-warchild label {
        color: rgba(255,255,255,0.8);
        font-size: 0.8rem;
        display: block;
        margin-bottom: 2px;
    }
    .metric-warchild .value {
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.3;
    }
    .metric-warchild .sub {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 2px;
    }
    [data-testid="column"] > div > div > div:has(.metric-warchild) {
        padding: 4px !important;
    }

    /* ── Responsive KPI metric sizing — no truncation ──────────────────── */
    [data-testid="stMetricValue"] {
        font-size: clamp(0.75rem, 1.5vw, 1.3rem) !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.6rem, 1.0vw, 0.85rem) !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: clamp(0.6rem, 1.0vw, 0.8rem) !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    /* ── Print optimizations ─────────────────────────────────────────── */
    @media print {
        @page {
            size: landscape;
            margin: 8mm;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0.3rem !important;
        }
        [data-testid="stMetricValue"] {
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: normal !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.65rem !important;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.65rem !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .element-container,
        .stPlotlyChart,
        .stColumn {
            break-inside: avoid;
            page-break-inside: avoid;
        }
        .row-widget.stColumns {
            gap: 4px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ── Brand constants (WarChild-inspired palette) ────────────────────────────
BLUE   = "#D01030"    # WarChild crimson — female bars, primary fills
TEAL   = "#682934"    # Deep burgundy — male bars, secondary fills
ACCENT = "#F05030"    # Bright red-orange — highlights, largest bar
MUTED  = "#888780"

AGE_GROUPS = ["0-4", "5-11", "12-17", "18-35", "36-59", "60+"]
AGE_LABELS = ["0–4", "5–11", "12–17", "18–35", "36–59", "60+"]
AGE_COLORS = sequential.OrRd[3:9]  # 6-step red-orange gradient for age groups

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
    "Nakivale":"Western","Kyangwali":"Western","Kyaka II":"Western",
    "Rwamwanja":"Western","Oruchinga":"Western","Kiryandongo":"Western",
    "Adjumani":"West Nile","Bidibidi":"West Nile","Palorinya":"West Nile",
    "Palabek":"West Nile","Rhino":"West Nile","Imvepi":"West Nile",
    "Lobule":"West Nile","Kampala":"Central",
}


# ═══════════════════════════════════════════════════════════════════════════
# Data loading
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    df = pd.read_csv("refugee_population_by_settlement.csv")
    df = df[df["Settlement"] != "Total"].reset_index(drop=True)

    df["Total Female"] = df[FEM_COLS].sum(axis=1)
    df["Total Male"]   = df[MAL_COLS].sum(axis=1)
    df["Region"]       = df["Settlement"].map(REGION_MAP)

    df["Child_0_17"]    = df["0-4 Total"] + df["5-11 Total"] + df["12-17 Total"]
    df["Adult_18_59"]   = df["18-35 Total"] + df["36-59 Total"]
    df["Youth_18_35"]   = df["18-35 Total"]
    df["Elderly_60plus"] = df["60+ Total"]
    df["School_Age"]    = df["5-11 Total"] + df["12-17 Total"]
    df["Working_Age"]   = df["18-35 Total"] + df["36-59 Total"]
    df["Under_5"]       = df["0-4 Total"]

    orig = pd.read_csv("refugee_country_of_origin.csv")
    orig["Region"] = orig["Settlement"].map(REGION_MAP)

    def simpsons(row):
        total = row[ORIGIN_COLS].sum()
        proportions = row[ORIGIN_COLS] / total
        return 1 - (proportions ** 2).sum()
    orig["diversity"] = orig.apply(simpsons, axis=1)
    orig["dominance"] = orig[ORIGIN_COLS].max(axis=1) / orig["Total"] * 100

    return df, orig


df, orig = load_data()


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def chart_template():
    """Return plotly template matching Streamlit's current theme."""
    return "plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"


def mut_color():
    return "#AAAAAA" if st.get_option("theme.base") == "dark" else MUTED


def hover_style():
    """Return hoverlabel dict that adapts to light/dark theme."""
    if st.get_option("theme.base") == "dark":
        return dict(bgcolor="#2d2d2d", font=dict(color="#FFFFFF", size=12))
    return dict(bgcolor="#FFFFFF", font=dict(color="#2C2C2A", size=12))


def build_active_columns(gender, age_selected, adult_child):
    """Return list of column names from ALL_DEMO_COLS that pass all filters."""
    cols = []
    age_to_suffix = {
        "0-4": "0-4", "5-11": "5-11", "12-17": "12-17",
        "18-35": "18-35", "36-59": "36-59", "60+": "60+",
    }
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


# ═══════════════════════════════════════════════════════════════════════════
# Chart functions — all return Plotly figures
# ═══════════════════════════════════════════════════════════════════════════

def chart_settlement_totals(df_, total_col="Grand Total"):
    settled = df_.sort_values(total_col, ascending=True)
    colors  = [ACCENT if v == settled[total_col].max() else BLUE
               for v in settled[total_col]]

    fig = go.Figure(go.Bar(
        x=settled[total_col],
        y=settled["Settlement"],
        orientation="h",
        marker_color=colors,
        text=settled[total_col].apply(lambda v: f"{v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Total refugees per settlement", font=dict(size=16)),
        xaxis=dict(title="Total population", title_font=dict(color=mut_color()),
                   tickformat=",", gridcolor="#D3D1C7"),
        yaxis=dict(categoryorder="array", categoryarray=settled["Settlement"].tolist()),
        template=chart_template(),
        height=200 + 35 * len(settled),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_age_pyramid(df_):
    fem_vals = df_[FEM_COLS].sum().values
    mal_vals = df_[MAL_COLS].sum().values
    grand    = df_["Grand Total"].sum()

    pcts_f = [f / grand * 100 for f in fem_vals]
    pcts_m = [m / grand * 100 for m in mal_vals]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=AGE_LABELS, x=-fem_vals, name="\u2640 Female", orientation="h",
        marker_color=BLUE,
        hovertemplate="%{y}<br>Female: %{customdata:,.0f} (%{x:,.0f})<extra></extra>",
        customdata=fem_vals,
        text=[f"{p:.1f}%" for p in pcts_f],
        textposition="outside", textfont=dict(color=BLUE, size=9),
    ))
    fig.add_trace(go.Bar(
        y=AGE_LABELS, x=mal_vals, name="\u2642 Male", orientation="h",
        marker_color=TEAL,
        hovertemplate="%{y}<br>Male: %{customdata:,.0f} (%{x:,.0f})<extra></extra>",
        customdata=mal_vals,
        text=[f"{p:.1f}%" for p in pcts_m],
        textposition="outside", textfont=dict(color=mut_color(), size=9),
    ))

    max_val = max(max(fem_vals), max(mal_vals))
    tick_vals = []
    step = 50000
    start = -( (max_val // step) + 1 ) * step
    for v in range(int(start), int(max_val * 1.18) + step, step):
        tick_vals.append(v)

    fig.update_layout(
        barmode="overlay",
        title=dict(text="Age & gender pyramid — all settlements",
                   font=dict(size=16)),
        xaxis=dict(
            title="Population", title_font=dict(color=mut_color()),
            tickmode="array",
            tickvals=tick_vals,
            ticktext=[f"{abs(v)/1000:.0f}k" for v in tick_vals],
            gridcolor="#D3D1C7",
            range=[-max_val * 1.18, max_val * 1.18],
        ),
        yaxis=dict(categoryorder="array", categoryarray=AGE_LABELS[::-1]),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
        template=chart_template(),
        height=400,
        margin=dict(l=10, r=30, t=50, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_age_composition(df_):
    fig = go.Figure()
    for col, lbl, clr in zip(AGE_TOTAL_COLS, AGE_LABELS, AGE_COLORS):
        fig.add_trace(go.Bar(
            x=df_["Settlement"], y=df_[col], name=lbl,
            marker_color=clr,
            hovertemplate="Settlement: %{x}<br>" + lbl + ": %{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=dict(text="Age composition — all settlements",
                   font=dict(size=16)),
        xaxis=dict(title="", tickangle=-35),
        yaxis=dict(title="Population", title_font=dict(color=mut_color()),
                   tickformat=","),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        template=chart_template(),
        height=400,
        margin=dict(l=10, r=20, t=50, b=60),
        hoverlabel=hover_style(),
    )
    return fig


def chart_female_vs_male(df_):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_["Settlement"], y=df_["Total Female"], name="\u2640 Female",
        marker_color=BLUE,
        hovertemplate="Settlement: %{x}<br>Female: %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df_["Settlement"], y=df_["Total Male"], name="\u2642 Male",
        marker_color=TEAL,
        hovertemplate="Settlement: %{x}<br>Male: %{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="Female vs male — all settlements",
                   font=dict(size=16)),
        xaxis=dict(title="", tickangle=-35),
        yaxis=dict(title="Population", title_font=dict(color=mut_color()),
                   tickformat=","),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
        template=chart_template(),
        height=200 + 35 * len(df_),
        margin=dict(l=10, r=20, t=40, b=60),
        hoverlabel=hover_style(),
    )
    return fig


def chart_age_donut(df_):
    age_totals = [df_[c].sum() for c in AGE_TOTAL_COLS]

    fig = go.Figure(go.Pie(
        values=age_totals, labels=AGE_LABELS,
        marker=dict(colors=AGE_COLORS),
        hole=0.45,
        textinfo="percent+label",
        textfont=dict(size=11),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        title=dict(text="Overall age-group share", font=dict(size=15)),
        template=chart_template(),
        height=350, width=350,
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=hover_style(),
    )
    return fig


# WarChild-inspired red palette for the regional breakdown
WARCHILD_REDS = ["#D01030", "#682934", "#F05030"]

def chart_regional_pie(df_):
    """Donut chart — population share by region."""
    grouped = df_.groupby("Region")["Grand Total"].sum().reset_index()
    region_order = ["Western", "West Nile", "Central"]
    grouped["Region"] = pd.Categorical(grouped["Region"], categories=region_order, ordered=True)
    grouped = grouped.sort_values("Region")

    fig = go.Figure(go.Pie(
        values=grouped["Grand Total"], labels=grouped["Region"],
        marker=dict(colors=WARCHILD_REDS),
        hole=0.45,
        textinfo="percent+label",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Population: %{value:,.0f} (%{percent})<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        title=dict(text="Regional population breakdown", font=dict(size=15)),
        template=chart_template(),
        height=350, width=350,
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=hover_style(),
    )
    return fig


def chart_gender_summary(df_):
    total_f = df_["Total Female"].sum()
    total_m = df_["Total Male"].sum()

    fig = go.Figure(go.Bar(
        x=[total_f, total_m],
        y=["\u2640 Female", "\u2642 Male"],
        orientation="h",
        marker_color=[BLUE, TEAL],
        text=[f"{total_f/1e6:.2f}M", f"{total_m/1e6:.2f}M"],
        textposition="outside",
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Gender total", font=dict(size=14)),
        xaxis=dict(visible=False),
        yaxis=dict(categoryorder="array", categoryarray=["\u2642 Male", "\u2640 Female"]),
        template=chart_template(),
        height=130,
        margin=dict(l=10, r=20, t=30, b=10),
        showlegend=False,
        hoverlabel=hover_style(),
    )
    return fig


# ── Country-of-origin charts ───────────────────────────────────────────────

def chart_country_of_origin(orig_):
    origin_totals = {c: orig_[c].sum() for c in ORIGIN_COLS}
    sorted_ctry = sorted(origin_totals.items(), key=lambda x: x[1])
    labels = [ORIGIN_LABELS[k] for k, _ in sorted_ctry]
    values = [v for _, v in sorted_ctry]
    grand  = sum(values)
    colors = [ACCENT if v == max(values) else BLUE for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors,
        text=[f"{v:,.0f} ({v/grand*100:.1f}%)" for v in values],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Refugees: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Refugees by country of origin",
                   font=dict(size=16)),
        xaxis=dict(title="Number of refugees", title_font=dict(color=mut_color()),
                   tickformat=",", gridcolor="#D3D1C7"),
        template=chart_template(),
        height=350,
        margin=dict(l=15, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_nationality_composition(orig_):
    comp = orig_.set_index("Settlement")[ORIGIN_COLS].copy()
    comp = comp.div(comp.sum(axis=1), axis=0) * 100
    comp = comp.sort_values("South_Sudan", ascending=False)
    col_labels = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]

    colors = qualitative.T10[:len(ORIGIN_COLS)]

    fig = go.Figure()
    for j, (col, lbl) in enumerate(zip(ORIGIN_COLS, col_labels)):
        fig.add_trace(go.Bar(
            y=comp.index, x=comp[col].values, name=lbl, orientation="h",
            marker_color=colors[j],
            hovertemplate="%{y}<br>" + lbl + ": %{x:.1f}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=dict(text="Nationality composition — % share per settlement",
                   font=dict(size=15)),
        xaxis=dict(title="% share of settlement population",
                   title_font=dict(color=mut_color()), ticksuffix="%"),
        legend=dict(font=dict(size=9), orientation="v",
                    x=1.02, xanchor="left", y=0.5),
        template=chart_template(),
        height=200 + 35 * len(comp),
        margin=dict(l=10, r=130, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_heatmap(orig_):
    heat = orig_.set_index("Settlement")[ORIGIN_COLS].copy()
    heat = heat.div(heat.sum(axis=1), axis=0) * 100
    heat = heat.sort_values("South_Sudan", ascending=False)
    col_labels = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]

    fig = go.Figure(go.Heatmap(
        z=heat.values,
        x=col_labels,
        y=heat.index,
        colorscale="YlOrRd",
        zmin=0, zmax=100,
        text=np.round(heat.values, 0).astype(int) if (heat.values > 1).any() else heat.values,
        texttemplate="%{text}%",
        textfont=dict(size=8),
        hovertemplate=(
            "Settlement: %{y}<br>"
            "Country: %{x}<br>"
            "Share: %{z:.1f}%<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=dict(
            text="Nationality Concentration Heatmap — Settlement × Country of Origin",
            font=dict(size=15),
        ),
        xaxis=dict(title="", tickangle=-30),
        yaxis=dict(title=""),
        template=chart_template(),
        height=200 + 40 * len(heat),
        margin=dict(l=10, r=30, t=40, b=50),
        hoverlabel=hover_style(),
    )
    return fig


def chart_diversity_index(orig_):
    div_sorted = orig_.sort_values("diversity", ascending=True)

    norm_min = div_sorted["diversity"].min()
    norm_max = div_sorted["diversity"].max()
    norm_vals = (div_sorted["diversity"] - norm_min) / (norm_max - norm_min) if norm_max > norm_min else [0.5] * len(div_sorted)
    colors = [f"rgb({int(255*v)},{int(155*(1-v))},{int(55*(1-v))})" for v in norm_vals]

    fig = go.Figure(go.Bar(
        x=div_sorted["diversity"],
        y=div_sorted["Settlement"],
        orientation="h",
        marker_color=colors,
        text=div_sorted["diversity"].apply(lambda v: f"{v:.3f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Diversity: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Settlement Diversity Index — Nationality Mix",
                   font=dict(size=16)),
        xaxis=dict(
            title="Simpson's Diversity Index (0 = homogeneous, 1 = fully diverse)",
            title_font=dict(color=mut_color(), size=10),
            range=[0, 0.85], gridcolor="#D3D1C7",
        ),
        template=chart_template(),
        height=200 + 35 * len(div_sorted),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    # Reference lines
    fig.add_vline(x=0.2, line=dict(dash="dash", color="#AAAAAA", width=1))
    fig.add_vline(x=0.5, line=dict(dash="dash", color="#AAAAAA", width=1))
    fig.add_annotation(x=0.2, y=-0.02, text="Low diversity",
                       showarrow=False, font=dict(size=9, color=mut_color()),
                       xref="x", yref="paper")
    fig.add_annotation(x=0.5, y=-0.02, text="Moderate",
                       showarrow=False, font=dict(size=9, color=mut_color()),
                       xref="x", yref="paper")
    return fig


def chart_origin_dominance(orig_):
    dom_sorted = orig_.sort_values("dominance", ascending=True)
    colors = [ACCENT if v == dom_sorted["dominance"].max() else TEAL
              for v in dom_sorted["dominance"]]

    fig = go.Figure(go.Bar(
        x=dom_sorted["dominance"],
        y=dom_sorted["Settlement"],
        orientation="h",
        marker_color=colors,
        text=dom_sorted["dominance"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Dominant nationality: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Origin dominance — largest nationality share per settlement",
                   font=dict(size=16)),
        xaxis=dict(
            title="% from largest single nationality",
            title_font=dict(color=mut_color()),
            range=[0, 105], gridcolor="#D3D1C7",
        ),
        template=chart_template(),
        height=200 + 35 * len(dom_sorted),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


# ── Demographic insight charts ─────────────────────────────────────────────

def chart_youth_bulge(df_):
    d = df_.copy()
    d["Pct"] = d["Youth_18_35"] / d["Grand Total"] * 100
    d = d.sort_values("Pct", ascending=True)
    colors = [ACCENT if v == d["Pct"].max() else BLUE for v in d["Pct"]]

    fig = go.Figure(go.Bar(
        x=d["Pct"], y=d["Settlement"], orientation="h",
        marker_color=colors,
        text=d["Pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Youth (18-35): %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Youth bulge — 18–35 age group as % of settlement",
                   font=dict(size=15)),
        xaxis=dict(title="% of settlement population",
                   title_font=dict(color=mut_color()), gridcolor="#D3D1C7"),
        template=chart_template(),
        height=200 + 35 * len(d),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_child_share(df_):
    d = df_.copy()
    d["Pct"] = d["Child_0_17"] / d["Grand Total"] * 100
    d = d.sort_values("Pct", ascending=True)
    colors = [ACCENT if v == d["Pct"].max() else BLUE for v in d["Pct"]]

    fig = go.Figure(go.Bar(
        x=d["Pct"], y=d["Settlement"], orientation="h",
        marker_color=colors,
        text=d["Pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Children (0-17): %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Child share — under 18 as % of settlement",
                   font=dict(size=15)),
        xaxis=dict(title="% of settlement population",
                   title_font=dict(color=mut_color()), gridcolor="#D3D1C7"),
        template=chart_template(),
        height=200 + 35 * len(d),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_elderly_share(df_):
    d = df_.copy()
    d["Pct"] = d["Elderly_60plus"] / d["Grand Total"] * 100
    d = d.sort_values("Pct", ascending=True)
    colors = [ACCENT if v == d["Pct"].max() else BLUE for v in d["Pct"]]

    fig = go.Figure(go.Bar(
        x=d["Pct"], y=d["Settlement"], orientation="h",
        marker_color=colors,
        text=d["Pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Elderly (60+): %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Elderly share — 60+ as % of settlement",
                   font=dict(size=15)),
        xaxis=dict(title="% of settlement population",
                   title_font=dict(color=mut_color()), gridcolor="#D3D1C7"),
        template=chart_template(),
        height=200 + 35 * len(d),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    return fig


def chart_gender_parity(df_):
    d = df_.copy()
    d["Pct"] = d["Total Female"] / d["Grand Total"] * 100
    d = d.sort_values("Pct", ascending=True)
    colors = [BLUE if v >= 50 else TEAL for v in d["Pct"]]

    fig = go.Figure(go.Bar(
        x=d["Pct"], y=d["Settlement"], orientation="h",
        marker_color=colors,
        text=d["Pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Female share: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Gender parity — female % of settlement population",
                   font=dict(size=15)),
        xaxis=dict(title="% female", title_font=dict(color=mut_color()),
                   gridcolor="#D3D1C7"),
        template=chart_template(),
        height=200 + 35 * len(d),
        margin=dict(l=10, r=30, t=40, b=30),
        hoverlabel=hover_style(),
    )
    fig.add_vline(x=50, line=dict(dash="dash", color="#888888", width=1.5))
    return fig


def chart_ngo_targeting(df_):
    edu_sorted  = df_.sort_values("School_Age",  ascending=True)
    live_sorted = df_.sort_values("Working_Age", ascending=True)
    edu_total   = df_["School_Age"].sum()
    live_total  = df_["Working_Age"].sum()

    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("School-Age Children (5-17 yrs)",
                                        "Working-Age Adults (18-59 yrs)"),
                        horizontal_spacing=0.12)

    # Education
    fig.add_trace(go.Bar(
        x=edu_sorted["School_Age"], y=edu_sorted["Settlement"], orientation="h",
        marker_color=BLUE, showlegend=False,
        text=[f"{v:,.0f} ({v/edu_total*100:.1f}%)" for v in edu_sorted["School_Age"]],
        textposition="outside", textfont=dict(size=8),
        hovertemplate="%{y}<br>Children: %{x:,.0f}<extra></extra>",
    ), row=1, col=1)

    # Livelihoods
    fig.add_trace(go.Bar(
        x=live_sorted["Working_Age"], y=live_sorted["Settlement"], orientation="h",
        marker_color=ACCENT, showlegend=False,
        text=[f"{v:,.0f} ({v/live_total*100:.1f}%)" for v in live_sorted["Working_Age"]],
        textposition="outside", textfont=dict(size=8),
        hovertemplate="%{y}<br>Adults: %{x:,.0f}<extra></extra>",
    ), row=1, col=2)

    fig.update_layout(
        title=dict(
            text="NGO Programme Targeting — Education & Livelihoods Priority Settlements",
            font=dict(size=15), y=0.98,
        ),
        template=chart_template(),
        height=200 + 35 * len(df_),
        margin=dict(l=10, r=30, t=50, b=30),
        hoverlabel=hover_style(),
    )
    fig.update_xaxes(title="Number of children", title_font=dict(color=mut_color(), size=10),
                     tickformat=",", row=1, col=1)
    fig.update_xaxes(title="Number of adults", title_font=dict(color=mut_color(), size=10),
                     tickformat=",", row=1, col=2)

    for i in range(1, 3):
        fig.update_yaxes(row=1, col=i, tickfont=dict(size=9))

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Safe chart display with empty-state fallback
# ═══════════════════════════════════════════════════════════════════════════

def show_chart(fig, len_df, empty_msg="No data matches the current filters."):
    """Display a Plotly chart with no mode bar (no zoom/pan to confuse users)."""
    if len_df == 0:
        st.info(empty_msg)
    else:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Sidebar — all filters ──────────────────────────────────────────────────

with st.sidebar:
    # Logo with dark-mode support (CSS inverts for dark theme)
    try:
        #logo = Image.open("Logos/wcc.jpg")
        logo = Image.open("Logos/canada.png")
        #
        st.image(logo, width=110)
    except Exception:
        pass

    st.title("Refugee Dashboard")
    st.caption("Uganda — 31 March 2026")
    st.markdown("---")

    st.subheader("Region")
    all_regions = ["Western", "West Nile", "Central"]
    sel_regions = st.multiselect(
        "Select regions:", options=all_regions, default=all_regions,
    )
    if not sel_regions:
        sel_regions = all_regions

    st.subheader("Country of Origin")
    sel_origins = st.multiselect(
        "Select origin countries:",
        options=[ORIGIN_LABELS[c] for c in ORIGIN_COLS],
        default=[ORIGIN_LABELS[c] for c in ORIGIN_COLS],
    )
    if not sel_origins:
        sel_origins = [ORIGIN_LABELS[c] for c in ORIGIN_COLS]
    label_to_col = {v: k for k, v in ORIGIN_LABELS.items()}
    sel_origin_cols = [label_to_col[l] for l in sel_origins]

    st.markdown("---")

    st.subheader("Gender")
    sel_gender = st.radio(
        "Population to show:", ["All", "Female", "Male"],
        index=0, horizontal=True,
    )

    st.subheader("Age Group")
    sel_ages = st.multiselect(
        "Select age brackets:", options=AGE_GROUPS, default=AGE_GROUPS,
    )

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

df_filtered = df[df["Region"].isin(sel_regions)].copy()
orig_filtered = orig[orig["Region"].isin(sel_regions)].copy()

if sel_origin_cols:
    has_origin = orig_filtered[sel_origin_cols].sum(axis=1) > 0
    valid_settlements = orig_filtered.loc[has_origin, "Settlement"].tolist()
    df_filtered = df_filtered[df_filtered["Settlement"].isin(valid_settlements)]
    orig_filtered = orig_filtered[orig_filtered["Settlement"].isin(valid_settlements)]

    # Zero out deselected origin columns so they disappear from charts
    deselected = [c for c in ORIGIN_COLS if c not in sel_origin_cols]
    if deselected:
        orig_filtered[deselected] = 0
    # Recompute Total, diversity and dominance from selected origins only
    orig_filtered["Total"] = orig_filtered[sel_origin_cols].sum(axis=1)
    def filter_simpsons(row):
        total = row[sel_origin_cols].sum()
        if total == 0:
            return 0
        proportions = row[sel_origin_cols] / total
        return 1 - (proportions ** 2).sum()
    orig_filtered["diversity"] = orig_filtered.apply(filter_simpsons, axis=1)
    orig_filtered["dominance"] = (
        orig_filtered[sel_origin_cols].max(axis=1) / orig_filtered["Total"] * 100
    )

active_cols = build_active_columns(sel_gender, sel_ages, sel_adult_child)

# Gender/age cascade — override standard columns with filtered values
if active_cols and sel_gender in ("Female", "Male"):
    df_filtered["Grand Total"] = df_filtered[active_cols].sum(axis=1)
    df_filtered["Total Female"] = df_filtered[[c for c in active_cols if c in FEM_COLS]].sum(axis=1)
    df_filtered["Total Male"]   = df_filtered[[c for c in active_cols if c in MAL_COLS]].sum(axis=1)

    for age_label in ["0-4", "5-11", "12-17", "18-35", "36-59", "60+"]:
        f_col = f"{age_label} Female"
        m_col = f"{age_label} Male"
        age_active = [c for c in [f_col, m_col] if c in active_cols]
        df_filtered[f"{age_label} Total"] = (
            df_filtered[age_active].sum(axis=1) if age_active else 0
        )

    df_filtered["Child_0_17"]    = df_filtered["0-4 Total"] + df_filtered["5-11 Total"] + df_filtered["12-17 Total"]
    df_filtered["Youth_18_35"]   = df_filtered["18-35 Total"]
    df_filtered["Elderly_60plus"] = df_filtered["60+ Total"]
    df_filtered["School_Age"]    = df_filtered["5-11 Total"] + df_filtered["12-17 Total"]
    df_filtered["Working_Age"]   = df_filtered["18-35 Total"] + df_filtered["36-59 Total"]
    df_filtered["Under_5"]       = df_filtered["0-4 Total"]

if active_cols:
    df_filtered["Demo_Total"] = df_filtered[active_cols].sum(axis=1)
else:
    df_filtered["Demo_Total"] = 0

demo_total = df_filtered["Demo_Total"].sum()

# Scale demographic totals to match the origin filter
# The age/gender CSV has no origin breakdown, so we proportionally scale
# each settlement's demographics by the share coming from selected origins.
is_origin_filtered = len(sel_origin_cols) < len(ORIGIN_COLS)
if is_origin_filtered and len(df_filtered) > 0 and len(orig_filtered) > 0:
    merge_s = orig_filtered[["Settlement", "Total"]].set_index("Settlement")["Total"]
    df_filtered = df_filtered.join(merge_s, on="Settlement", rsuffix="_o")
    factor = (df_filtered["Total"] / df_filtered["Grand Total"]).fillna(0).clip(0, 1)
    demo_cols_to_scale = [
        "Grand Total", "Total Female", "Total Male",
        "Child_0_17", "Youth_18_35", "Elderly_60plus",
        "School_Age", "Working_Age", "Under_5",
        "0-4 Total", "5-11 Total", "12-17 Total",
        "18-35 Total", "36-59 Total", "60+ Total",
    ]
    for col in demo_cols_to_scale:
        if col in df_filtered.columns:
            df_filtered[col] = (df_filtered[col] * factor).round(0)
    df_filtered.drop(columns=["Total"], inplace=True)


# ═══════════════════════════════════════════════════════════════════════════
# KPI metric cards
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    "# Uganda Refugee Settlement Dashboard  \n"
    "Population overview by settlement, gender, age group and country of origin — "
    "UNHCR Uganda / OPM proGres, 31 March 2026"
)
st.markdown("## Key Indicators")

ft_grand   = df_filtered["Grand Total"].sum()
ft_female  = df_filtered["Total Female"].sum()
ft_male    = df_filtered["Total Male"].sum()
ft_youth   = df_filtered["Youth_18_35"].sum()
ft_elderly = df_filtered["Elderly_60plus"].sum()
ft_child   = df_filtered["Child_0_17"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Refugees", f"{ft_grand:,.0f}")
k2.metric("\u2640 Female", f"{ft_female:,.0f}",
          delta=f"{ft_female/ft_grand*100:.1f}%" if ft_grand else None)
k3.metric("\u2642 Male", f"{ft_male:,.0f}",
          delta=f"{ft_male/ft_grand*100:.1f}%" if ft_grand else None)
k4.metric("Settlements", f"{len(df_filtered)}")
k5.metric("Youth (18-35)", f"{ft_youth:,.0f}",
          delta=f"{ft_youth/ft_grand*100:.1f}%" if ft_grand else None)
k6.metric("Elderly (60+)", f"{ft_elderly:,.0f}",
          delta=f"{ft_elderly/ft_grand*100:.1f}%" if ft_grand else None)

fo_ss   = orig_filtered["South_Sudan"].sum()
fo_drc  = orig_filtered["DRC"].sum()
fo_sud  = orig_filtered["Sudan"].sum()
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
o5.metric("Children (0-17)", f"{ft_child:,.0f}",
          delta=f"{ft_child/ft_grand*100:.1f}%" if ft_grand else None)
o6.metric("Filtered Pop.", f"{demo_total:,.0f}",
          delta=f"{demo_total/ft_grand*100:.1f}% of total" if ft_grand else None)

st.markdown("---")

# ── Region-level KPIs (WarChild red) ──────────────────────────────────────
if len(df_filtered) > 0:
    region_totals = df_filtered.groupby("Region")["Grand Total"].sum()
    region_settlements = df_filtered.groupby("Region")["Settlement"].nunique()
    cols = st.columns(3)
    for i, region in enumerate(["Western", "West Nile", "Central"]):
        total = region_totals.get(region, 0)
        n_sett = region_settlements.get(region, 0)
        with cols[i]:
            st.markdown(
                f"""
                <div class="metric-warchild">
                    <label>{region}</label>
                    <div class="value">{total:,.0f}</div>
                    <div class="sub">{n_sett} settlement{'s' if n_sett != 1 else ''}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")

# ── Download filtered data ─────────────────────────────────────────────
csv_data = df_filtered.to_csv(index=False).encode("utf-8") if len(df_filtered) > 0 else b""
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="Download filtered data (CSV)",
    data=csv_data,
    file_name="refugee_filtered.csv",
    mime="text/csv",
    disabled=len(df_filtered) == 0,
)


# ═══════════════════════════════════════════════════════════════════════════
# Tabs
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Age & Gender", "Country of Origin",
    "Demographic Insights", "Programme Targeting",
])

# ── TAB 1: Overview ───────────────────────────────────────────────────────
with tab1:
    st.markdown("### Settlement Totals & Population Pyramid")
    if len(df_filtered) == 0:
        st.info("No settlements match the current filters.")
    else:
        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            show_chart(chart_settlement_totals(df_filtered), len(df_filtered))
        with col_right:
            show_chart(chart_gender_summary(df_filtered), len(df_filtered))
            r1, r2 = st.columns(2)
            with r1:
                show_chart(chart_regional_pie(df_filtered), len(df_filtered))
            with r2:
                show_chart(chart_age_donut(df_filtered), len(df_filtered))
        st.markdown("---")
        show_chart(chart_age_pyramid(df_filtered), len(df_filtered))

# ── TAB 2: Age & Gender ───────────────────────────────────────────────────
with tab2:
    st.markdown("### Age Composition & Gender Comparison")
    show_chart(chart_age_composition(df_filtered), len(df_filtered))
    st.markdown("---")
    show_chart(chart_female_vs_male(df_filtered), len(df_filtered))

# ── TAB 3: Country of Origin ──────────────────────────────────────────────
with tab3:
    if len(orig_filtered) == 0:
        st.info("No settlements match the current filters.")
    else:
        st.markdown("### Country of Origin Distribution")
        col_a, col_b = st.columns([1, 1.5])
        with col_a:
            show_chart(chart_country_of_origin(orig_filtered), len(orig_filtered))
        with col_b:
            show_chart(chart_diversity_index(orig_filtered), len(orig_filtered))
        st.markdown("---")
        st.markdown("### Origin Dominance")
        show_chart(chart_origin_dominance(orig_filtered), len(orig_filtered))
        st.markdown("---")
        st.markdown("### Nationality Composition & Heatmap")
        show_chart(chart_nationality_composition(orig_filtered), len(orig_filtered))
        st.markdown("---")
        show_chart(chart_heatmap(orig_filtered), len(orig_filtered))

# ── TAB 4: Demographic Insights ───────────────────────────────────────────
with tab4:
    st.markdown("### Demographic Indicators per Settlement")
    show_chart(chart_youth_bulge(df_filtered), len(df_filtered))
    show_chart(chart_child_share(df_filtered), len(df_filtered))
    st.markdown("---")
    show_chart(chart_elderly_share(df_filtered), len(df_filtered))
    show_chart(chart_gender_parity(df_filtered), len(df_filtered))

# ── TAB 5: Programme Targeting ────────────────────────────────────────────
with tab5:
    st.markdown("### Education & Livelihoods Priority Settlements")
    show_chart(chart_ngo_targeting(df_filtered), len(df_filtered))

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

        f_top3_edu   = df_filtered.nlargest(3, "School_Age")[["Settlement", "School_Age"]]
        f_top3_live  = df_filtered.nlargest(3, "Working_Age")[["Settlement", "Working_Age"]]
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
            - **Youth (18-35):** {f_youth:,.0f} ({f_youth/f_grand*100:.1f}%)
            - **Children (0-17):** {f_child:,.0f} ({f_child/f_grand*100:.1f}%)
            - **Elderly (60+):** {f_elderly:,.0f} ({f_elderly/f_grand*100:.1f}%)
            """)
            st.markdown("#### Education")
            st.markdown(f"""
            - **School-age children (5-17):** {f_school:,.0f} ({f_school/f_grand*100:.1f}%)
            - **Under-5 (ECD priority):** {f_under5:,.0f}
            """)
            st.markdown("**Top 3 for education:**")
            for _, r in f_top3_edu.iterrows():
                st.markdown(f"- {r['Settlement']}: {r['School_Age']:,.0f} children")
            st.markdown("**Top 3 for child-focused programming:**")
            for _, r in f_top3_child.iterrows():
                st.markdown(f"- {r['Settlement']}: {r['Child_0_17']:,.0f} children (0-17)")

        with col_c2:
            st.markdown("#### Livelihoods")
            st.markdown(f"""
            - **Working-age adults (18-59):** {f_working:,.0f} ({f_working/f_grand*100:.1f}%)
            """)
            st.markdown("**Top 3 for livelihoods:**")
            for _, r in f_top3_live.iterrows():
                st.markdown(f"- {r['Settlement']}: {r['Working_Age']:,.0f} adults")
            st.markdown("**Top 3 for youth employment:**")
            for _, r in f_top3_youth.iterrows():
                st.markdown(f"- {r['Settlement']}: {r['Youth_18_35']:,.0f} youth (18-35)")
            st.markdown("#### Diversity & Dominance")
            st.markdown(f"""
            - **Most diverse:** {f_div_most}
            - **Most homogeneous:** {f_div_least}
            - **Highest single-nationality dominance:** {f_dom_most}
            """)

        st.markdown("---")
        st.caption(
            "Source: UNHCR Uganda — Population Summary by Settlement, "
            "Gender & Age Group  |  Author: Josh"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption(
    "Uganda Refugee Population Dashboard — Built with Streamlit. "
    "Data: UNHCR Uganda / OPM proGres Registration System, 31 March 2026. "
    "Author: Josh"
)
