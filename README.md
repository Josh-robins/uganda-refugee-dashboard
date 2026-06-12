# Uganda Refugee Population — Interactive Dashboard

**[Launch the live dashboard &rarr;](https://refugee-dashboard.streamlit.app/)**

Interactive analysis of UNHCR Uganda's **Active Population by Settlement** report (31 March 2026), covering **1,999,576 registered refugees and asylum-seekers** across 14 settlements.

Built with Python, Streamlit and Plotly. All visualisations are interactive — hover for values, zoom, pan, and switch between light and dark themes.

---

## Features

- **Interactive charts** — all 15 charts are built with Plotly. Hover on any bar, pie slice, or heatmap cell to see exact values and percentages. Zoom, pan, and download as PNG.
- **Dark / light mode** — toggle Settings > Theme in the top-right corner. Charts adapt instantly.
- **Region filter** — filter by Western (DRC corridor + Kiryandongo), West Nile (South Sudan corridor), or Central (Kampala).
- **Country of origin filter** — select any combination of the 9 origin countries. KPIs and charts recalculate to show only refugees from the selected origins.
- **Gender filter** — view female-only or male-only data across every chart.
- **Age group filter** — select specific age brackets (0-4, 5-11, 12-17, 18-35, 36-59, 60+).
- **Adult vs Child toggle** — switch between children (0-17), adults (18+), or all.

### Dashboard tabs

| Tab | Contents |
|---|---|
| **Overview** | Settlement totals (ranked bar), gender summary, age donut, population pyramid |
| **Age & Gender** | Age composition by settlement (stacked bar), female vs male comparison |
| **Country of Origin** | Origin distribution, diversity index, origin dominance, nationality composition, concentration heatmap |
| **Demographic Insights** | Youth bulge (18-35), child share (0-17), elderly share (60+), gender parity with 50% reference |
| **Programme Targeting** | Education & livelihoods priority settlements with top-3 rankings and key conclusions |

### Key findings

- **85% of all refugees** come from just two countries — South Sudan (52%) and DR Congo (33%)
- **Two geographic corridors** exist: a South Sudan–dominated north and a DRC-dominated west
- **Kampala is a complete outlier** — the only urban settlement, with refugees from 8+ countries and no single majority nationality (diversity index: 0.759)
- **Kiryandongo** is the only rural settlement split between two large groups — South Sudan (52%) and Sudan (48%)
- **787,171 school-age children** (5-17 yrs) — 39% of the total population — making education one of the most critical programming needs
- **931,599 working-age adults** (18-59 yrs) represent the livelihoods target population

---

## What's in this repo

```
├── app.py                                  # Streamlit / Plotly interactive dashboard
├── refugee_visualisation (1).ipynb         # Original Jupyter analysis notebook
├── refugee_population_by_settlement.csv    # Population by settlement, gender & age group
├── refugee_country_of_origin.csv           # Population by settlement & country of origin
├── BWAT.md                                 # Project instructions for AI coding assistant
├── requirements.txt                        # Python dependencies
├── Logos/                                  # Partner logos
│   ├── wcc.jpg
│   └── canada.png
└── README.md
```

---

## Live dashboard

**[https://refugee-dashboard.streamlit.app/](https://refugee-dashboard.streamlit.app/)** — hosted on Streamlit Community Cloud. Automatically deploys from the `main` branch on every push.

---

## Getting started

**Requirements**

```
pandas
numpy
streamlit
plotly
Pillow
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
