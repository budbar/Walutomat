from experta import *
from app.models.facts import WymianaWalut

class SystemEkspercki(KnowledgeEngine):
    # Reguła prowizji 0.2%
    @Rule(WymianaWalut(obrot=P(lambda x: x < 200_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_2(self):
        self.declare(Fact(prowizja=0.002))

    # Reguła prowizji 0.15%
    @Rule(WymianaWalut(obrot=P(lambda x: 200_000 <= x <= 1_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_15(self):
        self.declare(Fact(prowizja=0.0015))

    # Reguła prowizji 0.1%
    @Rule(WymianaWalut(obrot=P(lambda x: 1_000_000 < x <= 3_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_1(self):
        self.declare(Fact(prowizja=0.001))

    # Reguła prowizji 0.08%
    @Rule(WymianaWalut(obrot=P(lambda x: 3_000_000 < x <= 10_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_08(self):
        self.declare(Fact(prowizja=0.0008))

    # Reguła prowizji 0.06%
    @Rule(WymianaWalut(obrot=P(lambda x: x > 10_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_6(self):
        self.declare(Fact(prowizja=0.006))

    # Reguła karty dużej rodziny - DO POPRAWKI, ŹLE WYLICZA PROWIZJĘ
    @Rule(AS.f << Fact(obrot=MATCH.obrot, karta=True, prowizja=MATCH.prowizja))
    def karta_duzej_rodziny(self, f, obrot, karta, prowizja):
        self.modify(f, prowizja=prowizja * 0.75)

    # Reguła prowizji z punktami
    @Rule(WymianaWalut(punkty=P(lambda x: x >= 1000)))
    def bez_prowizji(self):
        self.declare(Fact(prowizja=0.0))

    # Reguła uczestnictwa w akcji specjalnej
    @Rule(WymianaWalut(akcja=True))
    def akcja_specjalna(self):
        self.declare(Fact(punkty_bonus=1000))
