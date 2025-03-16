import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

class ThuisbatterijCalculator:
    def __init__(self, csv_file):
        """
        Initialiseer de calculator met een CSV bestand van energiedata.
        
        Parameters:
        csv_file (str): Pad naar het CSV bestand met de energiedata.
        """
        self.csv_file = csv_file
        self.data = None
        self.batterij_resultaten = {}
        
        # Laadtarief parameters
        self.tarief_dag = 0.30  # prijs per kWh overdag (€)
        self.tarief_nacht = 0.25  # prijs per kWh 's nachts (€)
        self.teruglever_tarief = 0.10  # teruglevertarief per kWh (€)
        
        # Batterij parameters
        self.batterij_kosten_per_kwh = 400  # aanschafkosten per kWh batterijcapaciteit (€)
        self.batterij_levensduur = 10  # levensduur in jaren
        self.laad_efficiëntie = 0.90  # laad- en ontlaadefficiëntie (90%)
        
    def laad_data(self):
        """Laad de energiedata uit het CSV bestand."""
        try:
            print(f"Data laden uit: {self.csv_file}")
            self.data = pd.read_csv(self.csv_file)
            
            # Converteer de tijdkolom naar datetime
            self.data['time'] = pd.to_datetime(self.data['time'])
            
            # Bereken het werkelijke verbruik en productie per interval
            self.bereken_interval_waarden()
            
            print(f"Succesvol {len(self.data)} datapunten geladen.")
            return True
        except Exception as e:
            print(f"Fout bij het laden van de data: {e}")
            return False
    
    def bereken_interval_waarden(self):
        """Bereken het verbruik en productie per tijdsinterval."""
        # Maak kopieën van de cumulatieve waarden
        self.data['import_t1_interval'] = self.data['Import T1 kWh'].diff().fillna(0)
        self.data['import_t2_interval'] = self.data['Import T2 kWh'].diff().fillna(0)
        self.data['export_t1_interval'] = self.data['Export T1 kWh'].diff().fillna(0)
        self.data['export_t2_interval'] = self.data['Export T2 kWh'].diff().fillna(0)
        
        # Totaal import en export per interval
        self.data['totaal_import'] = self.data['import_t1_interval'] + self.data['import_t2_interval']
        self.data['totaal_export'] = self.data['export_t1_interval'] + self.data['export_t2_interval']
        
        # Bepaal dag/nacht tarief (aanname: 7-23 uur is dagtarief)
        self.data['is_dagtarief'] = (self.data['time'].dt.hour >= 7) & (self.data['time'].dt.hour < 23)
        
        # Bereken kosten zonder batterij
        import_kosten = np.where(
            self.data['is_dagtarief'],
            self.data['totaal_import'] * self.tarief_dag,
            self.data['totaal_import'] * self.tarief_nacht
        )
        export_opbrengst = self.data['totaal_export'] * self.teruglever_tarief
        
        self.data['netto_kosten'] = import_kosten - export_opbrengst
    
    def simuleer_batterij(self, capaciteiten=[3, 5, 7, 10, 15]):
        """
        Simuleer verschillende batterijcapaciteiten en bereken de rendabiliteit.
        
        Parameters:
        capaciteiten (list): Lijst met te simuleren batterijcapaciteiten in kWh.
        """
        if self.data is None:
            print("Laad eerst de data met de laad_data() methode.")
            return
        
        for capaciteit in capaciteiten:
            resultaat = self.simuleer_enkele_batterij(capaciteit)
            self.batterij_resultaten[capaciteit] = resultaat
    
    def simuleer_enkele_batterij(self, capaciteit):
        """
        Simuleer een enkele batterij en bereken de besparing.
        
        Parameters:
        capaciteit (float): Capaciteit van de batterij in kWh.
        
        Returns:
        dict: Resultaten van de simulatie.
        """
        # Maak een kopie van de data om mee te werken
        sim_data = self.data.copy()
        
        # Initialiseer batterij lading (50% om te beginnen)
        batterij_lading = capaciteit * 0.5
        
        # Arrays voor bijhouden van batterijstatus en besparingen
        batterij_laadstatus = []
        originele_kosten = []
        nieuwe_kosten = []
        
        for idx, rij in sim_data.iterrows():
            # Sla originele kosten op
            originele_kosten.append(rij['netto_kosten'])
            
            # Bepaal het tarief voor dit interval
            tarief = self.tarief_dag if rij['is_dagtarief'] else self.tarief_nacht
            
            # Bereken netto verbruik (positief = import, negatief = export)
            netto_verbruik = rij['totaal_import'] - rij['totaal_export']
            
            # Simuleer batterijgedrag
            if netto_verbruik > 0:  # We verbruiken meer dan we produceren
                # Ontlaad de batterij indien mogelijk
                energie_uit_batterij = min(netto_verbruik, batterij_lading)
                batterij_lading -= energie_uit_batterij
                
                # Resterende energie moet worden geïmporteerd
                resterende_import = netto_verbruik - energie_uit_batterij
                nieuwe_kost = resterende_import * tarief
            else:  # We produceren meer dan we verbruiken
                # Laad de batterij indien mogelijk
                beschikbare_energie = -netto_verbruik * self.laad_efficiëntie
                energie_naar_batterij = min(beschikbare_energie, capaciteit - batterij_lading)
                batterij_lading += energie_naar_batterij
                
                # Resterende energie wordt geëxporteerd
                resterende_export = -netto_verbruik - (energie_naar_batterij / self.laad_efficiëntie)
                nieuwe_kost = -resterende_export * self.teruglever_tarief
            
            nieuwe_kosten.append(nieuwe_kost)
            batterij_laadstatus.append(batterij_lading)
        
        # Bereken totale besparing
        totale_originele_kosten = sum(originele_kosten)
        totale_nieuwe_kosten = sum(nieuwe_kosten)
        jaarlijkse_besparing = totale_originele_kosten - totale_nieuwe_kosten
        
        # Bereken ROI
        batterij_investering = capaciteit * self.batterij_kosten_per_kwh
        terugverdientijd = batterij_investering / jaarlijkse_besparing if jaarlijkse_besparing > 0 else float('inf')
        totale_besparing_levensduur = jaarlijkse_besparing * self.batterij_levensduur - batterij_investering
        
        return {
            'capaciteit': capaciteit,
            'jaarlijkse_besparing': jaarlijkse_besparing,
            'batterij_investering': batterij_investering,
            'terugverdientijd': terugverdientijd,
            'totale_besparing_levensduur': totale_besparing_levensduur,
            'batterij_laadstatus': batterij_laadstatus,
            'originele_kosten': originele_kosten,
            'nieuwe_kosten': nieuwe_kosten
        }
    
    def toon_resultaten(self):
        """Toon de resultaten van de batterijsimulatie."""
        if not self.batterij_resultaten:
            print("Voer eerst een simulatie uit met de simuleer_batterij() methode.")
            return
        
        print("\n=== RESULTATEN THUISBATTERIJ ANALYSE ===")
        print(f"{'Capaciteit (kWh)':<15} {'Jaarlijkse Besparing (€)':<25} {'Investering (€)':<20} {'Terugverdientijd (jaren)':<25} {'Totale Besparing over Levensduur (€)':<35}")
        print("-" * 120)
        
        beste_roi = None
        beste_capaciteit = None
        
        for capaciteit, resultaat in sorted(self.batterij_resultaten.items()):
            print(f"{resultaat['capaciteit']:<15.1f} {resultaat['jaarlijkse_besparing']:<25.2f} {resultaat['batterij_investering']:<20.2f} {resultaat['terugverdientijd']:<25.2f} {resultaat['totale_besparing_levensduur']:<35.2f}")
            
            # Bepaal de beste ROI
            if beste_roi is None or (resultaat['terugverdientijd'] < beste_roi and resultaat['terugverdientijd'] > 0):
                beste_roi = resultaat['terugverdientijd']
                beste_capaciteit = capaciteit
        
        print("\n=== AANBEVELING ===")
        if beste_capaciteit is not None and beste_roi < self.batterij_levensduur:
            print(f"De optimale batterijcapaciteit is {beste_capaciteit} kWh met een terugverdientijd van {beste_roi:.2f} jaar.")
            print(f"Na {self.batterij_levensduur} jaar levert dit een totale besparing op van € {self.batterij_resultaten[beste_capaciteit]['totale_besparing_levensduur']:.2f}.")
        else:
            print("Gebaseerd op je huidige energieprofiel en de huidige kosten, is een thuisbatterij niet rendabel binnen de levensduur.")
            print("Overweeg om te wachten tot batterijprijzen verder dalen of het teruglevertarief verder afneemt.")
    
    def visualiseer_resultaten(self, capaciteit=None):
        """
        Visualiseer de resultaten van de batterijsimulatie.
        
        Parameters:
        capaciteit (float, optional): Specifieke capaciteit om te visualiseren. 
                                    Als None, wordt de meest rendabele getoond.
        """
        if not self.batterij_resultaten:
            print("Voer eerst een simulatie uit met de simuleer_batterij() methode.")
            return
        
        # Als geen capaciteit is opgegeven, gebruik de meest rendabele
        if capaciteit is None:
            beste_roi = float('inf')
            for cap, res in self.batterij_resultaten.items():
                if 0 < res['terugverdientijd'] < beste_roi:
                    beste_roi = res['terugverdientijd']
                    capaciteit = cap
            
            # Als er geen rendabele optie is, gebruik de eerste
            if capaciteit is None:
                capaciteit = list(self.batterij_resultaten.keys())[0]
        
        # Controleer of de opgegeven capaciteit bestaat
        if capaciteit not in self.batterij_resultaten:
            print(f"Capaciteit {capaciteit} kWh is niet gesimuleerd.")
            return
        
        resultaat = self.batterij_resultaten[capaciteit]
        
        # Maak een nieuwe plot
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Laadstatus van de batterij
        plt.subplot(2, 1, 1)
        tijden = self.data['time'].iloc[:len(resultaat['batterij_laadstatus'])]
        plt.plot(tijden, resultaat['batterij_laadstatus'], label=f'Batterijlading ({capaciteit} kWh)')
        plt.axhline(y=capaciteit, color='r', linestyle='--', label='Max capaciteit')
        plt.title(f'Batterijlading over tijd - {capaciteit} kWh capaciteit')
        plt.ylabel('Lading (kWh)')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Vergelijking kosten
        plt.subplot(2, 1, 2)
        plt.plot(tijden, np.cumsum(resultaat['originele_kosten']), label='Zonder batterij')
        plt.plot(tijden, np.cumsum(resultaat['nieuwe_kosten']), label='Met batterij')
        plt.title('Cumulatieve energiekosten')
        plt.xlabel('Tijd')
        plt.ylabel('Cumulatieve kosten (€)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'batterij_simulatie_{capaciteit}kWh.png')
        plt.show()
        
        # Toon ROI statistieken
        print(f"\n=== ROI ANALYSE VOOR {capaciteit} kWh BATTERIJ ===")
        print(f"Jaarlijkse besparing: € {resultaat['jaarlijkse_besparing']:.2f}")
        print(f"Investering: € {resultaat['batterij_investering']:.2f}")
        print(f"Terugverdientijd: {resultaat['terugverdientijd']:.2f} jaar")
        print(f"Totale besparing over {self.batterij_levensduur} jaar: € {resultaat['totale_besparing_levensduur']:.2f}")

# Eenvoudig voorbeeld van gebruik
if __name__ == "__main__":
    # Pad naar de CSV file
    csv_file = "P1e-2024-3-14-2025-3-14.csv"
    
    # Maak een nieuwe calculator en laad de data
    calculator = ThuisbatterijCalculator(csv_file)
    if calculator.laad_data():
        # Pas eventueel tarieven aan
        calculator.tarief_dag = 0.30
        calculator.tarief_nacht = 0.25
        calculator.teruglever_tarief = 0.10
        calculator.batterij_kosten_per_kwh = 400
        
        # Simuleer verschillende batterijgroottes
        calculator.simuleer_batterij([3, 5, 7, 10, 15, 20])
        
        # Toon de resultaten
        calculator.toon_resultaten()
        
        # Visualiseer de resultaten voor de batterij met de beste ROI
        calculator.visualiseer_resultaten() 