from app.engine.rules import ExpertSystem
from app.models.facts import CurrencyExchange

class TransactionProcessor:
    def __init__(self):
        self.transactions = []  # Lista transakcji
        self.total_trading = 0  # Obrót
        self.total_commission = 0
        self.processed_transactions = []

    def add_transaction(self, transaction_data):
        transaction = {
            'amount': transaction_data['amount'],
            'currency_in': transaction_data['currency_in'],
            'currency_out': transaction_data['currency_out'],
            'operation': transaction_data['operation'],
            'card': transaction_data.get('card', False),
            'processed': False,  # Flaga oznaczająca przetworzenie transakcji
            'id': len(self.transactions) + 1
        }

        self.transactions.append(transaction)

        return transaction['id']

    def get_exchange_rate_from_expert_system(self, amount, currency_in, currency_out, operation, current_trading, card):
        engine = ExpertSystem()
        engine.reset()

        engine.declare(CurrencyExchange(
            total_trading=current_trading,
            card=card,
            amount=amount,
            currency_in=currency_in.upper(),
            currency_out=currency_out.upper(),
            operation=operation
        ))

        engine.run()

        results = {
            'commision': 0.002,  # domyślne wartości
            'commision_percentage': 0.2,
            'exchange_rate_in': 1.0,
            'exchange_rate_out': 1.0
        }

        for fact_id, fact in engine.facts.items():
            if 'commision' in fact:
                results['commision'] = fact['commision']
            if 'commision_percentage' in fact:
                results['commision_percentage'] = fact['commision_percentage']
            if 'exchange_rate_in' in fact:
                results['exchange_rate_in'] = fact['exchange_rate_in']
            if 'exchange_rate_out' in fact:
                results['exchange_rate_out'] = fact['exchange_rate_out']

        return results

    def calculate_pln_value(self, amount, currency, operation, expert_results):
        if currency.upper() == 'PLN':
            return amount

        exchange_rate = expert_results['exchange_rate_in']
        return amount * exchange_rate

    def process_all_transactions(self):
        self.total_trading = 0
        self.total_commission = 0
        self.processed_transactions = []

        for transaction in self.transactions:
            if not transaction['processed']:
                expert_results = self.get_exchange_rate_from_expert_system(
                    transaction['amount'],
                    transaction['currency_in'],
                    transaction['currency_out'],
                    transaction['operation'],
                    self.total_trading,  # Użyj aktualnego obrotu
                    transaction['card'],
                )

                pln_value = self.calculate_pln_value(
                    transaction['amount'],
                    transaction['currency_in'],
                    transaction['operation'],
                    expert_results
                )

                self.total_trading += pln_value

                result = self.calculate_single_transaction(transaction, self.total_trading)

                transaction['processed'] = True
                transaction['result'] = result

                self.processed_transactions.append(transaction)

                self.total_commission += result['quota_commision']

        return self.get_summary()

    def calculate_single_transaction(self, transaction, current_trading):
        expert_results = self.get_exchange_rate_from_expert_system(
            transaction['amount'],
            transaction['currency_in'],
            transaction['currency_out'],
            transaction['operation'],
            current_trading,
            transaction['card'],
        )

        amount = transaction['amount']
        currency_in = transaction['currency_in']
        currency_out = transaction['currency_out']
        operation = transaction['operation']

        commision = expert_results['commision']
        commision_percentage = expert_results['commision_percentage']
        exchange_rate_in = expert_results['exchange_rate_in']
        exchange_rate_out = expert_results['exchange_rate_out']

        amount_in_pln = amount * exchange_rate_in

        quota_commision = amount_in_pln * commision
        amount_after_commision = amount_in_pln - quota_commision

        final_amount = amount_after_commision / exchange_rate_out

        return {
            'operation': operation,
            'input_amount': amount,
            'currency_in': currency_in,
            'amount_in_pln': amount_in_pln,
            'commision_percentage': commision_percentage,
            'quota_commision': quota_commision,
            'amount_after_commision': amount_after_commision,
            'final_amount': final_amount,
            'currency_out': currency_out,
            'exchange_rate_in': exchange_rate_in,
            'exchange_rate_out': exchange_rate_out,
            'current_commision': commision,
        }

    def get_summary(self):
        if self.processed_transactions:
            last_commision = self.processed_transactions[-1]['result']['commision_percentage']
        else:
            last_commision = self.get_current_commission()

        return {
            'number_of_transactions': len(self.processed_transactions),
            'total_trading_in_pln': self.total_trading,
            'total_commision': self.total_commission,
            'transactions': self.processed_transactions,
            'current_commision': last_commision
        }

    def get_current_commission(self):
        engine = ExpertSystem()
        engine.reset()

        engine.declare(CurrencyExchange(
            total_trading=self.total_trading,
            card=False,  # Sprawdzamy podstawową prowizję
        ))

        engine.run()

        for fact_id, fact in engine.facts.items():
            if 'commision_percentage' in fact:
                return fact['commision_percentage']

        return 0.2

    def reset_transactions(self):
        self.transactions = []
        self.total_trading = 0
        self.total_commission = 0
        self.processed_transactions = []


def calculate_exchange(amount, currency_in, currency_out, card, trading, operation):
    processor = TransactionProcessor()
    transaction_data = {
        'amount': amount,
        'currency_in': currency_in,
        'currency_out': currency_out,
        'operation': operation,
        'card': card,
    }

    processor.add_transaction(transaction_data)
    processor.total_turnover = trading
    result = processor.calculate_single_transaction(processor.transactions[0], trading)

    return (
        f"Operacja: {result['operation'].upper()}\n"
        f"Kwota wejściowa: {result['input_amount']:.2f} {result['currency_in'].upper()}\n"
        f"Kwota w PLN: {result['amount_in_pln']:.2f} PLN\n"
        f"Prowizja: {result['quota_commision']:.2f} PLN ({result['commision_percentage']:.3f}%)\n"
        f"Kwota po prowizji: {result['amount_after_commision']:.2f} PLN\n"
        f"Otrzymasz: {result['final_amount']:.2f} {result['currency_out'].upper()} (po kursie {result['exchange_rate_out']:.4f})\n"
    )