from experta import *
from app.models.facts import WymianaWalut

class SystemEkspercki(KnowledgeEngine):
    # Reguła prowizji 0.2%
    @Rule(WymianaWalut(obrot_calkowity=P(lambda x: x < 200_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_2(self):
        self.declare(Fact(prowizja=0.002))

    # Reguła prowizji 0.15%
    @Rule(WymianaWalut(obrot_calkowity=P(lambda x: 200_000 <= x <= 1_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_15(self):
        self.declare(Fact(prowizja=0.0015))

    # Reguła prowizji 0.1%
    @Rule(WymianaWalut(obrot_calkowity=P(lambda x: 1_000_000 < x <= 3_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_1(self):
        self.declare(Fact(prowizja=0.001))

    # Reguła prowizji 0.08%
    @Rule(WymianaWalut(obrot_calkowity=P(lambda x: 3_000_000 < x <= 10_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_08(self):
        self.declare(Fact(prowizja=0.0008))

    # Reguła prowizji 0.06%
    @Rule(WymianaWalut(obrot_calkowity=P(lambda x: x > 10_000_000), punkty=P(lambda x: x < 1000), karta=False))
    def prowizja_0_06(self):
        self.declare(Fact(prowizja=0.0006))

    # Reguły bonusów punktowych
    @Rule(WymianaWalut(akcja=True, obrot_calkowity=P(lambda x: x >= 500_000)))
    def bonus_punkty_duzy_obrot(self):
        self.declare(Fact(punkty_bonus=100))

    @Rule(WymianaWalut(akcja=True, obrot_calkowity=P(lambda x: 100_000 <= x < 500_000)))
    def bonus_punkty_sredni_obrot(self):
        self.declare(Fact(punkty_bonus=50))

    @Rule(WymianaWalut(akcja=True, obrot_calkowity=P(lambda x: x < 100_000)))
    def bonus_punkty_maly_obrot(self):
        self.declare(Fact(punkty_bonus=10))