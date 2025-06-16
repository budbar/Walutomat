from experta import *
from app.models.facts import CurrencyExchange

class ExpertSystem(KnowledgeEngine):
    # Reguły dotyczące prowizji
    @Rule(CurrencyExchange(total_trading=P(lambda x: x < 200_000), card=False))
    def commision_0_2(self):
        self.declare(Fact(commision=0.002, commision_percentage=0.2))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 200_000 <= x <= 1_000_000), card=False))
    def commision_0_15(self):
        self.declare(Fact(commision=0.0015, commision_percentage=0.15))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 1_000_000 < x <= 3_000_000), card=False))
    def commision_0_1(self):
        self.declare(Fact(commision=0.001, commision_percentage=0.1))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 3_000_000 < x <= 10_000_000), card=False))
    def commision_0_08(self):
        self.declare(Fact(commision=0.0008, commision_percentage=0.08))

    @Rule(CurrencyExchange(total_trading=P(lambda x: x > 10_000_000), card=False))
    def commision_0_06(self):
        self.declare(Fact(commision=0.0006, commision_percentage=0.06))

    # Reguły dla klientów z kartą lojalnościową (5% zniżki na prowizję)
    @Rule(CurrencyExchange(total_trading=P(lambda x: x < 200_000), card=True))
    def commision_card_0_2(self):
        self.declare(Fact(commision=0.0019, commision_percentage=0.19))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 200_000 <= x <= 1_000_000), card=True))
    def commision_card_0_15(self):
        self.declare(Fact(commision=0.001425, commision_percentage=0.1425))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 1_000_000 < x <= 3_000_000), card=True))
    def commision_card_0_1(self):
        self.declare(Fact(commision=0.00095, commision_percentage=0.095))

    @Rule(CurrencyExchange(total_trading=P(lambda x: 3_000_000 < x <= 10_000_000), card=True))
    def commision_card_0_08(self):
        self.declare(Fact(commision=0.00076, commision_percentage=0.076))

    @Rule(CurrencyExchange(total_trading=P(lambda x: x > 10_000_000), card=True))
    def commision_card_0_06(self):
        self.declare(Fact(commision=0.00057, commision_percentage=0.057))

    # Reguły dotyczące sprzedaży
    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='EUR'))
    def exchange_rate_buy_eur(self):
        self.declare(Fact(exchange_rate_in=4.23))

    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='USD'))
    def exchange_rate_buy_usd(self):
        self.declare(Fact(exchange_rate_in=3.71))

    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='GBP'))
    def exchange_rate_buy_gbp(self):
        self.declare(Fact(exchange_rate_in=5.02))

    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='PLN'))
    def exchange_rate_buy_pln(self):
        self.declare(Fact(exchange_rate_in=1.0))

    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='CZK'))
    def exchange_rate_buy_czk(self):
        self.declare(Fact(exchange_rate_in=0.16))

    @Rule(CurrencyExchange(operation='sprzedaz', currency_in='JPY'))
    def exchange_rate_buy_jpy(self):
        self.declare(Fact(exchange_rate_in=2.58))

    # Reguły dotyczące kupna
    @Rule(CurrencyExchange(operation='kupno', currency_in='EUR'))
    def exchange_rate_sell_eur(self):
        self.declare(Fact(exchange_rate_in=4.31))

    @Rule(CurrencyExchange(operation='kupno', currency_in='USD'))
    def exchange_rate_sell_usd(self):
        self.declare(Fact(exchange_rate_in=3.79))

    @Rule(CurrencyExchange(operation='kupno', currency_in='GBP'))
    def exchange_rate_sell_gbp(self):
        self.declare(Fact(exchange_rate_in=5.12))

    @Rule(CurrencyExchange(operation='kupno', currency_in='PLN'))
    def exchange_rate_sell_pln(self):
        self.declare(Fact(exchange_rate_in=1.0))

    @Rule(CurrencyExchange(operation='kupno', currency_in='CZK'))
    def exchange_rate_sell_czk(self):
        self.declare(Fact(exchange_rate_in=0.17))

    @Rule(CurrencyExchange(operation='kupno', currency_in='JPY'))
    def exchange_rate_sell_jpy(self):
        self.declare(Fact(exchange_rate_in=2.64))

    # Reguły kursów wejściowych
    @Rule(CurrencyExchange(currency_out='EUR'))
    def exchange_rate_out_eur(self):
        self.declare(Fact(exchange_rate_out=4.31))

    @Rule(CurrencyExchange(currency_out='USD'))
    def exchange_rate_out_usd(self):
        self.declare(Fact(exchange_rate_out=3.79))

    @Rule(CurrencyExchange(currency_out='GBP'))
    def exchange_rate_out_gbp(self):
        self.declare(Fact(exchange_rate_out=5.12))

    @Rule(CurrencyExchange(currency_out='PLN'))
    def exchange_rate_out_pln(self):
        self.declare(Fact(exchange_rate_out=1.0))

    @Rule(CurrencyExchange(currency_out='CZK'))
    def exchange_rate_out_czk(self):
        self.declare(Fact(exchange_rate_out=0.17))

    @Rule(CurrencyExchange(currency_out='JPY'))
    def exchange_rate_out_jpy(self):
        self.declare(Fact(exchange_rate_out=2.64))

    # Reguły domyślne
    @Rule(AS.f1 << CurrencyExchange(),
          NOT(Fact(commision=W())))
    def default_commision(self, f1):
        self.declare(Fact(commision=0.002, commision_percentage=0.2))

    @Rule(AS.f1 << CurrencyExchange(),
          NOT(Fact(exchange_rate_in=W())))
    def default_exchange_rate_in(self, f1):
        self.declare(Fact(exchange_rate_in=1.0))

    @Rule(AS.f1 << CurrencyExchange(),
          NOT(Fact(exchange_rate_out=W())))
    def default_exchange_rate_out(self, f1):
        self.declare(Fact(exchange_rate_out=1.0))