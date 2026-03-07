# Food Access Inequality Mapper — Barcelona

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://food-access-inequality-bcn.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Mapping grocery access gaps across Barcelona using H3 hexagonal indexing, OpenStreetMap POI data, and open demographic data from INE and Ajuntament de Barcelona.

**[🚀 Live Demo](https://food-access-inequality-bcn.streamlit.app/)**

---

## 🔍 Key Findings

- **Vila de Gràcia** is Barcelona's best-served neighbourhood (avg score: 69.9/100, 277 grocery stores), while **Vallvidrera, el Tibidabo i les Planes** is the most underserved (avg score: 21.3/100, 71.4% food desert hexes)
- **Food deserts in Barcelona are geography-driven, not income-driven**: Pearson r = 0.012 (p = 0.71) shows no significant linear relationship between household income and food access score
- A weak but significant Spearman correlation (r = 0.095, p = 0.003) suggests mild monotonic association, but the dominant driver is **physical isolation** — hillside and industrial neighbourhoods account for 8 of the 10 most underserved areas
- **96.4% of Barcelona's 73 neighbourhoods** were successfully matched with 2022 household income data from INE, enabling city-wide comparative analysis

---

## Problem Statement

Food deserts — areas with poor access to affordable, nutritious food — disproportionately affect low-income communities. Despite Barcelona's density, significant access gaps exist across districts. This project quantifies and visualises those gaps at street level using Uber's H3 hexagonal grid system, allowing policymakers, researchers, and businesses to identify underserved areas with precision.

---

## Methodology

### 1. Data Collection
- Grocery store POIs (supermarkets, convenience stores, fresh markets) fetched via the Overpass API from OpenStreetMap
- Population and income data at census-section level from INE (Censo 2021) and Ajuntament de Barcelona Open Data Portal
- Neighbourhood boundary GeoJSON from Ajuntament de Barcelona

### 2. H3 Indexing
- Barcelona tessellated at H3 resolution 9 (~174m hex diameter)
- Each grocery POI assigned to its H3 hex using `h3.geo_to_h3()`
- Catchment areas computed using `h3.grid_disk(hex, k=2)` (~500m radius)
- Hexes with zero stores within k=2 rings flagged as potential food deserts

### 3. Composite Food Access Score (0–100)

| Component            | Weight | Description                                             |
|----------------------|--------|---------------------------------------------------------|
| Store density        | 40%    | Count of grocery POIs within k=2 catchment ring        |
| Store diversity      | 20%    | Variety of shop types (supermarket, convenience, fresh) |
| Population pressure  | 20%    | Residents per store in catchment area                   |
| Income deprivation   | 20%    | Inverse of median household income (INE data)           |

A **lower score** indicates a food desert. A **higher score** indicates a well-served area.

### 4. Visualisation
- **Choropleth hex map** (Folium): hexes coloured by Food Access Score
- **Bivariate map**: income quintile overlaid with access score to surface inequality
- **Streamlit dashboard**: interactive resolution slider, district filter, and layer toggles

---

## Key Questions Answered

1. Which Barcelona districts have the worst food access?
2. Is low food access correlated with low income?
3. How does the picture change at different H3 resolutions?

---

## Project Structure

```
food-access-inequality-bcn/
├── data/
│   ├── raw/                  # Downloaded shapefiles and CSVs
│   └── processed/            # H3-indexed GeoDataFrames
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_h3_indexing.ipynb
│   ├── 03_scoring.ipynb
│   └── 04_visualization.ipynb
├── app/
│   └── streamlit_app.py      # Interactive Streamlit dashboard
├── outputs/
│   └── maps/                 # Exported Folium HTML maps
├── requirements.txt
└── README.md
```

---

## Data Sources

| Dataset                       | Source                            | License   |
|-------------------------------|-----------------------------------|-----------|
| Grocery POIs                  | OpenStreetMap via Overpass API    | ODbL      |
| Neighbourhood boundaries      | Ajuntament de Barcelona Open Data | CC BY 4.0 |
| Income by neighbourhood       | Ajuntament de Barcelona Open Data | CC BY 4.0 |
| Population by census section  | INE Censo 2021                    | Open      |

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run notebooks in order (01 → 04) via JupyterLab
jupyter lab

# Launch interactive dashboard
streamlit run app/streamlit_app.py
```

---

## Tech Stack

`h3-py` · `geopandas` · `folium` · `overpy` · `pandas` · `scipy` · `streamlit` · `plotly`

---

## Roadmap

- [x] Project scaffolding and data pipeline design
- [x] Overpass API data collection for Barcelona
- [x] H3 tessellation and catchment area analysis
- [x] Composite scoring model
- [x] Folium choropleth visualisation
- [x] Streamlit dashboard
- [ ] v2: Expand to all of Catalonia (947 municipalities)

---

## Author

**Ayush Raj** — MSc Business Analytics, ESADE Barcelona  
[GitHub](https://github.com/ayushr-1o) · [LinkedIn](https://www.linkedin.com/in/r-ayush-1101/)
