import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from branca.colormap import LinearColormap
import plotly.express as px

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Access Inequality — Barcelona",
    page_icon="🥦",
    layout="wide"
)

# ── Load Data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    gdf_hex   = gpd.read_file("data/processed/barcelona_hex_scored.geojson")
    df_barris = pd.read_csv("data/processed/barcelona_barri_scores.csv")
    gdf_pois  = gpd.read_file("data/processed/barcelona_pois_clipped.geojson")
    return gdf_hex, df_barris, gdf_pois

gdf_hex, df_barris, gdf_pois = load_data()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.markdown("## 🥦")
st.sidebar.title("Food Access BCN")
st.sidebar.markdown("Mapping grocery access inequality across Barcelona using H3 hexagonal indexing.")

map_type = st.sidebar.radio(
    "Select Map",
    ["Food Access Score", "Bivariate (Income vs Access)", "Store Density Heatmap"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

all_barris = sorted(gdf_hex["barri_name"].dropna().unique().tolist())
selected_barris = st.sidebar.multiselect(
    "Filter by Neighbourhood",
    options=all_barris,
    default=[]
)

score_range = st.sidebar.slider(
    "Food Access Score Range",
    min_value=0, max_value=100,
    value=(0, 100), step=1
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Sources**")
st.sidebar.markdown("- OpenStreetMap (Overpass API)\n- Ajuntament de Barcelona\n- INE Censo 2021")
st.sidebar.markdown("**Author:** [Ayush Raj](https://github.com/ayushr-1o)")

# ── Filter Data ───────────────────────────────────────────────────
gdf_filtered = gdf_hex[
    gdf_hex["food_access_score"].between(score_range[0], score_range[1])
].copy()

if selected_barris:
    gdf_filtered = gdf_filtered[gdf_filtered["barri_name"].isin(selected_barris)]

# ── Header ────────────────────────────────────────────────────────
st.title("🥦 Food Access Inequality — Barcelona")
st.markdown("*Mapping grocery access gaps using H3 hexagonal indexing, OpenStreetMap POI data, and INE household income data.*")

# ── KPI Row ───────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Hexes Analysed",   f"{len(gdf_hex):,}")
k2.metric("Grocery Stores Mapped",  f"{len(gdf_pois):,}")
k3.metric("Food Desert Hexes",      f"{gdf_hex['is_food_desert'].sum():,}",
          f"{gdf_hex['is_food_desert'].mean()*100:.1f}% of city",
          delta_color="inverse")
k4.metric("Neighbourhoods Covered", f"{gdf_hex['barri_name'].nunique()}")

st.markdown("---")

# ── Build Map ─────────────────────────────────────────────────────
st.subheader(f"🗺️ {map_type}")

m = folium.Map(location=[41.3874, 2.1686], zoom_start=12, tiles="CartoDB positron")

if map_type == "Food Access Score":
    colormap = LinearColormap(
        colors=["#d73027", "#f46d43", "#fee08b", "#a6d96a", "#1a9850"],
        vmin=gdf_hex["food_access_score"].min(),
        vmax=gdf_hex["food_access_score"].max(),
    )
    # DO NOT add colormap to map — use custom HTML legend instead

    features = []
    for _, row in gdf_filtered.iterrows():
        features.append({
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {
                "barri_name":            str(row.get("barri_name", "")),
                "food_access_score":     round(float(row["food_access_score"]), 1),
                "catchment_store_count": int(row["catchment_store_count"]),
                "is_food_desert":        bool(row["is_food_desert"]),
            }
        })

    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda f: {
            "fillColor":  colormap(f["properties"]["food_access_score"]),
            "color": "white", "weight": 0.3, "fillOpacity": 0.75
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["barri_name", "food_access_score", "catchment_store_count", "is_food_desert"],
            aliases=["Neighbourhood", "Access Score", "Stores in catchment", "Food Desert?"]
        )
    ).add_to(m)

    # Custom centered legend
    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:25px;left:50%;transform:translateX(-50%);
                background:white;padding:8px 16px;border-radius:6px;
                box-shadow:2px 2px 6px rgba(0,0,0,0.3);z-index:1000;
                font-size:12px;color:black;text-align:center;">
        <b>Food Access Score</b><br>
        <span style="color:#d73027">&#9632;</span> 0 &nbsp;
        <span style="background:linear-gradient(to right,#d73027,#f46d43,#fee08b,#a6d96a,#1a9850);
                     display:inline-block;width:160px;height:12px;vertical-align:middle;
                     border-radius:3px;"></span>
        &nbsp; 100 <span style="color:#1a9850">&#9632;</span><br>
        <small style="color:#666">Worst → Best</small>
    </div>
    """))

    features = []
    for _, row in gdf_filtered.iterrows():
        features.append({
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {
                "barri_name":            str(row.get("barri_name", "")),
                "food_access_score":     round(float(row["food_access_score"]), 1),
                "catchment_store_count": int(row["catchment_store_count"]),
                "is_food_desert":        bool(row["is_food_desert"]),
            }
        })

    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda f: {
            "fillColor":  colormap(f["properties"]["food_access_score"]),
            "color": "white", "weight": 0.3, "fillOpacity": 0.75
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["barri_name", "food_access_score", "catchment_store_count", "is_food_desert"],
            aliases=["Neighbourhood", "Access Score", "Stores in catchment", "Food Desert?"]
        )
    ).add_to(m)

elif map_type == "Bivariate (Income vs Access)":
    gdf_filtered["income_q"] = pd.qcut(
        gdf_filtered["income_index"].fillna(gdf_filtered["income_index"].median()),
        q=3, labels=["Low", "Mid", "High"]
    )
    gdf_filtered["access_q"] = pd.qcut(
        gdf_filtered["food_access_score"], q=3, labels=["Low", "Mid", "High"]
    )
    bivariate_colors = {
        ("Low","Low"):"#e8d6c0",  ("Low","Mid"):"#c8a882",  ("Low","High"):"#a67c52",
        ("Mid","Low"):"#b0c4c8",  ("Mid","Mid"):"#8fa8aa",  ("Mid","High"):"#6a8c8e",
        ("High","Low"):"#6a9fb5", ("High","Mid"):"#4a7f96", ("High","High"):"#1a5f78",
    }
    gdf_filtered["biv_color"] = gdf_filtered.apply(
        lambda r: bivariate_colors.get((str(r["income_q"]), str(r["access_q"])), "#cccccc"), axis=1
    )

    features = []
    for _, row in gdf_filtered.iterrows():
        features.append({
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {
                "barri_name":        str(row.get("barri_name", "")),
                "income_index":      round(float(row["income_index"]), 0) if pd.notna(row["income_index"]) else 0,
                "food_access_score": round(float(row["food_access_score"]), 1),
                "income_q":          str(row["income_q"]),
                "access_q":          str(row["access_q"]),
                "biv_color":         str(row["biv_color"]),
            }
        })

    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda f: {
            "fillColor": f["properties"]["biv_color"],
            "color": "white", "weight": 0.3, "fillOpacity": 0.75
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["barri_name", "income_index", "food_access_score", "income_q", "access_q"],
            aliases=["Neighbourhood", "Median Income (€)", "Access Score", "Income Tier", "Access Tier"]
        )
    ).add_to(m)

    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:30px;left:50%;transform:translateX(-50%);
                background:white;padding:12px;border-radius:8px;font-size:11px;
                box-shadow:2px 2px 6px rgba(0,0,0,0.3);z-index:1000;">
      <b>Income vs Food Access</b><br><br>
      <table cellspacing="2">
        <tr><td></td>
            <td style="text-align:center;font-size:10px">Low<br>Access</td>
            <td style="text-align:center;font-size:10px">Mid<br>Access</td>
            <td style="text-align:center;font-size:10px">High<br>Access</td></tr>
        <tr><td style="font-size:10px">High<br>Income</td>
            <td style="background:#6a9fb5;width:22px;height:22px"></td>
            <td style="background:#4a7f96;width:22px;height:22px"></td>
            <td style="background:#1a5f78;width:22px;height:22px"></td></tr>
        <tr><td style="font-size:10px">Mid<br>Income</td>
            <td style="background:#b0c4c8;width:22px;height:22px"></td>
            <td style="background:#8fa8aa;width:22px;height:22px"></td>
            <td style="background:#6a8c8e;width:22px;height:22px"></td></tr>
        <tr><td style="font-size:10px">Low<br>Income</td>
            <td style="background:#e8d6c0;width:22px;height:22px"></td>
            <td style="background:#c8a882;width:22px;height:22px"></td>
            <td style="background:#a67c52;width:22px;height:22px"></td></tr>
      </table>
    </div>
    """))

