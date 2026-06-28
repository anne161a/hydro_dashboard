import streamlit as st
from utils import load_data, prepare_data, sidebar_filters
import plotly.express as px

df = load_data()
df = prepare_data(df)

filtered, location = sidebar_filters(df)

st.header("Wasserverbrauch verglichen nach Jahren")

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

fig_yearTW.update_yaxes(
    range=[0, df["Total_Wasser"].max()]
)

st.plotly_chart(fig_yearTW, use_container_width=True)

max_cols = 4

for i in range(0, len(year_summary), max_cols):
    cols = st.columns(max_cols)

    chunk = year_summary.iloc[i:i + max_cols]

    for col, (_, row) in zip(cols, chunk.iterrows()):
        col.metric(
            label=f"Jahr {int(row['year'])}",
            value=f"{row['sum']:,.0f} m³".replace("," ,"'"),
            delta=f"{row['mean']:,.1f} m³/Tag".replace("," ,"'")
        )

year_summary_source = (
    year_df.groupby("year")["Quellwasser_imNetz_absolut"]
    .agg(["mean", "sum"])
    .reset_index()
)

st.write(
    """Der Wasserverbrauch pro Jahr folgt einer Linie: im Hochsommer (Juli und August) und im Dezember 
    Wasser verbraucht als im Frühling und Herbst. Dies hängt mit dem starken Tourismus in der Gemeinde 
    Saanen zusammen. 
    """
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

fig_yearQW.update_yaxes(
    range=[0, df["Quellwasser_imNetz_absolut"].max()]
)

st.plotly_chart(fig_yearQW, use_container_width=True)

for i in range(0, len(year_summary_source), max_cols):
    cols = st.columns(max_cols)

    chunk = year_summary_source.iloc[i:i + max_cols]

    for col, (_, row) in zip(cols, chunk.iterrows()):
        col.metric(
            label=f"Jahr {int(row['year'])}",
            value=f"{row['sum']:,.0f} m³".replace(",", "'"),
            delta=f"{row['mean']:,.1f} m³/Tag".replace(",", "'")
        )


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
        tickvals=[15 ,45 ,75 ,115 ,135 ,165 ,195 ,225 ,255 ,285 ,315 ,345],
        ticktext=["Jan" ,"Feb" ,"Mrz" ,"Apr" ,"Mai" ,"Jun" ,"Jul" ,"Aug" ,"Sep" ,"Okt" ,"Nov" ,"Dez"]
    )
)

fig_yearGW.update_yaxes(
    range=[0, df["Grundwasser_imNetz_absolut"].max()]
)

st.plotly_chart(fig_yearGW, use_container_width=True)