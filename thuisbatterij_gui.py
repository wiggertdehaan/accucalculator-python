import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, 
                            QComboBox, QMessageBox, QCheckBox, QListWidget, QTextEdit)
from PyQt5.QtCore import Qt
from thuisbatterij_calculator import ThuisbatterijCalculator

class ThuisbatterijGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thuisbatterij Calculator")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialiseer de calculator
        self.calculator = None
        self.csv_file = None
        
        # Maak de centrale widget en layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Maak de GUI componenten
        self.maak_bestandsselectie()
        self.maak_tarief_instellingen()
        self.maak_batterij_instellingen()
        self.maak_simulatie_instellingen()
        self.maak_resultaten_weergave()
        
        # Voeg een knop toe om de simulatie te starten
        self.start_button = QPushButton("Start Simulatie")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_simulatie)
        self.main_layout.addWidget(self.start_button)
    
    def maak_bestandsselectie(self):
        """Maak de bestandsselectie sectie"""
        # Groepeer de bestandsselectie componenten
        bestand_group = QGroupBox("Data Selectie")
        bestand_layout = QHBoxLayout()
        
        # Label en veld voor bestandspad
        self.bestand_label = QLabel("CSV Bestand:")
        self.bestand_veld = QLineEdit()
        self.bestand_veld.setReadOnly(True)
        
        # Knop om bestand te selecteren
        self.bestand_knop = QPushButton("Selecteer Bestand")
        self.bestand_knop.clicked.connect(self.selecteer_bestand)
        
        # Voeg alles toe aan de layout
        bestand_layout.addWidget(self.bestand_label)
        bestand_layout.addWidget(self.bestand_veld)
        bestand_layout.addWidget(self.bestand_knop)
        bestand_group.setLayout(bestand_layout)
        
        # Voeg de groep toe aan de main layout
        self.main_layout.addWidget(bestand_group)
    
    def maak_tarief_instellingen(self):
        """Maak de tarief instellingen sectie"""
        # Groepeer de tarief componenten
        tarief_group = QGroupBox("Tarief Instellingen")
        tarief_layout = QHBoxLayout()
        
        # Componenten voor dag tarief
        self.dag_label = QLabel("Dagtarief (€/kWh):")
        self.dag_veld = QLineEdit("0.30")
        
        # Componenten voor nacht tarief
        self.nacht_label = QLabel("Nachttarief (€/kWh):")
        self.nacht_veld = QLineEdit("0.25")
        
        # Componenten voor teruglever tarief
        self.teruglever_label = QLabel("Teruglevertarief (€/kWh):")
        self.teruglever_veld = QLineEdit("0.10")
        
        # Voeg alles toe aan de layout
        tarief_layout.addWidget(self.dag_label)
        tarief_layout.addWidget(self.dag_veld)
        tarief_layout.addWidget(self.nacht_label)
        tarief_layout.addWidget(self.nacht_veld)
        tarief_layout.addWidget(self.teruglever_label)
        tarief_layout.addWidget(self.teruglever_veld)
        tarief_group.setLayout(tarief_layout)
        
        # Voeg de groep toe aan de main layout
        self.main_layout.addWidget(tarief_group)
    
    def maak_batterij_instellingen(self):
        """Maak de batterij instellingen sectie"""
        # Groepeer de batterij componenten
        batterij_group = QGroupBox("Batterij Instellingen")
        batterij_layout = QHBoxLayout()
        
        # Componenten voor batterij kosten
        self.batterij_kosten_label = QLabel("Batterijkosten (€/kWh):")
        self.batterij_kosten_veld = QLineEdit("400")
        
        # Componenten voor levensduur
        self.levensduur_label = QLabel("Levensduur (jaren):")
        self.levensduur_veld = QLineEdit("10")
        
        # Componenten voor laad efficiëntie
        self.efficientie_label = QLabel("Laad/ontlaad efficiëntie (%):")
        self.efficientie_veld = QLineEdit("90")
        
        # Voeg alles toe aan de layout
        batterij_layout.addWidget(self.batterij_kosten_label)
        batterij_layout.addWidget(self.batterij_kosten_veld)
        batterij_layout.addWidget(self.levensduur_label)
        batterij_layout.addWidget(self.levensduur_veld)
        batterij_layout.addWidget(self.efficientie_label)
        batterij_layout.addWidget(self.efficientie_veld)
        batterij_group.setLayout(batterij_layout)
        
        # Voeg de groep toe aan de main layout
        self.main_layout.addWidget(batterij_group)
    
    def maak_simulatie_instellingen(self):
        """Maak de simulatie instellingen sectie"""
        # Groepeer de simulatie componenten
        simulatie_group = QGroupBox("Simulatie Instellingen")
        simulatie_layout = QVBoxLayout()
        
        # Instructie label
        instructie_label = QLabel("Selecteer de batterijcapaciteiten om te simuleren (in kWh):")
        
        # Horizontale layout voor de capaciteiten checkboxes
        capaciteiten_layout = QHBoxLayout()
        
        # Voeg checkboxes toe voor verschillende batterijgroottes
        self.capaciteit_checks = {}
        for capaciteit in [3, 5, 7, 10, 15, 20]:
            checkbox = QCheckBox(str(capaciteit))
            checkbox.setChecked(True)
            self.capaciteit_checks[capaciteit] = checkbox
            capaciteiten_layout.addWidget(checkbox)
        
        # Voeg alles toe aan de simulatie layout
        simulatie_layout.addWidget(instructie_label)
        simulatie_layout.addLayout(capaciteiten_layout)
        simulatie_group.setLayout(simulatie_layout)
        
        # Voeg de groep toe aan de main layout
        self.main_layout.addWidget(simulatie_group)
    
    def maak_resultaten_weergave(self):
        """Maak de resultaten weergave sectie"""
        # Groepeer de resultaten componenten
        resultaten_group = QGroupBox("Resultaten")
        resultaten_layout = QVBoxLayout()
        
        # Tekstgebied voor resultaten
        self.resultaten_tekst = QTextEdit()
        self.resultaten_tekst.setReadOnly(True)
        resultaten_layout.addWidget(self.resultaten_tekst)
        
        # Voeg horizontale layout toe voor knoppen onder resultaten
        knoppen_layout = QHBoxLayout()
        
        # Knop om resultaten te visualiseren
        self.visualiseer_knop = QPushButton("Visualiseer Resultaten")
        self.visualiseer_knop.setEnabled(False)
        self.visualiseer_knop.clicked.connect(self.visualiseer_resultaten)
        knoppen_layout.addWidget(self.visualiseer_knop)
        
        # Selectiecombobox voor visualisatie van specifieke capaciteit
        self.visualiseer_combobox = QComboBox()
        self.visualiseer_combobox.setEnabled(False)
        knoppen_layout.addWidget(self.visualiseer_combobox)
        
        # Toevoegen van de knoppen layout aan de resultaten layout
        resultaten_layout.addLayout(knoppen_layout)
        resultaten_group.setLayout(resultaten_layout)
        
        # Voeg de groep toe aan de main layout
        self.main_layout.addWidget(resultaten_group)
    
    def selecteer_bestand(self):
        """Opent een bestandsdialoog om een CSV bestand te selecteren"""
        bestandspad, _ = QFileDialog.getOpenFileName(
            self, "Selecteer CSV Bestand", "", "CSV Bestanden (*.csv)"
        )
        
        if bestandspad:
            self.csv_file = bestandspad
            self.bestand_veld.setText(bestandspad)
            self.start_button.setEnabled(True)
    
    def start_simulatie(self):
        """Start de batterijsimulatie met de ingestelde parameters"""
        # Controleer of er een bestand is geselecteerd
        if not self.csv_file:
            QMessageBox.warning(self, "Waarschuwing", "Selecteer eerst een CSV bestand.")
            return
        
        # Maak een nieuwe calculator
        self.calculator = ThuisbatterijCalculator(self.csv_file)
        
        # Lees de tarief instellingen
        try:
            self.calculator.tarief_dag = float(self.dag_veld.text().replace(',', '.'))
            self.calculator.tarief_nacht = float(self.nacht_veld.text().replace(',', '.'))
            self.calculator.teruglever_tarief = float(self.teruglever_veld.text().replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Waarschuwing", "Ongeldige tariefwaarden. Gebruik numerieke waarden.")
            return
        
        # Lees de batterij instellingen
        try:
            self.calculator.batterij_kosten_per_kwh = float(self.batterij_kosten_veld.text().replace(',', '.'))
            self.calculator.batterij_levensduur = float(self.levensduur_veld.text().replace(',', '.'))
            self.calculator.laad_efficiëntie = float(self.efficientie_veld.text().replace(',', '.')) / 100
        except ValueError:
            QMessageBox.warning(self, "Waarschuwing", "Ongeldige batterijwaarden. Gebruik numerieke waarden.")
            return
        
        # Bepaal welke capaciteiten gesimuleerd moeten worden
        te_simuleren = [cap for cap, check in self.capaciteit_checks.items() if check.isChecked()]
        if not te_simuleren:
            QMessageBox.warning(self, "Waarschuwing", "Selecteer minstens één batterijcapaciteit.")
            return
        
        # Laad de data en voer de simulatie uit
        self.resultaten_tekst.clear()
        self.resultaten_tekst.append("Data laden en simulatie uitvoeren...")
        QApplication.processEvents()  # Update de UI
        
        if self.calculator.laad_data():
            self.calculator.simuleer_batterij(te_simuleren)
            
            # Weergeef de resultaten
            self.toon_resultaten()
            
            # Activeer de visualisatie knop
            self.visualiseer_knop.setEnabled(True)
            
            # Vul de combobox met de gesimuleerde capaciteiten
            self.visualiseer_combobox.clear()
            for cap in sorted(self.calculator.batterij_resultaten.keys()):
                self.visualiseer_combobox.addItem(f"{cap} kWh", cap)
            self.visualiseer_combobox.setEnabled(True)
        else:
            self.resultaten_tekst.append("Fout bij het laden van de data. Controleer het CSV bestand.")
    
    def toon_resultaten(self):
        """Toont de resultaten van de simulatie in het tekstgebied"""
        if not self.calculator or not self.calculator.batterij_resultaten:
            return
        
        self.resultaten_tekst.clear()
        
        # Tabel header
        self.resultaten_tekst.append("=== RESULTATEN THUISBATTERIJ ANALYSE ===\n")
        header = "{:<15} {:<25} {:<20} {:<25} {:<35}".format(
            "Capaciteit (kWh)", "Jaarlijkse Besparing (€)", "Investering (€)", 
            "Terugverdientijd (jaren)", "Totale Besparing over Levensduur (€)"
        )
        self.resultaten_tekst.append(header)
        self.resultaten_tekst.append("-" * 120)
        
        # Toon de resultaten voor elke gesimuleerde capaciteit
        beste_roi = None
        beste_capaciteit = None
        
        for capaciteit, resultaat in sorted(self.calculator.batterij_resultaten.items()):
            rij = "{:<15.1f} {:<25.2f} {:<20.2f} {:<25.2f} {:<35.2f}".format(
                resultaat['capaciteit'],
                resultaat['jaarlijkse_besparing'],
                resultaat['batterij_investering'],
                resultaat['terugverdientijd'],
                resultaat['totale_besparing_levensduur']
            )
            self.resultaten_tekst.append(rij)
            self.resultaten_tekst.append("")  # Extra lege regel
            
            # Bepaal de beste ROI
            if beste_roi is None or (resultaat['terugverdientijd'] < beste_roi and resultaat['terugverdientijd'] > 0):
                beste_roi = resultaat['terugverdientijd']
                beste_capaciteit = capaciteit
        
        # Toon aanbeveling
        self.resultaten_tekst.append("\n=== AANBEVELING ===")
        if beste_capaciteit is not None and beste_roi < self.calculator.batterij_levensduur:
            levensduur_besparing = self.calculator.batterij_resultaten[beste_capaciteit]['totale_besparing_levensduur']
            self.resultaten_tekst.append(
                f"De optimale batterijcapaciteit is {beste_capaciteit} kWh met een terugverdientijd van {beste_roi:.2f} jaar."
            )
            self.resultaten_tekst.append(
                f"Na {self.calculator.batterij_levensduur} jaar levert dit een totale besparing op van € {levensduur_besparing:.2f}."
            )
        else:
            self.resultaten_tekst.append(
                "Gebaseerd op je huidige energieprofiel en de huidige kosten, is een thuisbatterij niet rendabel binnen de levensduur."
            )
            self.resultaten_tekst.append(
                "Overweeg om te wachten tot batterijprijzen verder dalen of het teruglevertarief verder afneemt."
            )
    
    def visualiseer_resultaten(self):
        """Visualiseert de resultaten voor de geselecteerde capaciteit"""
        if not self.calculator or not self.calculator.batterij_resultaten:
            return
        
        # Haal de geselecteerde capaciteit op uit de combobox
        geselecteerde_capaciteit = self.visualiseer_combobox.currentData()
        
        # Visualiseer de resultaten
        self.calculator.visualiseer_resultaten(geselecteerde_capaciteit)

# Start de applicatie als het script direct wordt uitgevoerd
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThuisbatterijGUI()
    window.show()
    sys.exit(app.exec_()) 