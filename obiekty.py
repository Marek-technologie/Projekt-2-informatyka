from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainterPath, QFont

class ObiektPrzemyslowy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pompa(ObiektPrzemyslowy):
    def __init__(self, x, y, nazwa="P"):
        super().__init__(x, y)
        self.nazwa = nazwa
        self.aktywna = False
        self.kat_wirnika = 0

    def przelacz(self):
        self.aktywna = not self.aktywna

    def draw(self, p):
        # Korpus
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(QColor(100, 100, 100))
        p.drawEllipse(int(self.x), int(self.y), 40, 40)
        
        # Dioda statusu
        kolor = QColor("#2ecc71") if self.aktywna else QColor("#e74c3c")
        p.setBrush(kolor)
        p.drawEllipse(int(self.x + 12), int(self.y + 12), 16, 16)
        
        # Wirnik
        p.save()
        p.translate(self.x + 20, self.y + 20)
        if self.aktywna:
            self.kat_wirnika = (self.kat_wirnika + 20) % 360
            p.rotate(self.kat_wirnika)
        
        p.setPen(QPen(Qt.white, 2))
        p.drawLine(-10, 0, 10, 0)
        p.drawLine(0, -10, 0, 10)
        p.restore()
        
        # Podpis
        p.setPen(Qt.white)
        p.drawText(int(self.x), int(self.y - 5), self.nazwa)

class Grzalka(ObiektPrzemyslowy):
    def __init__(self, x, y, nazwa="G1"): # Dodalem nazwe
        super().__init__(x, y)
        self.nazwa = nazwa
        self.aktywna = False
        self.temperatura = 20.0
    
    def przelacz(self):
        """Metoda do sterowania ręcznego"""
        self.aktywna = not self.aktywna
        
    def draw(self, p):
        if self.aktywna:
            kolor = QColor(255, 50, 50, 200)
            self.temperatura += 0.5
        else:
            kolor = QColor(50, 50, 50)
            self.temperatura = max(20.0, self.temperatura - 0.1)
            
        p.setPen(QPen(kolor, 4))
        path = QPainterPath()
        start_x, start_y = self.x, self.y
        path.moveTo(start_x, start_y)
        for i in range(4):
            path.lineTo(start_x + 10 + (i*10), start_y + 20)
            path.lineTo(start_x + 20 + (i*10), start_y)
            
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        
        # Podpis grzałki
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 8))
        p.drawText(int(self.x), int(self.y + 35), self.nazwa)

class Zbiornik(ObiektPrzemyslowy):
    def __init__(self, x, y, w, h, nazwa, poj=100):
        super().__init__(x, y)
        self.w = w
        self.h = h
        self.nazwa = nazwa
        self.pojemnosc = poj
        self.aktualna_ilosc = 0.0
        self.temperatura = 20.0

    def czy_pelny(self): return self.aktualna_ilosc >= self.pojemnosc
    def czy_pusty(self): return self.aktualna_ilosc <= 0.1
    
    def zmien_ilosc(self, delta):
        self.aktualna_ilosc = max(0, min(self.pojemnosc, self.aktualna_ilosc + delta))

    def draw(self, p):
        p.setPen(QPen(Qt.white, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(int(self.x), int(self.y), int(self.w), int(self.h))
        
        poziom = self.aktualna_ilosc / self.pojemnosc
        h_cieczy = self.h * poziom
        
        red = min(255, max(0, int((self.temperatura - 20) * 3)))
        p.setBrush(QColor(red, 100, 255 - red, 180))
        p.setPen(Qt.NoPen)
        p.drawRect(int(self.x + 2), int(self.y + self.h - h_cieczy), int(self.w - 4), int(h_cieczy))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 9))
        p.drawText(int(self.x), int(self.y - 20), f"{self.nazwa}")
        p.drawText(int(self.x), int(self.y - 5), f"{int(self.aktualna_ilosc)} L | {int(self.temperatura)}°C")

class Rura:
    def __init__(self, punkty_xy, grubosc=8):
        self.punkty = [QPointF(*pt) for pt in punkty_xy]
        self.grubosc = grubosc
        self.plynie = False
        
    def draw(self, p):
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for pt in self.punkty[1:]:
            path.lineTo(pt)
            
        p.setPen(QPen(QColor(80, 80, 80), self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        
        if self.plynie:
            p.setPen(QPen(QColor(0, 200, 255), self.grubosc-4))
            p.drawPath(path)