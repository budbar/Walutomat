import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.logic.calculations import TransactionProcessor

def start_gui():
    app = tk.Tk()
    app.geometry('1200x700')
    app.title("Walutomat - System Ekspercki")

    processor = TransactionProcessor()

    main_frame = tk.Frame(app)
    main_frame.pack(fill='both', expand=True)

    # Lewa sekcja transakcji
    left_frame = tk.Frame(main_frame, width=400)
    left_frame.pack(side='left', fill='y')
    left_frame.pack_propagate(False)

    # Kontrolki górne
    top_control_frame = tk.Frame(left_frame)
    top_control_frame.pack(fill='x', pady=5)

    # Globalne ustawienia
    global_frame = tk.LabelFrame(left_frame, text="Ustawienia globalne", padx=5, pady=5)
    global_frame.pack(fill='x', padx=5, pady=5)

    var_card_global = tk.BooleanVar()
    tk.Checkbutton(global_frame, text="Karta lojalnościowa", variable=var_card_global).grid(row=0, column=2, padx=10)

    # Informacja o obecnym obrocie
    trading_info_frame = tk.Frame(global_frame)
    trading_info_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)

    # Scrollowalna lista transakcji
    scroll_container = tk.Frame(left_frame)
    scroll_container.pack(fill='both', expand=True)

    scroll_canvas = tk.Canvas(scroll_container, borderwidth=0, highlightthickness=0)
    scroll_canvas.pack(side="left", fill="both", expand=True)

    vsb = tk.Scrollbar(scroll_container, orient="vertical", command=scroll_canvas.yview)
    vsb.pack(side="right", fill="y")

    scroll_canvas.configure(yscrollcommand=vsb.set)
    scroll_frame = tk.Frame(scroll_canvas)
    window_id = scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_frame_configure(event):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

    def resize_canvas(event):
        scroll_canvas.itemconfig(window_id, width=event.width)

    scroll_frame.bind("<Configure>", on_frame_configure)
    scroll_canvas.bind("<Configure>", resize_canvas)

    def _on_mousewheel(event):
        scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Separator
    separator = ttk.Separator(main_frame, orient='vertical')
    separator.pack(side='left', fill='y', padx=5)

    # Prawa sekcja wyników
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side='left', fill='both', expand=True, padx=10)

    # Przycisk oblicz
    calculate_frame = tk.Frame(right_frame)
    calculate_frame.pack(fill='x', pady=10)

    btn_calculate = tk.Button(calculate_frame, text="OBLICZ WSZYSTKIE TRANSAKCJE",
                              font=("Helvetica", 12, "bold"), bg="green", fg="white", height=2)
    btn_calculate.pack(fill='x')

    # Wyniki
    results_frame = tk.LabelFrame(right_frame, text="Podsumowanie transakcji", font=("Helvetica", 10, "bold"))
    results_frame.pack(fill='both', expand=True, pady=10)

    # Text widget z scrollbarem dla wyników
    results_text_frame = tk.Frame(results_frame)
    results_text_frame.pack(fill='both', expand=True, padx=5, pady=5)

    results_text = tk.Text(results_text_frame, wrap=tk.WORD, font=("Consolas", 10))
    results_scrollbar = tk.Scrollbar(results_text_frame)

    results_text.pack(side="left", fill="both", expand=True)
    results_scrollbar.pack(side="right", fill="y")

    results_text.config(yscrollcommand=results_scrollbar.set)
    results_scrollbar.config(command=results_text.yview)

    # Lista paneli transakcji
    transaction_panels = []

    def update_transaction_labels():
        for idx, panel_data in enumerate(transaction_panels, start=1):
            label = panel_data['label']
            label.config(text=f"Transakcja {idx}")

    def remove_panel(panel_data):
        panel = panel_data['frame']
        panel.destroy()
        transaction_panels.remove(panel_data)
        update_transaction_labels()
        # Przelicz obrót po usunięciu panelu
        if transaction_panels:
            calculate_all_transactions(update_display_only=True)
        else:
            processor.reset_transactions()

    def get_transaction_data(panel_data):
        try:
            amount = float(panel_data['entry_amount'].get())

            return {
                'amount': amount,
                'currency_in': panel_data['var_currency_in'].get().upper(),
                'currency_out': panel_data['var_currency_out'].get().upper(),
                'operation': panel_data['var_operation'].get(),
                'card': var_card_global.get()
            }
        except ValueError:
            return None

    def validate_transaction_data(panel_data):
        try:
            amount = float(panel_data['entry_amount'].get())
            if amount <= 0:
                return False, "Kwota musi być większa od 0"

            currency_in = panel_data['var_currency_in'].get().upper()
            currency_out = panel_data['var_currency_out'].get().upper()

            if currency_in == currency_out:
                return False, "Waluta wejściowa i wyjściowa nie mogą być takie same"

            return True, ""
        except ValueError:
            return False, "Nieprawidłowa kwota"

    def add_exchange_panel():
        if len(transaction_panels) >= 10:
            messagebox.showwarning("Limit osiągnięty", "Można dodać maksymalnie 10 transakcji.")
            return

        nr = len(transaction_panels) + 1
        panel = tk.Frame(scroll_frame, bd=2, relief='groove', padx=5, pady=5)
        panel.pack(fill='x', padx=5, pady=5)

        # Etykieta i przycisk usuwania
        header_frame = tk.Frame(panel)
        header_frame.pack(fill='x')

        label = tk.Label(header_frame, text=f"Transakcja {nr}", font=("Helvetica", 10, "bold"))
        label.pack(side='left')

        btn_delete = tk.Button(header_frame, text="✕", fg="red", font=("Helvetica", 10, "bold"),
                               command=lambda: remove_panel(panel_data))
        btn_delete.pack(side='right')

        # Zmienne - zgodne z klasą WymianaWalut
        var_operation = tk.StringVar(value='sprzedaz')
        var_currency_in = tk.StringVar(value='EUR')
        var_currency_out = tk.StringVar(value='PLN')

        # Kontrolki
        controls_frame = tk.Frame(panel)
        controls_frame.pack(fill='x', pady=5)

        # Pierwsza linia
        tk.Label(controls_frame, text="Operacja:").grid(row=0, column=0, sticky="w", padx=5)
        operation_menu = tk.OptionMenu(controls_frame, var_operation, 'sprzedaz', 'kupno')
        operation_menu.grid(row=0, column=1, padx=5, sticky="ew")

        tk.Label(controls_frame, text="Kwota:").grid(row=0, column=2, sticky="w", padx=(15, 5))
        entry_amount = tk.Entry(controls_frame, width=12)
        entry_amount.grid(row=0, column=3, padx=5)

        # Druga linia
        tk.Label(controls_frame, text="Z waluty:").grid(row=1, column=0, sticky="w", padx=5)
        currency_in_menu = tk.OptionMenu(controls_frame, var_currency_in, 'EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY')
        currency_in_menu.grid(row=1, column=1, padx=5, sticky="ew")

        tk.Label(controls_frame, text="Na walutę:").grid(row=1, column=2, sticky="w", padx=(15, 5))
        currency_out_menu = tk.OptionMenu(controls_frame, var_currency_out, 'EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY')
        currency_out_menu.grid(row=1, column=3, padx=5, sticky="ew")

        # Konfiguracja kolumn
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(3, weight=1)

        # Status i przewidywany wynik
        status_frame = tk.Frame(panel)
        status_frame.pack(fill='x', pady=2)

        status_label = tk.Label(status_frame, text="Status: Nie przetworzona", font=("Helvetica", 8))
        status_label.pack(side='left')

        preview_label = tk.Label(status_frame, text="", font=("Helvetica", 8))
        preview_label.pack(side='right')

        # Funkcja do aktualizacji podglądu
        def update_preview(*args):
            is_valid, error_msg = validate_transaction_data({'entry_amount': entry_amount,
                                                             'var_currency_in': var_currency_in,
                                                             'var_currency_out': var_currency_out})
            if is_valid:
                try:
                    amount = float(entry_amount.get())
                    preview_label.config(text=f"~{amount:.2f} {var_currency_in.get()} → {var_currency_out.get()}")
                except:
                    preview_label.config(text="")
            else:
                preview_label.config(text=error_msg if error_msg else "")

        # Bindowanie zdarzeń dla podglądu
        entry_amount.bind('<KeyRelease>', update_preview)
        var_currency_in.trace('w', update_preview)
        var_currency_out.trace('w', update_preview)
        var_operation.trace('w', update_preview)

        panel_data = {
            'frame': panel,
            'label': label,
            'var_operation': var_operation,
            'var_currency_in': var_currency_in,
            'var_currency_out': var_currency_out,
            'entry_amount': entry_amount,
            'status_label': status_label,
            'preview_label': preview_label
        }
        transaction_panels.append(panel_data)

        # Pierwsza aktualizacja podglądu
        update_preview()

    def clear_all_panels():
        for panel_data in transaction_panels:
            panel_data['frame'].destroy()
        transaction_panels.clear()
        processor.reset_transactions()
        results_text.delete(1.0, tk.END)

    def calculate_all_transactions(update_display_only=False):
        """Oblicza wszystkie transakcje z lepszą walidacją"""
        processor.reset_transactions()

        # Walidacja i dodawanie transakcji
        valid_transactions = 0
        invalid_panels = []

        for panel_data in transaction_panels:
            is_valid, error_msg = validate_transaction_data(panel_data)

            if is_valid:
                transaction_data = get_transaction_data(panel_data)
                if transaction_data:
                    processor.add_transaction(transaction_data)
                    valid_transactions += 1
                    panel_data['status_label'].config(text="Status: Gotowa do przetworzenia", fg="blue")
                else:
                    panel_data['status_label'].config(text="Status: Błąd danych", fg="red")
                    invalid_panels.append(panel_data)
            else:
                panel_data['status_label'].config(text=f"Status: {error_msg}", fg="red")
                invalid_panels.append(panel_data)

        if valid_transactions == 0:
            if not update_display_only:
                messagebox.showwarning("Brak danych", "Nie ma poprawnych transakcji do przetworzenia.")
            return

        # Przetwarzanie transakcji
        try:
            summary = processor.process_all_transactions()

            # Aktualizacja statusów paneli
            for i, panel_data in enumerate(transaction_panels):
                if panel_data not in invalid_panels:
                    if i < len(summary['transactions']):
                        panel_data['status_label'].config(text="Status: Przetworzona", fg="green")

            # Wyświetlenie wyników tylko jeśli nie jest to aktualizacja wyświetlania
            if not update_display_only:
                display_results(summary)

        except Exception as e:
            messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd podczas przetwarzania: {str(e)}")

    def display_results(summary):
        """Wyświetla wyniki w prawym panelu z lepszym formatowaniem"""
        results_text.delete(1.0, tk.END)

        # Podsumowanie ogólne
        results_text.insert(tk.END, "=" * 65 + "\n")
        results_text.insert(tk.END, "           PODSUMOWANIE WSZYSTKICH TRANSAKCJI\n")
        results_text.insert(tk.END, "=" * 65 + "\n\n")

        results_text.insert(tk.END, f"Liczba transakcji: {summary['number_of_transactions']}\n")
        results_text.insert(tk.END, f"Łączny obrót: {summary['total_trading_in_pln']:.2f} PLN\n")
        results_text.insert(tk.END, f"Aktualna stawka prowizji: {summary['current_commision']:.3f}%\n")
        results_text.insert(tk.END, f"Łączna prowizja: {summary['total_commision']:.2f} PLN\n")

        # Progi prowizji
        results_text.insert(tk.END, "PROGI PROWIZJI:\n")
        results_text.insert(tk.END, "-" * 30 + "\n")
        results_text.insert(tk.END, "< 200,000 PLN        → 0.20%\n")
        results_text.insert(tk.END, "200,000 - 1,000,000  → 0.15%\n")
        results_text.insert(tk.END, "1M - 3M PLN          → 0.10%\n")
        results_text.insert(tk.END, "3M - 10M PLN         → 0.08%\n")
        results_text.insert(tk.END, "> 10M PLN            → 0.06%\n")
        results_text.insert(tk.END, "* Karta lojalnościowa: -5% prowizji\n\n")

        # Szczegóły transakcji
        results_text.insert(tk.END, " SZCZEGÓŁY TRANSAKCJI:\n")
        results_text.insert(tk.END, "-" * 65 + "\n")

        for i, transaction in enumerate(summary['transactions'], 1):
            result = transaction['result']
            results_text.insert(tk.END, f"\nTransakcja {i}:\n")
            results_text.insert(tk.END, f"Operacja: {result['operation'].upper()}\n")
            results_text.insert(tk.END, f"Kwota: {result['input_amount']:.2f} {result['currency_in']}\n")
            results_text.insert(tk.END, f"Wartość w PLN: {result['amount_in_pln']:.2f} PLN\n")
            results_text.insert(tk.END, f"Prowizja: {result['quota_commision']:.2f} PLN ({result['commision_percentage']:.3f}%)\n")
            results_text.insert(tk.END, f"Otrzymasz: {result['final_amount']:.2f} {result['currency_out']}\n")

    # Przyciski kontrolne z lepszymi opisami
    control_buttons_frame = tk.Frame(top_control_frame)
    control_buttons_frame.pack(fill='x')

    tk.Button(control_buttons_frame, text="Dodaj transakcję", command=add_exchange_panel).pack(side='left', padx=2)
    tk.Button(control_buttons_frame, text="Usuń wszystkie", command=clear_all_panels).pack(side='left', padx=2)
    tk.Button(control_buttons_frame, text="Reset obliczeń",
              command=lambda: [processor.reset_transactions(), results_text.delete(1.0, tk.END)],
              ).pack(side='left', padx=2)

    # Przypisz funkcję obliczania
    btn_calculate.config(command=calculate_all_transactions)

    # Bindowanie aktualizacji obrotu przy zmianach globalnych
    def on_global_change(*args):
        if transaction_panels:
            calculate_all_transactions(update_display_only=True)

    var_card_global.trace('w', on_global_change)

    # Dodaj pierwszą transakcję automatycznie
    add_exchange_panel()

    app.mainloop()