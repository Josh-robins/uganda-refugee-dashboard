# Uganda Refugee Population — Interactive Dashboard

**[Launch the live dashboard &rarr;](https://refugee-dashboard.streamlit.app/)**

Interactive analysis of UNHCR Uganda's **Active Population by Settlement** report (31 March 2026), covering **1,999,576 registered refugees and asylum-seekers** across 14 settlements.

Built with **Python, Streamlit and Plotly**. All 17 visualisations are interactive — hover for values, zoom, pan, and switch between light and dark themes.

---

## Features

### Filters (sidebar)

| Filter | Options | Behaviour |
|---|---|---|
| **Region** | Western, West Nile, Central | Cascades through all charts and KPIs |
| **Country of Origin** | 9 origin countries (South Sudan, DRC, Sudan, Eritrea, Somalia, Burundi, Rwanda, Ethiopia, Other) | When deselected, the age/gender data is **proportionally scaled** to match the selected origin mix — not simply hidden |
| **Gender** | All, Female, Male | Applies to every chart including age pyramid |
| **Age Group** | All 6 age brackets from 0-4 to 60+ | Filters age-specific chart data |
| **Adult vs Child** | All, Child (0-17), Adult (18+) | Quick toggle for programme targeting |

### Download filtered data

A **Download filtered data (CSV)** button at the bottom of the sidebar exports the currently filtered settlement-level dataset.

---

### Dashboard tabs (17 charts)

| Tab | Charts |
|---|---|
| **Overview** | Settlement totals (ranked horizontal bar), gender summary bar, regional population donut, age-group donut, age & gender pyramid |
| **Age & Gender** | Age composition by settlement (stacked bar), female vs male (grouped bar) |
| **Country of Origin** | Country-of-origin distribution (ranked bar), settlement diversity index (Simpson's, with 0.2 / 0.5 reference lines), origin dominance bar, nationality composition (stacked bar), concentration heatmap |
| **Demographic Insights** | Youth bulge (18-35 %), child share (0-17 %), elderly share (60+ %), gender parity bar (with 50 % reference line) |
| **Programme Targeting** | Education vs livelihoods dual subplot, auto-generated key conclusions with top-3 settlement rankings |

### Region KPI cards

Three **WarChild-red** summary cards below the main KPIs show per-region totals and settlement counts (Western, West Nile, Central), styled as dedicated callout cards.

### Key findings

- **85% of all refugees** come from just two countries — South Sudan (52%) and DR Congo (33%)
- **Two geographic corridors** exist: a South Sudan–dominated north and a DRC-dominated west
- **Kampala is a complete outlier** — the only urban settlement, with refugees from 8+ countries and no single majority nationality (diversity index: 0.759)
- **Kiryandongo** is the only rural settlement split between two large groups — South Sudan (52%) and Sudan (48%)
- **787,171 school-age children** (5-17 yrs) — 39% of the total population — making education one of the most critical programming needs
- **931,599 working-age adults** (18-59 yrs) represent the livelihoods target population

### Key Conclusions panel (Tab 5)

The Programme Targeting tab includes an auto-generated **Key Conclusions** section that shows:
- Population overview with top-3 nationalities
- Demographic breakdown (youth, children, elderly percentages)
- Education and livelihoods priority counts
- Top-3 settlements for education, child programming, livelihoods, and youth employment
- Most and least diverse settlements (Simpson's index)
- Highest single-nationality dominance settlement

---

## What's in this repo

```
├── app.py                                  # Streamlit / Plotly interactive dashboard (1,179 lines)
├── refugee_visualisation (1).ipynb         # Original Jupyter analysis notebook
├── refugee_population_by_settlement.csv    # Population by settlement, gender & age group
├── refugee_country_of_origin.csv           # Population by settlement & country of origin
├── BWAT.md                                 # Project instructions for AI coding assistant
├── requirements.txt                        # Python dependencies
├── Logos/                                  # Partner logos embedded in dashboard
│   ├── wcc.jpg
│   └── canada.png
└── README.md
```

---

## Technical notes

### Responsive KPI cards

Native `st.metric()` values are styled via CSS `clamp()` to scale font-size automatically on narrow screens, preventing the text-truncation (ellipsis) that occurs when 6 columns of KPIs share limited width.

### Print optimisations

A `@media print` stylesheet hides the sidebar, compresses metric fonts, reduces column gaps, and prevents chart elements from breaking across pages. Suitable for generating PDF reports from the browser's Print dialog.

### Streamlit Community Cloud

The free tier **sleeps after 7 days** of inactivity and takes 30–90 seconds to cold-start on the next visit. An uptime monitor (e.g. UptimeRobot free plan) can keep it warm by pinging it at regular intervals.

Data is loaded via `@st.cache_data` so the CSV files are parsed only once per session.

---

## Getting started

**Requirements**

```
pandas>=2.0
numpy>=1.24
Pillow>=9.0
streamlit>=1.28
plotly>=5.18
```

Install with:

```bash
pip install -r requirements.txt
```

**Run the dashboard**

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

**Run the notebook**

```bash
jupyter notebook "refugee_visualisation (1).ipynb"
```

Make sure both CSV files are in the same folder as the notebook, then run all cells from top to bottom.

---

## Data source

**UNHCR Uganda — Annex I: Active Population by Settlement, 31 March 2026**
Uganda Office of the Prime Minister (OPM) / proGres registration system.

> The boundaries and names shown and the designations used do not imply official endorsement or acceptance by the United Nations.

---

## Author

**Josh**