elif map_type == "Store Density Heatmap":
    m = folium.Map(location=[41.3874, 2.1686], zoom_start=12, tiles="CartoDB dark_matter")
    heat_data = [[r.geometry.y, r.geometry.x] for _, r in gdf_pois.iterrows()]
    HeatMap(heat_data, radius=12, blur=8).add_to(m)

# ── Render Map Full Width ─────────────────────────────────────────
st_folium(m, width=1400, height=650, returned_objects=[])

st.markdown("---")

# ── Neighbourhood Rankings (full width) ───────────────────────────
st.subheader("📊 Neighbourhood Rankings")

df_display = df_barris.dropna(subset=["avg_food_access_score"]).sort_values("avg_food_access_score")

rank_col1, rank_col2 = st.columns(2)

with rank_col1:
    st.markdown("#### 🔴 Most Underserved")
    st.dataframe(
        df_display.head(10)[["barri_name", "avg_food_access_score", "pct_food_desert", "total_stores"]]
        .rename(columns={
            "barri_name":            "Neighbourhood",
            "avg_food_access_score": "Score",
            "pct_food_desert":       "% Desert",
            "total_stores":          "Stores"
        })
        .round(1).reset_index(drop=True),
        use_container_width=True, hide_index=True
    )

with rank_col2:
    st.markdown("#### 🟢 Best Served")
    st.dataframe(
        df_display.tail(10).iloc[::-1][["barri_name", "avg_food_access_score", "pct_food_desert", "total_stores"]]
        .rename(columns={
            "barri_name":            "Neighbourhood",
            "avg_food_access_score": "Score",
            "pct_food_desert":       "% Desert",
            "total_stores":          "Stores"
        })
        .round(1).reset_index(drop=True),
        use_container_width=True, hide_index=True
    )

