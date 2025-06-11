import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.logic.calculations import TransactionProcessor


def start_gui():
    app = tk.Tk()
    app.geometry('1200x700')
    app.title("Walutomat - System Ekspercki")

    # Procesor transakcji
    processor = TransactionProcessor()

    main_frame = tk.Frame(app)
    main_frame.pack(fill='both', expand=True)

    # --- Lewa sekcja (Transakcje) ---
    left_frame = tk.Frame(main_frame, width=400)
    left_frame.pack(side='left', fill='y')
    left_frame.pack_propagate(False)

    # Kontrolki górne
    top_control_frame = tk.Frame(left_frame)
    top_control_frame.pack(fill='x', pady=5)

    # Globalne ustawienia
    global_frame = tk.LabelFrame(left_frame, text="Ustawienia globalne", padx=5, pady=5)
    global_frame.pack(fill='x', padx=5, pady=5)

    tk.Label(global_frame, text="Punkty lojalnościowe:").grid(row=0, column=0, sticky="w")
    entry_punkty_global = tk.Entry(global_frame, width=10)
    entry_punkty_global.insert(0, "0")
    entry_punkty_global.grid(row=0, column=1, padx=5)

    var_karta_global = tk.BooleanVar()
    tk.Checkbutton(global_frame, text="Karta lojalnościowa", variable=var_karta_global).grid(row=0, column=2, padx=10)

    var_akcja_global = tk.BooleanVar()
    tk.Checkbutton(global_frame, text="Akcja specjalna", variable=var_akcja_global).grid(row=0, column=3, padx=10)

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

    # --- Prawa sekcja (Wyniki) ---
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

    def get_transaction_data(panel_data):
        """Pobiera dane z panelu transakcji"""
        try:
            kwota = float(panel_data['entry_kwota'].get())
            return {
                'kwota': kwota,
                'waluta_wej': panel_data['var_waluta_wej'].get(),
                'waluta_wyj': panel_data['var_waluta_wyj'].get(),
                'operacja': panel_data['var_operacja'].get(),
                'punkty': int(entry_punkty_global.get() or 0),
                'karta': var_karta_global.get(),
                'akcja': var_akcja_global.get()
            }
        except ValueError:
            return None

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

        btn_delete = tk.Button(header_frame, text="✕", fg="red",
                               command=lambda: remove_panel(panel_data))
        btn_delete.pack(side='right')

        # Zmienne
        var_operacja = tk.StringVar(value='sprzedaz')
        var_waluta_wej = tk.StringVar(value='EUR')
        var_waluta_wyj = tk.StringVar(value='PLN')

        # Kontrolki
        controls_frame = tk.Frame(panel)
        controls_frame.pack(fill='x', pady=5)

        tk.Label(controls_frame, text="Operacja:").grid(row=0, column=0, sticky="w", padx=5)
        tk.OptionMenu(controls_frame, var_operacja, 'sprzedaz', 'kupno').grid(row=0, column=1, padx=5)

        tk.Label(controls_frame, text="Kwota:").grid(row=0, column=2, sticky="w", padx=5)
        entry_kwota = tk.Entry(controls_frame, width=10)
        entry_kwota.grid(row=0, column=3, padx=5)

        tk.Label(controls_frame, text="Z:").grid(row=1, column=0, sticky="w", padx=5)
        tk.OptionMenu(controls_frame, var_waluta_wej, 'EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY').grid(row=1, column=1,
                                                                                                     padx=5)

        tk.Label(controls_frame, text="Na:").grid(row=1, column=2, sticky="w", padx=5)
        tk.OptionMenu(controls_frame, var_waluta_wyj, 'EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY').grid(row=1, column=3,
                                                                                                     padx=5)

        # Status
        status_label = tk.Label(panel, text="Status: Nie przetworzona", fg="orange")
        status_label.pack(anchor='w', pady=2)

        panel_data = {
            'frame': panel,
            'label': label,
            'var_operacja': var_operacja,
            'var_waluta_wej': var_waluta_wej,
            'var_waluta_wyj': var_waluta_wyj,
            'entry_kwota': entry_kwota,
            'status_label': status_label
        }
        transaction_panels.append(panel_data)

    def clear_all_panels():
        for panel_data in transaction_panels:
            panel_data['frame'].destroy()
        transaction_panels.clear()
        processor.reset_transactions()
        results_text.delete(1.0, tk.END)

    def calculate_all_transactions():
        """Oblicza wszystkie transakcje"""
        processor.reset_transactions()

        # Dodaj wszystkie transakcje do procesora
        valid_transactions = 0
        for panel_data in transaction_panels:
            transaction_data = get_transaction_data(panel_data)
            if transaction_data:
                processor.add_transaction(transaction_data)
                valid_transactions += 1
            else:
                panel_data['status_label'].config(text="Status: Błąd danych", fg="red")

        if valid_transactions == 0:
            messagebox.showwarning("Brak danych", "Nie ma poprawnych transakcji do przetworzenia.")
            return

        # Przetwórz wszystkie transakcje
        summary = processor.process_all_transactions()

        # Aktualizuj statusy paneli
        for i, panel_data in enumerate(transaction_panels):
            if i < len(summary['transakcje']):
                panel_data['status_label'].config(text="Status: Przetworzona", fg="green")

        # Wyświetl wyniki
        display_results(summary)

    def display_results(summary):
        """Wyświetla wyniki w prawym panelu"""
        results_text.delete(1.0, tk.END)

        # Podsumowanie ogólne
        results_text.insert(tk.END, "=" * 60 + "\n")
        results_text.insert(tk.END, "PODSUMOWANIE WSZYSTKICH TRANSAKCJI\n")
        results_text.insert(tk.END, "=" * 60 + "\n\n")

        results_text.insert(tk.END, f"Liczba transakcji: {summary['liczba_transakcji']}\n")
        results_text.insert(tk.END, f"Łączny obrót: {summary['laczny_obrot_pln']:.2f} PLN\n")
        results_text.insert(tk.END, f"Aktualna stawka prowizji: {summary['aktualna_prowizja']:.2f}%\n")
        results_text.insert(tk.END, f"Łączna prowizja: {summary['laczna_prowizja']:.2f} PLN\n")
        results_text.insert(tk.END, f"Łączne punkty: {summary['laczne_punkty']}\n\n")

        # Progi prowizji
        results_text.insert(tk.END, "PROGI PROWIZJI:\n")
        results_text.insert(tk.END, "< 200,000 PLN → 0.20%\n")
        results_text.insert(tk.END, "200,000 - 1,000,000 PLN → 0.15%\n")
        results_text.insert(tk.END, "1,000,000 - 3,000,000 PLN → 0.10%\n")
        results_text.insert(tk.END, "3,000,000 - 10,000,000 PLN → 0.08%\n")
        results_text.insert(tk.END, "> 10,000,000 PLN → 0.06%\n\n")

        # Szczegóły transakcji
        results_text.insert(tk.END, "SZCZEGÓŁY TRANSAKCJI:\n")
        results_text.insert(tk.END, "-" * 60 + "\n")

        for i, transaction in enumerate(summary['transakcje'], 1):
            result = transaction['result']
            results_text.insert(tk.END, f"\nTransakcja {i}:\n")
            results_text.insert(tk.END, f"  Operacja: {result['operacja'].upper()}\n")
            results_text.insert(tk.END, f"  Kwota: {result['kwota_wejsciowa']:.2f} {result['waluta_wej'].upper()}\n")
            results_text.insert(tk.END, f"  Wartość w PLN: {result['kwota_w_pln']:.2f} PLN\n")
            results_text.insert(tk.END,
                                f"  Prowizja: {result['prowizja_kwotowa']:.2f} PLN ({result['prowizja_procent']:.2f}%)\n")
            results_text.insert(tk.END, f"  Otrzymasz: {result['kwota_koncowa']:.2f} {result['waluta_wyj'].upper()}\n")
            results_text.insert(tk.END, f"  Punkty: {result['punkty_zdobyte']} (bonus: {result['punkty_bonus']})\n")

    # Przyciski kontrolne
    tk.Button(top_control_frame, text="Dodaj transakcję", command=add_exchange_panel).pack(side='left', padx=5)
    tk.Button(top_control_frame, text="Usuń wszystkie", command=clear_all_panels).pack(side='left', padx=5)
    tk.Button(top_control_frame, text="Reset obliczeń",
              command=lambda: [processor.reset_transactions(), results_text.delete(1.0, tk.END)]).pack(side='left',
                                                                                                       padx=5)

    # Przypisz funkcję obliczania
    btn_calculate.config(command=calculate_all_transactions)

    # Dodaj pierwszą transakcję automatycznie
    add_exchange_panel()

    app.mainloop()