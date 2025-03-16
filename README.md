# Thuisbatterij Calculator

Een tool om de rendabiliteit van een thuisbatterij te berekenen op basis van je energiedata.

## Beschrijving

Deze calculator analyseert je energiedata en berekent of het rendabel is om een thuisbatterij aan te schaffen. Het script simuleert verschillende batterijcapaciteiten en geeft inzicht in:

- Jaarlijkse besparingen
- Terugverdientijd
- Totale besparing over de levensduur van de batterij
- Optimale batterijgrootte voor jouw situatie

## Benodigdheden

- Python 3.6 of hoger
- De volgende Python bibliotheken:
  - pandas
  - numpy
  - matplotlib
  - PyQt5 (alleen voor de GUI versie)

Je kunt deze installeren met:

```
pip install -r requirements.txt
```

## Gebruiksaanwijzing

Er zijn twee manieren om de calculator te gebruiken:

### 1. Command Line versie

```
python thuisbatterij_calculator.py
```

### 2. Grafische interface (GUI)

```
python thuisbatterij_gui.py
```

De GUI versie biedt de volgende voordelen:
- Gemakkelijk aanpassen van tarieven en batterijparameters
- Selecteer eenvoudig welke batterijcapaciteiten je wilt simuleren
- Overzichtelijke weergave van de resultaten
- Mogelijkheid om grafieken te genereren voor specifieke batterijcapaciteiten

## Data Vereisten

Je energiedata moet beschikbaar zijn in CSV-formaat. De data moet de volgende kolommen bevatten:
- `time`: Tijdstip (datetime formaat)
- `Import T1 kWh`: Geïmporteerde energie tijdens tarief 1 (dagtarief)
- `Import T2 kWh`: Geïmporteerde energie tijdens tarief 2 (nachttarief)
- `Export T1 kWh`: Geëxporteerde energie tijdens tarief 1
- `Export T2 kWh`: Geëxporteerde energie tijdens tarief 2
- `L1 max W`, `L2 max W`, `L3 max W`: Maximaal vermogen per fase (optioneel)

## Aanpassen van parameters

### In de GUI versie:
Gebruik de invoervelden om de parameters aan te passen:
- Tarieven (dag, nacht, teruglever)
- Batterijkosten per kWh
- Levensduur van de batterij
- Laad/ontlaad efficiëntie
- Te simuleren batterijcapaciteiten

### In de command line versie:
Pas de volgende parameters aan in het script:
```python
calculator.tarief_dag = 0.30
calculator.tarief_nacht = 0.25
calculator.teruglever_tarief = 0.10
calculator.batterij_kosten_per_kwh = 400
calculator.batterij_levensduur = 10
calculator.laad_efficiëntie = 0.90
```

## Voorbeeld uitvoer

```
=== RESULTATEN THUISBATTERIJ ANALYSE ===
Capaciteit (kWh)  Jaarlijkse Besparing (€)    Investering (€)      Terugverdientijd (jaren)    Totale Besparing over Levensduur (€)
------------------------------------------------------------------------------------------------------------------------
3.0              120.50                      1200.00               9.96                        5.00
5.0              180.75                      2000.00               11.06                       -192.50
7.0              220.30                      2800.00               12.71                       -597.00
...

=== AANBEVELING ===
De optimale batterijcapaciteit is 3 kWh met een terugverdientijd van 9.96 jaar.
Na 10 jaar levert dit een totale besparing op van € 5.00.
```

## Grafische weergave

Het script genereert ook grafieken die laten zien:
- De laadstatus van de batterij over tijd
- De cumulatieve kosten met en zonder batterij

## Opmerkingen

- De berekeningen zijn gebaseerd op historische gegevens en geven een indicatie. Werkelijke besparingen kunnen variëren.
- De calculator gaat uit van een constant teruglevertarief, maar dit kan in de toekomst veranderen.
- Batterijprijzen dalen over tijd, dus in de toekomst kan een batterij rendabeler worden.
- De berekening houdt geen rekening met eventuele subsidies voor thuisbatterijen. 