st.markdown("---")

# ── Scatter Plot (full width) ─────────────────────────────────────
st.subheader("📈 Income vs Food Access Score")

df_scatter = df_barris.dropna(subset=["avg_food_access_score", "median_income"])
label_these = [
    "la Vila de Gràcia", "Vallvidrera, el Tibidabo i les Planes",
    "Pedralbes", "Ciutat Meridiana", "el Raval",
    "Sant Genís dels Agudells", "les Tres Torres"
]
df_scatter["label"] = df_scatter["barri_name"].apply(
    lambda x: x if x in label_these else ""
)

fig = px.scatter(
    df_scatter, x="median_income", y="avg_food_access_score",
    text="label", color="avg_food_access_score",
    color_continuous_scale="RdYlGn", size="total_stores", size_max=35,
    hover_name="barri_name",
    hover_data={"median_income": True, "avg_food_access_score": True,
                "total_stores": True, "label": False},
    labels={
        "median_income":         "Median Household Income (€)",
        "avg_food_access_score": "Avg Food Access Score",
        "total_stores":          "Total Stores"
    },
    title="Income vs Food Access Score by Neighbourhood (Spearman r=0.095, p=0.003)"
)
fig.update_traces(textposition="top center", textfont_size=10)
fig.update_layout(
    height=550, template="plotly_white",
    showlegend=False, coloraxis_showscale=True,
    margin=dict(t=60, b=60, l=60, r=60)
)
fig.add_annotation(
    x=0.02, y=0.97, xref="paper", yref="paper",
    text="<b>Key insight:</b> Food deserts are geography-driven,<br>not income-driven in Barcelona (Pearson r=0.012)",
    showarrow=False, bgcolor="white", bordercolor="grey",
    borderwidth=1, font=dict(size=11, color="black"), align="left"
)
st.plotly_chart(fig, use_container_width=True)

# ── Key Findings ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔍 Key Findings")

f1, f2, f3 = st.columns(3)
f1.info("**Vila de Gràcia** is Barcelona's best-served neighbourhood (score: 69.9/100, 277 stores)")
f2.warning("**Vallvidrera/Tibidabo** is the most underserved (score: 21.3/100) — driven by mountain terrain, not poverty")
f3.success("**Food deserts are geography-driven, not income-driven** — Pearson r = 0.012 (p = 0.71)")
