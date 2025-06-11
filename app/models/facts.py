from experta import Fact

class WymianaWalut(Fact):
    """Fakt opisujący dane potrzebne do oceny prowizji"""
    obrot_calkowity = 0  # Łączny obrót wszystkich transakcji w PLN
    karta = False        # Czy klient ma kartę lojalnościową
    punkty = 0          # Aktualne punkty lojalnościowe klienta
    akcja = False       # Czy trwa akcja specjalna
    pass