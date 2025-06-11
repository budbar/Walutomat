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


class TransactionProcessor:
    def __init__(self):
        self.transactions = []
        self.total_turnover = 0
        self.total_commission = 0
        self.total_points = 0
        self.processed_transactions = []

    def add_transaction(self, transaction_data):
        """Dodaje transakcję do listy"""
        transaction = {
            'kwota': transaction_data['kwota'],
            'waluta_wej': transaction_data['waluta_wej'],
            'waluta_wyj': transaction_data['waluta_wyj'],
            'operacja': transaction_data['operacja'],
            'punkty': transaction_data.get('punkty', 0),
            'karta': transaction_data.get('karta', False),
            'akcja': transaction_data.get('akcja', False),
            'processed': False,
            'id': len(self.transactions) + 1
        }
        self.transactions.append(transaction)
        return transaction['id']

    def calculate_pln_value(self, kwota, waluta, operacja):
        """Przelicza wartość na PLN"""
        if waluta.upper() == 'PLN':
            return kwota

        if operacja == 'sprzedaz':
            # Użytkownik sprzedaje, walutomat kupuje
            kurs = KURSY_KUPNA.get(waluta.upper(), 1.0)
        else:  # kupno
            # Użytkownik kupuje, walutomat sprzedaje
            kurs = KURSY_SPRZEDAZY.get(waluta.upper(), 1.0)

        return kwota * kurs

    def process_all_transactions(self):
        """Przetwarza wszystkie transakcje sekwencyjnie"""
        self.total_turnover = 0
        self.total_commission = 0
        self.total_points = 0
        self.processed_transactions = []

        for transaction in self.transactions:
            if not transaction['processed']:
                # Oblicz wartość w PLN dla obrotu
                pln_value = self.calculate_pln_value(
                    transaction['kwota'],
                    transaction['waluta_wej'],
                    transaction['operacja']
                )

                # Dodaj do łącznego obrotu
                self.total_turnover += pln_value

                # Uruchom system ekspercki z aktualnym obrotem
                result = self.calculate_single_transaction(transaction, self.total_turnover)

                # Oznacz jako przetworzoną
                transaction['processed'] = True
                transaction['result'] = result

                self.processed_transactions.append(transaction)

                # Dodaj do łącznych sum
                self.total_commission += result['prowizja_kwotowa']
                self.total_points += result['punkty_zdobyte']

        return self.get_summary()

    def calculate_single_transaction(self, transaction, current_turnover):
        """Oblicza pojedynczą transakcję z uwzględnieniem aktualnego obrotu"""
        engine = SystemEkspercki()
        engine.reset()

        # Użyj aktualnego obrotu dla systemu eksperckiego
        engine.declare(WymianaWalut(
            obrot_calkowity=current_turnover,
            karta=transaction['karta'],
            akcja=transaction['akcja'],
            punkty=transaction['punkty']
        ))
        engine.run()

        # Pobierz prowizję z systemu eksperckiego
        prowizja = 0.002  # domyślna prowizja
        punkty_bonus = 0

        for fact in engine.facts.values():
            if isinstance(fact, dict):
                if 'prowizja' in fact:
                    prowizja = fact['prowizja']
                if 'punkty_bonus' in fact:
                    punkty_bonus = fact['punkty_bonus']

        # Oblicz szczegóły transakcji
        kwota = transaction['kwota']
        waluta_wej = transaction['waluta_wej']
        waluta_wyj = transaction['waluta_wyj']
        operacja = transaction['operacja']

        kurs_wej_kupno = KURSY_KUPNA.get(waluta_wej.upper(), 1.0)
        kurs_wej_sprzedaz = KURSY_SPRZEDAZY.get(waluta_wej.upper(), 1.0)
        kurs_wyj_kupno = KURSY_KUPNA.get(waluta_wyj.upper(), 1.0)
        kurs_wyj_sprzedaz = KURSY_SPRZEDAZY.get(waluta_wyj.upper(), 1.0)

        # Przelicz na PLN
        if operacja == 'sprzedaz':
            kwota_w_pln = kwota * kurs_wej_kupno
        else:
            kwota_w_pln = kwota * kurs_wej_sprzedaz

        # Oblicz prowizję
        prowizja_kwotowa = kwota_w_pln * prowizja
        kwota_po_prowizji = kwota_w_pln - prowizja_kwotowa

        # Oblicz kwotę końcową
        if operacja == 'sprzedaz':
            kwota_koncowa = kwota_po_prowizji / kurs_wyj_sprzedaz
            kurs_wyj_uzyty = kurs_wyj_sprzedaz
        else:
            kwota_koncowa = kwota_po_prowizji / kurs_wyj_kupno
            kurs_wyj_uzyty = kurs_wyj_kupno

        # Oblicz punkty
        punkty_za_kwote = 0
        if waluta_wej.upper() in ['EUR', 'USD', 'GBP']:
            punkty_za_kwote = kwota // 10
        elif waluta_wej.upper() == 'PLN':
            punkty_za_kwote = kwota // 50
        elif waluta_wej.upper() in ['CZK', 'JPY']:
            punkty_za_kwote = kwota // 1000

        punkty_zdobyte = int(punkty_za_kwote + punkty_bonus)

        return {
            'operacja': operacja,
            'kwota_wejsciowa': kwota,
            'waluta_wej': waluta_wej,
            'kwota_w_pln': kwota_w_pln,
            'prowizja_procent': prowizja * 100,
            'prowizja_kwotowa': prowizja_kwotowa,
            'kwota_po_prowizji': kwota_po_prowizji,
            'kwota_koncowa': kwota_koncowa,
            'waluta_wyj': waluta_wyj,
            'kurs_uzyty': kurs_wyj_uzyty,
            'punkty_bonus': punkty_bonus,
            'punkty_zdobyte': punkty_zdobyte,
            'aktualna_prowizja': prowizja
        }

    def get_summary(self):
        """Zwraca podsumowanie wszystkich transakcji"""
        return {
            'liczba_transakcji': len(self.processed_transactions),
            'laczny_obrot_pln': self.total_turnover,
            'laczna_prowizja': self.total_commission,
            'laczne_punkty': self.total_points,
            'transakcje': self.processed_transactions,
            'aktualna_prowizja': self.get_current_commission_rate()
        }

    def get_current_commission_rate(self):
        """Zwraca aktualną stawkę prowizji na podstawie obrotu"""
        if self.total_turnover < 200_000:
            return 0.2
        elif 200_000 <= self.total_turnover <= 1_000_000:
            return 0.15
        elif 1_000_000 < self.total_turnover <= 3_000_000:
            return 0.1
        elif 3_000_000 < self.total_turnover <= 10_000_000:
            return 0.08
        else:
            return 0.06

    def reset_transactions(self):
        """Resetuje wszystkie transakcje"""
        self.transactions = []
        self.total_turnover = 0
        self.total_commission = 0
        self.total_points = 0
        self.processed_transactions = []


