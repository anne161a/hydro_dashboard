import streamlit as st
import pandas as pd
import glob
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Hydrologie Dashboard", layout="wide")


# 1. DATA LOADING
@st.cache_data
def load_data():

    # --- Meteo ---
    meteo = pd.read_csv("data/ChateauDOex_Meteo.csv", sep=";")
    meteo["Datum"] = pd.to_datetime(meteo["Datum"], dayfirst=True)

    # --- Wasser (alle Orte + Jahre) ---
    files = glob.glob("data/*_Saanen.csv")

    dfs = []

    for file in files:
        df = pd.read_csv(file, sep=";")

        # Ort aus Filename
        name = Path(file).stem
        parts = name.split("_")

        if len(parts) >= 2:
            df["year"] = parts[0]
            df["location"] = "_".join(parts[1:])

        df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)

        dfs.append(df)

    wasser = pd.concat(dfs, ignore_index=True)

    # --- Merge Meteo ---
    df = pd.merge(wasser, meteo, on="Datum", how="left")

    return df


df = load_data()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["dayofyear"] = df["Datum"].dt.dayofyear

df = df.sort_values("Datum")

df["Total_Wasser"] = (
    df["Quellwasser_imNetz_absolut"] +
    df["Grundwasser_imNetz_absolut"]
)

