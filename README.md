# Uganda Refugee Population — Data Analysis & Visualisation

Exploratory data analysis of UNHCR Uganda's **Active Population by Settlement** report (31 March 2026), covering **1,999,576 registered refugees and asylum-seekers** across 14 settlements.

Built with Python and Jupyter. This analysis was intened for educational purposes. No copies of this visuals have been publicly published in journals or any articles. Readers may request me to perform for them an in depth analysis in case they have their intended data at hand. 

---

## What's in this repo

```
├── app.py                                  # Streamlit interactive dashboard
├── refugee_visualisation (1).ipynb         # Main analysis notebook
├── refugee_population_by_settlement.csv    # Population by settlement, gender & age group
├── refugee_country_of_origin.csv           # Population by settlement & country of origin
├── requirements.txt                        # Python dependencies
├── Logos/                                  # Partner logos
│   ├── wcc.png
│   └── canada.png
└── README.md
```

---

## Key findings

- **85% of all refugees** come from just two countries — South Sudan (52%) and DR Congo (33%)
- **Two geographic corridors** exist: a South Sudan–dominated north and a DRC-dominated west
- **Kampala is a complete outlier** — the only urban settlement, with refugees from 8+ countries and no single majority nationality (diversity index: 0.759)
- **Kiryandongo** is the only rural settlement split between two large groups — South Sudan (52%) and Sudan (48%)
- **787,171 school-age children** (5–17 yrs) — 39% of the total population — making education one of the most critical programming needs
- **931,599 working-age adults** (18–59 yrs) represent the livelihoods target population

---

## Notebook sections

| Section | Description |
|---|---|
| 1. Setup & data loading | Libraries, colour palette, load CSVs |
| 2. Settlement totals | Ranked horizontal bar — population per settlement |
| 3. Age & gender pyramid | Population pyramid with percentage labels |
| 4. Age composition | Stacked bar — age groups across all settlements |
| 5. Female vs male | Grouped bar comparison per settlement |
| 6. Age-group share | Donut chart — overall age distribution |
| 7. Full dashboard | All 5 charts combined into one exportable figure |
| A. Country of origin | Ranked bar — frequency of each origin country |
| B. Nationality composition | 100% stacked bar — mix per settlement |
| C. Concentration heatmap | Settlement × country matrix |
| D. Diversity index | Simpson's Diversity Index per settlement |
| E. NGO targeting panel | School-age children vs working-age adults |
| F. Key conclusions | Printed summary for education & livelihoods NGOs |

---

## Getting started

**Requirements**
```
pandas
matplotlib
numpy
streamlit
Pillow
```

Install with:
```bash
pip install -r requirements.txt
```

**Run the interactive dashboard (recommended)**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501` — filter by region, country of origin, gender, age group, and adult/child. Five tabs: Overview, Age & Gender, Country of Origin, Demographic Insights, Programme Targeting.

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