# Funkcja kompatybilności z oryginalnym kodem
def oblicz_wymiane(kwota, waluta_wej, waluta_wyj, punkty, karta, akcja, obrot, operacja):
    """Funkcja kompatybilności - oblicza pojedynczą wymianę"""
    processor = TransactionProcessor()
    transaction_data = {
        'kwota': kwota,
        'waluta_wej': waluta_wej,
        'waluta_wyj': waluta_wyj,
        'operacja': operacja,
        'punkty': punkty,
        'karta': karta,
        'akcja': akcja
    }

    processor.add_transaction(transaction_data)
    processor.total_turnover = obrot  # Ustaw obrót ręcznie
    result = processor.calculate_single_transaction(processor.transactions[0], obrot)

    return (
        f"Operacja: {result['operacja'].upper()}\n"
        f"Kwota wejściowa: {result['kwota_wejsciowa']:.2f} {result['waluta_wej'].upper()}\n"
        f"Kwota w PLN: {result['kwota_w_pln']:.2f} PLN\n"
        f"Prowizja: {result['prowizja_kwotowa']:.2f} PLN ({result['prowizja_procent']:.2f}%)\n"
        f"Kwota po prowizji: {result['kwota_po_prowizji']:.2f} PLN\n"
        f"Otrzymasz: {result['kwota_koncowa']:.2f} {result['waluta_wyj'].upper()} (po kursie {result['kurs_uzyty']:.4f})\n"
        f"Punkty za udział w akcji specjalnej: {result['punkty_bonus']}\n"
        f"Zdobyte punkty: {result['punkty_zdobyte']}"
    )