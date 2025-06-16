from experta import Fact

class CurrencyExchange(Fact):
    """Fakt opisujący dane potrzebne do oceny prowizji i transakcji"""
    total_trading = 0  # Łączny obrót wszystkich transakcji w PLN
    card = False        # Czy klient ma kartę lojalnościową
    amount = 0           # Kwota transakcji
    currency_in = ""     # Waluta wejściowa
    currency_out = ""     # Waluta wyjściowa
    operation = ""       # Typ operacji (sprzedaz/kupno)
    pass