df["Grundwasser_7d"] = (
    df.groupby(["location","year"])["Grundwasser_imNetz_absolut"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)
df["Quellwasser_7d"] = (
    df.groupby(["location","year"])["Quellwasser_imNetz_absolut"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)
df["TotalWasser_7d"] = (
    df.groupby(["location","year"])["Total_Wasser"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)

df["WasserBilanz"] = (
    df["Niederschlag"] -
    df["Referenzverdunstung"]
)

# System Parameter Konstanten
GW_KONZESSION_L_MIN = 17500
GW_KONZESSION_M3_DAY = GW_KONZESSION_L_MIN * 60 * 24 / 1000

RESERVOIR_CAPACITY_M3 = 12055

# Sidebar Zeitraum
st.sidebar.title("Filter")

locations = df["location"].dropna().unique()
location = st.sidebar.selectbox("Ort", locations)

min_date = df["Datum"].min()
max_date = df["Datum"].max()

date_range = st.sidebar.date_input(
    "Zeitraum",
    [min_date, max_date]
)

# Sidebar Graphen anzeigen
compare_years = st.sidebar.checkbox("Jahresvergleich anzeigen", True)
water_origin = st.sidebar.checkbox("Wasserherkunft anzeigen", True)
meteo_hydrologie_data = st.sidebar.checkbox("Meteodaten und Hydrologie anzeigen", True)
szenario = st.sidebar.checkbox("Szenario anzeigen", True)

# Sidebar Szenario

st.sidebar.subheader("Versorgungsszenario")

pump_failure = st.sidebar.slider(
    "Pumpausfall (%)",
    0,
    100,
    0
) / 100

initial_storage_percent = st.sidebar.slider(
    "Reservoir Füllstand (%)",
    0,
    100,
    70
) / 100
st.sidebar.metric(
    "Reservoir Inhalt",
    f"{RESERVOIR_CAPACITY_M3 * initial_storage_percent:.0f} m³"
)


# Filter in DataFrame einbauen
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

filtered = df[
    (df["location"] == location) &
    (df["Datum"] >= start) &
    (df["Datum"] <= end)
].copy()

filtered = filtered.sort_values("Datum")

# Dataframe für Korrelationsmatrix
corr_df = filtered[[
    "Niederschlag",
    "LufttemperaturMittel",
    "Total_Wasser",
    "Quellwasser_imNetz_absolut"
]].dropna()

# verfügbare Grundwasserförderung
gw_available = GW_KONZESSION_M3_DAY * (1-pump_failure)

filtered["GW_Szenario"] = gw_available

filtered["Supply_Szenario"] =(
    filtered["Quellwasser_imNetz_absolut"] +
    filtered["GW_Szenario"]
)

filtered["Demand"] = filtered["Total_Wasser"]

filtered["Quellwasser_7d_f"] = (
    filtered["Quellwasser_imNetz_absolut"]
    .rolling(7, min_periods=1)
    .mean()
)

filtered["Grundwasser_7d_f"] = (
    filtered["Grundwasser_imNetz_absolut"]
    .rolling(7, min_periods=1)
    .mean()
)

filtered["TotalWasser_7d_f"] = (
    filtered["Total_Wasser"]
    .rolling(7, min_periods=1)
    .mean()
)

filtered["WasserBilanz_7d_f"] = (
    filtered["WasserBilanz"]
    .rolling(7, min_periods=1)
    .mean()
)

filtered["Quellwasser_7d_prozent_f"] =(
    filtered["Quellwasser_imNetz_prozent"]
    .rolling(7, min_periods=1)
    .mean()
)
filtered["Grundwasser_7d_prozent_f"] =(
    filtered["Grundwasser_imNetz_prozent"]
    .rolling(7, min_periods=1)
    .mean()
)

storage = RESERVOIR_CAPACITY_M3 * initial_storage_percent

storage_levels = []
deficits = []
spills = []

# DataFrame für Szenario

for i, row in filtered.iterrows():

    supply = row["Supply_Szenario"]
    demand = row["Demand"]

    #Rohe Bilanz
    storage_new = storage + supply - demand

    # Defizit
    if storage_new < 0:
        deficit = -storage_new
        storage_new = 0
    else: 
        deficit = 0

    # überlauf 
    spill = max(0, storage_new - RESERVOIR_CAPACITY_M3)

    #finaler Speicer
    storage = min(storage_new, RESERVOIR_CAPACITY_M3 * initial_storage_percent)

    storage_levels.append(storage)
    deficits.append(deficit)
    spills.append(spill)

filtered["Reservoir"] = storage_levels
filtered["Defizit"] = deficits
filtered["Spill"] = spills

# titel
st.title("Saanen Wasserversorgung Dashboard")


# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ø Temperatur", f"{filtered['LufttemperaturMittel'].mean():.2f} °C")

with col2:
    st.metric("Total Niederschlag", f"{filtered['Niederschlag'].sum():.1f} mm")

with col3:
    st.metric("Ø Täglicher Wasserverbrauch",
              f"{filtered['Total_Wasser'].mean():.1f} m³")

# Graphen

# Vergleich der Jahre
if compare_years:
    st.subheader("Vergleich Wasserverbrauch nach Jahr")

    year_df = df[df["location"] == location].copy()

    year_summary = (
        year_df.groupby("year")["Total_Wasser"]
        .agg(["mean", "sum"])
        .reset_index()
    )
    # Total Wasser
    fig_yearTW = px.line(
        year_df,
        x="dayofyear",
        y="TotalWasser_7d",
        color="year",
        title="Wasserverbrauch im Jahresvergleich",
    )

    fig_yearTW.update_layout(
        xaxis_title="Tag im Jahr",
        yaxis_title="Wasserverbrauch [m³]",
        xaxis=dict(
            tickmode="array",
            tickvals=[15, 45, 75, 115, 135, 165, 195, 225, 255, 285, 315, 345],
            ticktext=["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
        )
    )

    st.plotly_chart(fig_yearTW, use_container_width=True)

    max_cols = 4

    for i in range(0, len(year_summary), max_cols):
        cols = st.columns(max_cols)

        chunk = year_summary.iloc[i:i + max_cols]

        for col, (_, row) in zip(cols, chunk.iterrows()):
            col.metric(
                label=f"Jahr {int(row['year'])}",
                value=f"{row['sum']:,.0f} m³".replace(",","'"),
                delta=f"{row['mean']:,.1f} m³/Tag".replace(",","'")
            )

# Quellwasser
    fig_yearQW = px.line(
        year_df,
        x="dayofyear",
        y="Quellwasser_7d",
        color="year",
        title="Quellwasserverbrauch im Jahresvergleich",
    )

    fig_yearQW.update_layout(
        xaxis_title="Tag im Jahr",
        yaxis_title="Quellwasserverbrauch [m³]",
        xaxis=dict(
            tickmode="array",
            tickvals=[15, 45, 75, 115, 135, 165, 195, 225, 255, 285, 315, 345],
            ticktext=["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
        )
    )

    st.plotly_chart(fig_yearQW, use_container_width=True)

# Grundwasser
    fig_yearGW = px.line(
        year_df,
        x="dayofyear",
        y="Grundwasser_7d",
        color="year",
        title="Grundwasserverbrauch im Jahresvergleich",
    )

    fig_yearGW.update_layout(
        xaxis_title="Tag im Jahr",
        yaxis_title="Grundwasserverbrauch [m³]",
        xaxis=dict(
            tickmode="array",
            tickvals=[15,45,75,115,135,165,195,225,255,285,315,345],
            ticktext=["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
        )
    )

    st.plotly_chart(fig_yearGW, use_container_width=True)

# Wasser Herkunft
if water_origin:
    st.subheader("Herkunft Wasser")

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

# Meteo und Hydro Graphen
if meteo_hydrologie_data:
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

# Szenario
if szenario:
    st.subheader("Reservoir Speicher")
    fig7 = px.line(
        filtered,
        x="Datum",
        y="Reservoir",
        title="Reservoirfüllstand"
    )

    fig7.update_layout(
        yaxis_title="Speicher [m³]"
    )

    st.plotly_chart(fig7, use_container_width=True)

    # Defizit Plot
    fig8 = px.bar(
        filtered,
        x="Datum",
        y="Defizit",
        title="Versorgungsdefizit"
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


    # 8. RAW DATA
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(filtered)

