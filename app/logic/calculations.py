from app.engine.rules import SystemEkspercki
from app.models.facts import WymianaWalut

# Walutomat kupuje od użytkownika
KURSY_KUPNA = {
    'EUR': 4.23, 'USD': 3.71, 'GBP': 5.02,
    'PLN': 1.0, 'CZK': 0.16, 'JPY': 2.58
}

# Walutomat sprzedaje klientowi
KURSY_SPRZEDAZY = {
    'EUR': 4.31, 'USD': 3.79, 'GBP': 5.12,
    'PLN': 1.0, 'CZK': 0.17, 'JPY': 2.64
}

def oblicz_wymiane(kwota, waluta_wej, waluta_wyj, punkty, karta, akcja, obrot, operacja):
    engine = SystemEkspercki()
    engine.reset()
    engine.declare(WymianaWalut(obrot=obrot, karta=karta, akcja=akcja, punkty=punkty))
    engine.run()

    prowizja = 0.002  # domyślna prowizja
    for fact in engine.facts.values():
        if isinstance(fact, dict) and 'prowizja' in fact:
            prowizja = fact['prowizja']

    kurs_wej_kupno = KURSY_KUPNA.get(waluta_wej.upper(), 1.0)
    kurs_wej_sprzedaz = KURSY_SPRZEDAZY.get(waluta_wej.upper(), 1.0)
    kurs_wyj_kupno = KURSY_KUPNA.get(waluta_wyj.upper(), 1.0)
    kurs_wyj_sprzedaz = KURSY_SPRZEDAZY.get(waluta_wyj.upper(), 1.0)

    # Przeliczamy walutę wejściową na PLN
    if operacja == 'sprzedaz':
        # użytkownik sprzedaje walutę, walutomat ją kupuje, dlatego używamy kursu kupna
        kwota_w_pln = kwota * kurs_wej_kupno
    else:  # 'kupno'
        # użytkownik kupuje walutę, walutomat ją sprzedaje, dlatego używamy kursu sprzedaży
        kwota_w_pln = kwota * kurs_wej_sprzedaz

    # pobieramy prowizję
    prowizja_kwotowa = kwota_w_pln * prowizja
    kwota_po_prowizji = kwota_w_pln - prowizja_kwotowa

    if operacja == 'sprzedaz':
        # użytkownik chce dostać walutę wyjściową, więc my ją sprzedajemy => kurs SPRZEDAŻY
        kwota_koncowa = kwota_po_prowizji / kurs_wyj_sprzedaz
        kurs_wyj_uzyty = kurs_wyj_sprzedaz
    else:  # kupno
        # użytkownik chce dostać walutę wyjściową, my ją kupujemy => kurs KUPNA
        kwota_koncowa = kwota_po_prowizji / kurs_wyj_kupno
        kurs_wyj_uzyty = kurs_wyj_kupno

    # wyliczanie punktów
    punkty_za_kwote = 0
    if waluta_wej.upper() in ['EUR', 'USD', 'GBP']:
        punkty_za_kwote = kwota // 10
    elif waluta_wej.upper() == 'PLN':
        punkty_za_kwote = kwota // 50
    elif waluta_wej.upper() in ['CZK', 'JPY']:
        punkty_za_kwote = kwota // 1000

    punkty_bonus = 0
    for fact in engine.facts.values():
        if isinstance(fact, dict) and 'punkty_bonus' in fact:
            punkty_bonus = fact['punkty_bonus']

    punkty_za_kwote += punkty_bonus

    return (
        f"Operacja: {operacja.upper()}\n"
        f"Kwota wejściowa: {kwota:.2f} {waluta_wej.upper()}\n"
        f"Kwota w PLN: {kwota_w_pln:.2f} PLN\n"
        f"Prowizja: {prowizja_kwotowa:.2f} PLN ({prowizja * 100:.2f}%)\n"
        f"Kwota po prowizji: {kwota_po_prowizji:.2f} PLN\n"
        f"Otrzymasz: {kwota_koncowa:.2f} {waluta_wyj.upper()} (po kursie {kurs_wyj_uzyty:.4f})\n"
        f"Punkty za udział w akcji specjalnej: {punkty_bonus}\n"
        f"Zdobyte punkty: {int(punkty_za_kwote)}"
    )
