from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

from konfiguracja import StanProcesu
from obiekty import Zbiornik, Pompa, Grzalka, Rura

class SCADA_System(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System SCADA: Mieszalnik V5.0")
        self.setFixedSize(1000, 750)
        self.setStyleSheet("background-color: #2c3e50;")
        
        self.stan = StanProcesu.STOP
        self.tryb_auto = True
        self.czy_pauza = False
        
        self.init_objects()
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)

    def init_objects(self):
        # Inicjalizacja obiektów (bez zmian)
        self.z1 = Zbiornik(50, 50, 100, 150, "T1: Surowiec A", poj=100)
        self.z1.aktualna_ilosc = 100
        self.z2 = Zbiornik(850, 50, 100, 150, "T2: Surowiec B", poj=100)
        self.z2.aktualna_ilosc = 100
        self.z3 = Zbiornik(400, 250, 200, 200, "T3: Reaktor", poj=200)
        self.z4 = Zbiornik(400, 550, 200, 100, "T4: Produkt", poj=200)
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self.p1 = Pompa(180, 150, "P1")
        self.p2 = Pompa(780, 150, "P2")
        self.p3 = Pompa(350, 480, "P3")
        self.pompy = [self.p1, self.p2, self.p3]
        
        self.grzalka = Grzalka(450, 400, "G1")
        
        self.rura1 = Rura([(100, 200), (100, 220), (200, 220), (200, 170), (450, 170), (450, 250)])
        self.rura2 = Rura([(900, 200), (900, 220), (800, 220), (800, 170), (550, 170), (550, 250)])
        self.rura3 = Rura([(500, 450), (500, 500), (370, 500), (370, 520), (500, 520), (500, 550)])
        self.rury = [self.rura1, self.rura2, self.rura3]

    def setup_ui(self):
        # Konfiguracja przycisków 
        self.lbl_info = QLabel("STAN: STOP", self)
        self.lbl_info.setGeometry(20, 680, 400, 30)
        self.lbl_info.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        # Przyciski dolne
        btns_config = [
            ("START AUTO", 380, self.start_procesu, "#27ae60"),
            ("PAUZA", 510, self.przelacz_pauze, "#f39c12"),
            ("TRYB: AUTO", 620, self.zmien_tryb, "#2980b9"),
            ("RESET", 750, self.reset_symulacji, "#c0392b")
        ]
        
        for text, x, func, color in btns_config:
            btn = QPushButton(text, self)
            btn.setGeometry(x, 680, 120 if "TRYB" in text or "START" in text else 100, 40)
            btn.setStyleSheet(f"background-color: {color}; color: white;")
            btn.clicked.connect(func)
            if "PAUZA" in text: self.btn_pauza = btn
            if "TRYB" in text: self.btn_tryb = btn

        # Przyciski boczne (Manualne)
        self.lbl_manual = QLabel("STEROWANIE RĘCZNE:", self)
        self.lbl_manual.setGeometry(870, 460, 120, 20)
        self.lbl_manual.setStyleSheet("color: #aaa; font-size: 10px;")

        self.btn_p1 = self.create_manual_btn("P1", 490, self.p1)
        self.btn_p2 = self.create_manual_btn("P2", 530, self.p2)
        self.btn_grzalka = self.create_manual_btn("GRZAŁKA", 570, self.grzalka)
        self.btn_p3 = self.create_manual_btn("P3", 610, self.p3)
        
        self.aktualizuj_wyglad_manualny()

    def create_manual_btn(self, text, y, obj):
        btn = QPushButton(text, self)
        btn.setGeometry(870, y, 100, 30)
        btn.clicked.connect(lambda: self.steruj_recznie(obj))
        return btn

    # --- LOGIKA UI ---
    def start_procesu(self):
        if self.tryb_auto:
            self.stan = StanProcesu.DOZOWANIE
            self.czy_pauza = False
            self.btn_pauza.setText("PAUZA")

    def przelacz_pauze(self):
        self.czy_pauza = not self.czy_pauza
        text = "WZNÓW" if self.czy_pauza else "PAUZA"
        self.btn_pauza.setText(text)
        if self.czy_pauza: self.lbl_info.setText("STAN: WSTRZYMANY")

    def zmien_tryb(self):
        self.tryb_auto = not self.tryb_auto
        if self.tryb_auto:
            self.btn_tryb.setText("TRYB: AUTO")
            self.btn_tryb.setStyleSheet("background-color: #2980b9; color: white;")
            self.lbl_info.setText("Przełączono na AUTO")
            # Wyłącz wszystko
            for dev in self.pompy + [self.grzalka]: dev.aktywna = False
        else:
            self.btn_tryb.setText("TRYB: RĘCZNY")
            self.btn_tryb.setStyleSheet("background-color: #8e44ad; color: white;")
            self.lbl_info.setText("Sterowanie RĘCZNE")
            self.stan = StanProcesu.STOP
        self.aktualizuj_wyglad_manualny()

    def steruj_recznie(self, urzadzenie):
        if not self.tryb_auto:
            urzadzenie.przelacz()
            self.aktualizuj_wyglad_manualny()

    def aktualizuj_wyglad_manualny(self):
        pairs = [(self.btn_p1, self.p1), (self.btn_p2, self.p2), 
                 (self.btn_p3, self.p3), (self.btn_grzalka, self.grzalka)]
        
        for btn, dev in pairs:
            if self.tryb_auto:
                btn.setEnabled(False)
                btn.setStyleSheet("background-color: #34495e; color: #7f8c8d; border: 1px solid #555;")
                btn.setText(f"{dev.nazwa}: AUTO")
            else:
                btn.setEnabled(True)
                if dev.aktywna:
                    btn.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
                    btn.setText(f"{dev.nazwa}: WYŁĄCZ")
                else:
                    btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                    btn.setText(f"{dev.nazwa}: WŁĄCZ")

    def reset_symulacji(self):
        self.stan = StanProcesu.STOP
        self.tryb_auto = True
        self.czy_pauza = False
        self.z1.aktualna_ilosc = 100
        self.z2.aktualna_ilosc = 100
        self.z3.aktualna_ilosc = 0
        self.z3.temperatura = 20
        self.z4.aktualna_ilosc = 0
        self.z4.temperatura = 20
        for dev in self.pompy + [self.grzalka]: dev.aktywna = False
        self.zmien_tryb()
        self.zmien_tryb() 
        self.update()

    # funkcje pomocnicze
    
    def obsluz_transfer(self, pompa, rura, z_zrodlo, z_cel, szybkosc, mieszaj_temp=False):
        """Uniwersalna funkcja do obsługi przepływu cieczy"""
        dziala = False
        # Warunki: Pompa aktywna + Źródło ma płyn + Cel ma miejsce
        if pompa.aktywna and not z_zrodlo.czy_pusty() and not z_cel.czy_pelny():
            rura.plynie = True
            z_zrodlo.zmien_ilosc(-szybkosc)
            z_cel.zmien_ilosc(szybkosc)
            dziala = True
            
            # Mieszanie temperatury (tylko gdy wlewamy do Z4)
            if mieszaj_temp:
                z_cel.temperatura = (z_cel.temperatura * 0.9) + (z_zrodlo.temperatura * 0.1)
        else:
            rura.plynie = False
            
        return dziala

    def obsluz_grzanie(self):
        """Obsługa fizyki grzałki i bezpiecznika"""
        if self.grzalka.aktywna:
            if self.grzalka.temperatura > self.z3.temperatura:
                self.z3.temperatura += 0.2
            
            # Bezpiecznik 60 stopni
            if self.z3.temperatura >= 60.0:
                self.z3.temperatura = 60.0
                self.grzalka.aktywna = False
                self.aktualizuj_wyglad_manualny()

    # --- GŁÓWNA PĘTLA SYMULACJI ---

    def update_simulation(self):
        if self.czy_pauza: return

        if not self.tryb_auto:
            self.logika_reczna()
        else:
            self.logika_auto()
            
        self.update()

    def logika_reczna(self):
        # 1. Obsługa pomp 
        self.obsluz_transfer(self.p1, self.rura1, self.z1, self.z3, 0.5)
        self.obsluz_transfer(self.p2, self.rura2, self.z2, self.z3, 0.5)
        self.obsluz_transfer(self.p3, self.rura3, self.z3, self.z4, 0.8, mieszaj_temp=True)
        
        # 2. Obsługa grzałki
        self.obsluz_grzanie()

        # 3. Komunikaty
        if self.z4.czy_pelny():
            self.lbl_info.setText("RĘCZNY: PROCES ZAKOŃCZONY (Produkt gotowy!)")
            self.lbl_info.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
        elif "PROCES" in self.lbl_info.text():
             self.lbl_info.setText("Sterowanie RĘCZNE")
             self.lbl_info.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

    def logika_auto(self):
        # Reset stanów 
        for dev in self.pompy + [self.grzalka]: dev.aktywna = False
        for r in self.rury: r.plynie = False

        if self.stan == StanProcesu.DOZOWANIE:
            self.lbl_info.setText("AUTO: Dozowanie składników...")
            self.lbl_info.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            
            # Symulujemy włączenie pomp przez automat
            self.p1.aktywna = True
            self.p2.aktywna = True
            
            p1_ok = self.obsluz_transfer(self.p1, self.rura1, self.z1, self.z3, 0.5)
            p2_ok = self.obsluz_transfer(self.p2, self.rura2, self.z2, self.z3, 0.5)
            
            # Jeśli nic nie płynie (bo pusto lub pełno), idź dalej
            if self.z3.czy_pelny() or (not p1_ok and not p2_ok):
                self.stan = StanProcesu.OBROBKA

        elif self.stan == StanProcesu.OBROBKA:
            self.lbl_info.setText(f"AUTO: Grzanie ({int(self.z3.temperatura)}/60°C)")
            self.grzalka.aktywna = True
            self.obsluz_grzanie() # Używamy tej samej fizyki co w manualu
            
            if not self.grzalka.aktywna: # Jeśli bezpiecznik wyłączył grzałkę (temp >= 60)
                self.stan = StanProcesu.WYLEWANIE

        elif self.stan == StanProcesu.WYLEWANIE:
            self.lbl_info.setText("AUTO: Zrzut produktu")
            self.p3.aktywna = True
            p3_ok = self.obsluz_transfer(self.p3, self.rura3, self.z3, self.z4, 0.8, mieszaj_temp=True)
            
            if not p3_ok: # Jeśli przestało płynąć (pusto w Z3 lub pełno w Z4)
                self.stan = StanProcesu.STOP
                self.lbl_info.setText("AUTO: KONIEC PROCESU")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(p)
        for z in self.zbiorniki: z.draw(p)
        for pompa in self.pompy: pompa.draw(p)
        self.grzalka.draw(p)