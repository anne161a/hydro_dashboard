import streamlit as st
from utils import load_data, prepare_data, sidebar_filters
import plotly.express as px

df = load_data()
df = prepare_data(df)

filtered, location = sidebar_filters(df)

st.subheader("Herkunft vom gebrauchten Wasser")

# Quellwasserverbrauch
fig1 = px.line(
    filtered,
    x="Datum",
    y="Quellwasser_7d_f",
    title="Quellwasser im Netz (7 Tage Mittel)"
)

st.plotly_chart(fig1, use_container_width=True)


fig2 = px.line(
    filtered,
    x="Datum",
    y=["Quellwasser_7d_f", "Grundwasser_7d_f"],
    title="Wasserherkunft (absolut)"
)
fig2.update_layout(
    yaxis_title="[m³]"
)

st.plotly_chart(fig2, use_container_width=True)

# Wassermix

fig5 = px.area(
    filtered,
    x="Datum",
    y=[
        "Quellwasser_7d_prozent_f",
        "Grundwasser_7d_prozent_f"
    ],
    title="Anteile im Netz"
)

st.plotly_chart(fig5, use_container_width=True)

