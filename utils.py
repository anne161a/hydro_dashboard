import pandas as pd
import glob
from pathlib import Path
import streamlit as st

# Konstanten
GW_KONZESSION_L_MIN = 17500
GW_KONZESSION_M3_DAY = GW_KONZESSION_L_MIN * 60 * 24 / 1000

RESERVOIR_CAPACITY_M3 = 12055

@st.cache_data
def load_data():

    # Meteo
    meteo = pd.read_csv("data/ChateauDOex_Meteo.csv", sep=";")
    meteo["Datum"] = pd.to_datetime(meteo["Datum"], dayfirst=True)

    # Wasser
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

    # Merge Meteo
    df = pd.merge(wasser, meteo, on="Datum", how="left")

    return df


def prepare_data(df):
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["dayofyear"] = df["Datum"].dt.dayofyear

    df = df.sort_values("Datum")

    df["Total_Wasser"] = (
            df["Quellwasser_imNetz_absolut"] +
            df["Grundwasser_imNetz_absolut"]
    )

    df["Grundwasser_7d"] = (
        df.groupby(["location", "year"])["Grundwasser_imNetz_absolut"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )
    df["Quellwasser_7d"] = (
        df.groupby(["location", "year"])["Quellwasser_imNetz_absolut"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )
    df["TotalWasser_7d"] = (
        df.groupby(["location", "year"])["Total_Wasser"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    df["WasserBilanz"] = (
            df["Niederschlag"] -
            df["Referenzverdunstung"]
    )

    return df


def sidebar_filters(df):
    st.sidebar.title("Filter")

    locations = df["location"].dropna().unique()
    location = st.sidebar.selectbox("Ort", locations)

    min_date = df["Datum"].min()
    max_date = df["Datum"].max()

    date_range = st.sidebar.date_input(
        "Zeitraum",
        [min_date, max_date]
    )

    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    filtered = df[
        (df["location"] == location) &
        (df["Datum"] >= start) &
        (df["Datum"] <= end)
    ].copy()

    return filtered, location

def scenario_settings():

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

    return pump_failure, initial_storage_percent

def prepare_scenario(filtered, pump_failure):

    gw_available = GW_KONZESSION_M3_DAY * (1 - pump_failure)

    filtered["GW_Szenario"] = gw_available

    filtered["Supply_Szenario"] = (
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

    return filtered


def simulate_reservoir(filtered, initial_storage_percent):

    storage = RESERVOIR_CAPACITY_M3 * initial_storage_percent

    storage_levels = []
    deficits = []
    spills = []

    for _, row in filtered.iterrows():

        supply = row["Supply_Szenario"]
        demand = row["Demand"]

        storage_new = storage + supply - demand

        if storage_new < 0:
            deficit = -storage_new
            storage_new = 0
        else:
            deficit = 0

        spill = max(0, storage_new - RESERVOIR_CAPACITY_M3)

        storage = min(storage_new, RESERVOIR_CAPACITY_M3 * initial_storage_percent)

        storage_levels.append(storage)
        deficits.append(deficit)
        spills.append(spill)

    filtered["Reservoir"] = storage_levels
    filtered["Defizit"] = deficits
    filtered["Spill"] = spills

    return filtered
