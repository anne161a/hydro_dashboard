import streamlit as st

st.set_page_config(
    page_title="Hydrologie Dashboard",
    layout="wide"
)

st.title("Hydrologisches Dashboard Saanen")

st.header("Einleitung")

st.write("""Wasser ist eine der wichtigsten Ressourcen. Die Trinkwasserversorgung wird daher als kritische 
Infrastruktur angesehen (BWL, 2021, S.2) und ihre Sicherstellung stellt eine der zentralen Aufgaben für das Gemeinwohl 
der Bevölkerung dar. 

Die Gemeinde Saanen im Berner Oberland bietet hierfür ein aufschlussreiches Beispiel. Ihre Trinkwasserversorgung basiert 
auf einem dualen System, das sowohl Quell- als auch Grundwasser verwendet.

Die vorliegende Arbeit untersucht die Trinkwasserversorgung der Gemeinde Saanen hinsichtlich seiner Resilienz sowie der 
Frage, wie das Zusammenspiel von Quell- und Grundwasser zu einer stabilen Versorgung beiträgt. 
""")

st.header("Über die Gemeinde")

st.write("""
- Anzahl ständige Wohnbevölkerung: 7'603
- Saisonale Schwankungen der Wohnbevölerung: ca. 350 Arbeitskräfte
- Wochenaufenthalter: ca. 220
- Anzahl Haushalte: 3'547

Saanen hat in Winter- und Sommersaison viele Tourist:innen. Circa 30'000 Menschen halten sich während
Winter- und Sommersaison in der Gemeinde auf. 

Saanen ist mit rund 12'000 Hektaren flächenmässig die 8. grösste Gemeinde des Kantons Bern. Knapp über die Hälfte
der Fläche wird landwirtschaftlich genutzt (Gemeinde in Zahlen, o. J.). 


""")

st.header("Forschungsfrage")

st.write("""
Untersucht wird, wie resilient das duale Wasserversorgungssystem der Gemeinde Saanen gegenüber Schwankungen der 
Grundwasserverfügbarkeit ist. Dabei wird analysiert, inwiefern die Kombination aus Grund- und Quellwasser die 
Wasserversorgungssicherheit im trockenen Jahr 2022 gewährleistet.
""")

with st.expander("Was bedeutet Resilienz?"):
    st.write("""Resilienz ist die Fähigkeit eines Systems, Herausforderungen standzuhalten und weiterhin ein 
    Mindestmass an Funktionalität zu gewähren. Ein resilientes System kann Belastungen aushalten, sich anpassen und 
    sich nach Problemen wieder erholen (EBP, o. J.). 
    
Auf die Wasserversorgung bezogen bedeutet dies, dass das System auch in extremen Situationen wie Trockenheit oder 
Hitze zuverlässig Wasser bereitstellt (DVGW, o. J.). 
""")

with st.expander("Was ist ein duales Wasserversorgungssystem?"):
    st.write("""Das duale Wasserversorgungssystem, auch «Prinzip der zwei Standbeine» genannt, hat das Ziel, die 
    Wasserversorgungssicherheit zu erhöhen. Dabei wird Wasser aus zwei hydrogeologisch unabhängigen Bezugsorten 
    gewonnen, welche den mittleren Bedarf abdecken. 
    
D.h. fällt eine Quelle aufgrund von Trockenheit, technischen Problemen oder Verunreinigungen teilweise oder vollständig 
aus, kann die zweite Quelle die Versorgung weiterhin sicherstellen. Dadurch wird die Ausfallsicherheit des gesamten 
Systems erhöht.

    """)

st.header("Datengrundlage")

st.write("""
Die Analyse basiert auf hydrologischen und meteorologischen Daten der Gemeinde Saanen: 
-	Meteorologische Daten von Château d’Oex
-	Daten zum Grundwasserstand seit 1979 mit einzelnen Datenlücken 
-	Daten zum Wasserverbrauch im Netz seit 2020 inklusive der Anteile von Quell- und Grundwasser 
-	Konzessionierte Menge der Grundwasserfassungen 
-	Speicherkapazität der Reservoire 

""")

st.header("Methodik")

st.write("""
Die in der Datengrundlage genannten Datensätze werden in Python verarbeitet. Zur Verarbeitung der CSV-Dateien 
wird die Bibliothek Pandas eingesetzt. Die Diagramme werden mit Plotly Express erstellt und in einem interaktiven 
Streamlit Dashboard visualisiert. Dadurch lassen sich saisonale Schwankungen sowie Zusammenhänge zwischen Niederschlag, 
Grundwasserstand, Wasserverbrauch und Wasserverfügbarkeit visualisieren. 
Zur Beurteilung der Resilienz des Wasserversorgungssystems werden mögliche Szenarien simuliert, welche den 
Reservoirfüllstand sowie die Leistung der Pumpen beeinflussen. Dabei wird berechnet, ab welchem Punkt ein erstes 
Versorgungsdefizit auftritt – abhängig vom Reservoirfüllstand und des Pumpausfalls. 

""")



