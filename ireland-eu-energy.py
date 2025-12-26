import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Energy Consumption Analysis and Forecasting of Ireland in Comparison with Selected EU Countries (2012-2024)", layout="wide")

https://github.com/2025669-InciAldogan/ireland-eu-energy-dashboard/blob/main/ireland-eu-energy.py

@st.cache_data
def load_panel(path="final_panel_features.csv"):
    df = pd.read_csv(path)
    df["country"] = df["country"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    for c in ["final_cons_ktoe", "index_2012", "growth_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["country", "year"])
    return df

df_dash = load_panel()

st.title("Energy Dashboard (Ireland + Europe)")
st.caption("Interactive dashboard based on the cleaned panel dataset (2012–2023).")

# Sidebar controls
st.sidebar.header("Controls")

min_year = int(df_dash["year"].min())
max_year = int(df_dash["year"].max())
year_start, year_end = st.sidebar.slider(
    "Year range",
    min_year, max_year,
    (max(2012, min_year), min(2023, max_year))
)

df_f = df_dash[df_dash["year"].between(year_start, year_end)].copy()

# Optional: drop EU aggregate row if exists
EU27_NAME = "European Union - 27 countries (from 2020)"
df_f = df_f[df_f["country"] != EU27_NAME]

countries_all = sorted(df_f["country"].unique().tolist())
default_sel = [c for c in ["Ireland"] if c in countries_all]
countries_sel = st.sidebar.multiselect("Countries", countries_all, default=default_sel)

if countries_sel:
    df_f = df_f[df_f["country"].isin(countries_sel)].copy()

show_raw = st.sidebar.checkbox("Show raw data")
if show_raw:
    st.subheader("Filtered data preview")
    st.dataframe(df_f, use_container_width=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Europe map", "Change"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Trend (2012=100)")
        fig_line = px.line(
            df_f,
            x="year", y="index_2012", color="country",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_line.update_layout(template="plotly_white", height=420, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.subheader("Top 10 in selected year")
        year_pick = st.slider("Pick a year", year_start, year_end, year_end, key="top10_year")
        df_y = df_dash.copy()
        df_y = df_y[(df_y["year"] == year_pick) & (df_y["country"] != EU27_NAME)].copy()
        df_y = df_y.sort_values("final_cons_ktoe", ascending=False).head(10)

        fig_bar = px.bar(
            df_y,
            y="country", x="final_cons_ktoe",
            orientation="h",
            color="country",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_bar.update_layout(template="plotly_white", height=420, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("Europe Map (indexed, 2012=100)")
    year_map = st.slider("Map year", year_start, year_end, year_end, key="map_year")
    df_map = df_dash.copy()
    df_map = df_map[(df_map["year"] == year_map) & (df_map["country"] != EU27_NAME)].copy()

    fig_map = px.choropleth(
        df_map,
        locations="country",
        locationmode="country names",
        color="index_2012",
        hover_name="country",
        scope="europe",
        color_continuous_scale="Viridis"
    )
    fig_map.update_layout(template="plotly_white", height=560, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.subheader("Change view")
    year_sc = st.slider("Scatter year", year_start, year_end, year_end, key="sc_year")
    df_sc = df_dash.copy()
    df_sc = df_sc[(df_sc["year"] == year_sc) & (df_sc["country"] != EU27_NAME)].dropna(subset=["growth_pct", "index_2012"])

    fig_scatter = px.scatter(
        df_sc,
        x="index_2012", y="growth_pct",
        hover_name="country"
    )
    fig_scatter.update_layout(template="plotly_white", height=520, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)



