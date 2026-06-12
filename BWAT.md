# BWAT.md

This file provides guidance to Bwat when working with code in this repository.

## Tech Stack
- Python 3 with Jupyter Notebook (`.ipynb`)
- Streamlit — interactive web dashboard (`app.py`) with sidebar filters, tabs, and KPI cards
- pandas — data loading and transformation
- matplotlib — all charting and dashboard assembly (rendered via `st.pyplot()`)
- numpy — numerical arrays and calculations
- Pillow (PIL) — logo rendering in the sidebar

## Brand Identity

**Colors** (defined as module-level constants in the notebook — use these exact values on every chart):
- Primary (Female bars): `#185FA5` (`BLUE`)
- Secondary (Male bars): `#2A9D8F` (`TEAL`)
- Accent (highlight / largest bar): `#D85A30` (`ACCENT`)
- Text: `#2C2C2A` (`TEXT`)
- Muted / axis labels: `#888780` (`MUTED`)
- Figure / axes background: `#FAFAF8`
- Grid lines: `#D3D1C7`, 0.5pt width
- Age-group palette: matplotlib `Blues` colormap, resampled to 8 steps, skipping the lightest

**Typography**:
- Font family: `sans-serif` (matplotlib default — let the system fallback resolve)
- Title: 13pt bold (11pt for sub-charts in dashboard)
- Axis labels: 10pt, muted color
- Tick labels: 8–9pt
- Footer / attribution: 7.5pt, muted, centered below every chart
- Bar value labels: 8–9pt, text color

**Geometry**:
- Bar height: `0.6` (horizontal) or width `0.38` (grouped vertical)
- Bar edges: `none` (flat, no stroke)
- Chart spines: top and right spines hidden; grid on x-axis only (y-axis grid hidden)
- Dashboard grid: `gridspec.GridSpec` with `hspace=0.38, wspace=0.38`
- Footer position: `fig.text(0.5, -0.02, ...)` on standalone charts; `fig.text(0.5, -0.04, ...)` when x-tick labels are rotated

**Visual language**: Clean, publication-ready NGO data viz — flat bars, no unnecessary ornament, restrained two-hue palette with a single orange accent for the largest value. Every chart carries a source/author footer line.

## Coding Conventions

- Define colors as module-level constants (`BLUE`, `TEAL`, `ACCENT`, `TEXT`, `MUTED`) in the setup cell — never hardcode hex values in chart cells.
- Define `AGE_GROUPS`, `AGE_COLS`, `AGE_LABELS`, `FOOTER` as constants in setup.
- Define `fem_cols` and `mal_cols` lists once; reuse them everywhere they are needed.
- Call `plt.tight_layout()` before every `plt.show()`.
- Always append the `FOOTER` string via `fig.text(0.5, -0.02, FOOTER, ...)` on every chart.
- Use `plt.FuncFormatter` for axis tick formatting (k/M suffixes).
- Notebook cells depend on prior cells (e.g. `df`, `totals`, `orig` are set early and reused). Cells must be run top-to-bottom; do not reorder or assume independent execution.
- DataFrames loaded from CSV should strip the "Total" summary row at load time.
- All charting uses the `#FAFAF8` canvas colour — set `figure.facecolor` and `axes.facecolor` via `rcParams` in the setup cell, and explicitly set `ax.set_facecolor("#FAFAF8")` on each axis when building multi-chart layouts.

## Architecture Notes

- **Two CSVs, one notebook.** `refugee_population_by_settlement.csv` drives Sections 1–7 (population, age/gender, dashboard). `refugee_country_of_origin.csv` drives Sections A–F (nationality, diversity, NGO targeting). Both are loaded into the same notebook and cross-referenced.
- **Single-cell execution dependency chain.** The setup cell defines global constants and loads `df`. Later cells (including the country-of-origin section) depend on earlier cells. The notebook is not modular — it is a linear pipeline.
- **Dashboard is the deliverable.** Section 7 combines all 5 base charts into one exportable figure saved as `refugee_population_dashboard.png`. The logos live in `Logos/` and are embedded via PIL.
- **Streamlit app (`app.py`).** Same brand constants, same matplotlib charts, same data pipeline — but wrapped in an interactive browser UI with sidebar settlement filtering, four tabbed views, and live KPI metric cards. Uses `@st.cache_data` to avoid re-parsing CSVs on every interaction. The sidebar filters cascade through all charts; all chart functions accept a filtered DataFrame parameter.
- **Data source:** UNHCR Uganda / OPM proGres registration system, snapshot dated 31 March 2026. The CSVs are manually exported extracts — there is no live API or database.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit dashboard (recommended)
streamlit run app.py

# Run the notebook
jupyter notebook "refugee_visualisation (1).ipynb"
```

## Gotchas

- **CSV files must be in the same working directory as the notebook.** The `pd.read_csv()` calls use bare filenames with no path.
- **The "Total" row in the settlement CSV must be stripped.** The notebook filters `df[df["Settlement"] != "Total"]` after loading. If the CSV format changes (e.g. different row label), that filter will silently pass through the summary row and double-count.
- **Pillow (PIL) is required for the dashboard section.** Cell 14 (`59865bc8`) imports `from PIL import Image` to render the WCC logo. If Pillow is not installed, that cell and all subsequent cells will fail. The earlier sections (1–6) work fine without it.
- **Column name sensitivity.** The CSVs use space-separated column names (e.g. `"0-4 Female"`, `"South_Sudan"`). Any upstream change to column spelling or separator will break the notebook silently — pandas will return KeyErrors rather than obvious failures.
- **The notebook filename contains spaces and parentheses** (`refugee_visualisation (1).ipynb`). On some shells, this requires quoting when passing to `jupyter notebook`.
- **No virtual environment configured.** There is no `requirements.txt`, `pyproject.toml`, or `Pipfile`. Dependencies are documented only in the README.
