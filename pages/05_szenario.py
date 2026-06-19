import streamlit as st
import plotly.express as px
from utils import *

df = load_data()
df = prepare_data(df)

filtered, location = sidebar_filters(df)

pump_failure, initial_storage_percent = scenario_settings()

filtered = prepare_scenario(filtered, pump_failure)
filtered = simulate_reservoir(filtered, initial_storage_percent)

st.subheader("Szenarien Rechner")

with st.expander("Erlärung zu den Graphen anzeigen"):
    st.write("""Es wird berechnet wie viel Grundwasser noch verfügbar wäre, wenn ein prozentualer Pumpausfall
                 von x vorfällt. 
                 Im Graph über den Reservoirfüllstand wird angezeigt, wie voll das Reservoir ist. Dieses füllt
                 sich automatisch auf, wenn genügend Wasser verfügbar ist. Das Reservoir füllt sich aber nur auf den
                 von Benutzenden eingestellten Wert. 
                 Im Graph über Versorgungsdefizit, sieht man an welchen Tagen der Wasserverbrauch nicht hätte
                 gedeckt werden können. Dies basiert auf die echten Verbrauchsdaten der vergangen Jahre. 

                 """)

fig7 = px.line(
    filtered,
    x="Datum",
    y="Reservoir",
    title="Reservoirfüllstand"
)

fig7.update_yaxes(
    range=[0, RESERVOIR_CAPACITY_M3],
    title="Speicher [m³]"
)

st.plotly_chart(fig7, use_container_width=True)

# Defizit Plot
fig8 = px.bar(
    filtered,
    x="Datum",
    y="Defizit",
    title="Versorgungsdefizit"
)

st.write(
    """Aus den Graphen und Berechnungen kann man lesen, dass die Gemeinde Saanen erst 
    bei einem Pumpausfall über 85% ein Versorgungsdefizit hätte (bei einem Reservoir von mind. 40%).         
    """
)

st.plotly_chart(fig8, use_container_width=True)

# Kennzahlen Resilienz
st.subheader("System Resilienz")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Tage mit Defizit",
    int((filtered["Defizit"] > 0).sum())
)

col2.metric(
    "Minimum Reservoir",
    f"{filtered['Reservoir'].min():.0f} m³"
)

col3.metric(
    "Max Defizit",
    f"{filtered['Defizit'].max():.0f} m³"
)