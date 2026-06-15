import streamlit as st
from utils import load_data, prepare_data, sidebar_filters
import plotly.express as px

df = load_data()
df = prepare_data(df)

filtered, location = sidebar_filters(df)

# Dataframe für Korrelationsmatrix
corr_df = filtered[[
    "Niederschlag",
    "LufttemperaturMittel",
    "Total_Wasser",
    "Quellwasser_imNetz_absolut"
]].dropna()

st.subheader("Meteodaten und Hydrologie")

#korrelation
fig4 = px.scatter(
    filtered,
    x="Niederschlag",
    y="Quellwasser_imNetz_absolut",
    trendline="ols",
    title="Niederschlag vs Quellwasserverfügbarkeit"
)

st.plotly_chart(fig4, use_container_width=True)

# Lag effekt
filtered["Niederschlag_lag30"] = filtered["Niederschlag"].shift(30)

fig_lag = px.scatter(
    filtered,
    x="Niederschlag_lag30",
    y="Quellwasser_imNetz_absolut",
    trendline="ols",
    title="Lag 7 Tage: Niederschlag → Quellwasser"
)

st.plotly_chart(fig_lag, use_container_width=True)


#Korrelationsmatrix

corr = corr_df.corr(numeric_only=True)

fig6 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    aspect="auto",
    title="Korrelationsmatrix"
)

st.plotly_chart(fig6, use_container_width=True)

st.write(
    """Es kann keine signifikante Korrelation zwischen Niederschlag, Wasserverfügbarkeit und 
    Quellwasserverbrauch festgestellt werden.         
    """
)