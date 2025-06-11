import tkinter as tk
from tkinter import messagebox
from app.logic.calculations import oblicz_wymiane

def start_gui():
    # Konfiguracja okna
    app = tk.Tk()
    app.geometry('300x500')
    app.title("Walutomat")

    # Rodzaj operacji
    tk.Label(app, text="Rodzaj operacji:").grid(row=0, column=0)
    var_operacja = tk.StringVar(value='sprzedaz')
    tk.OptionMenu(app, var_operacja, 'sprzedaz', 'kupno').grid(row=0, column=1)

    # Kwota
    tk.Label(app, text="Kwota:").grid(row=1, column=0)
    entry_kwota = tk.Entry(app)
    entry_kwota.grid(row=1, column=1)

    # Waluta wejściowa
    tk.Label(app, text="Waluta wejściowa:").grid(row=2, column=0)
    var_waluta_wej = tk.StringVar(value='EUR')
    entry_waluta_wej = tk.OptionMenu(app, var_waluta_wej, *['EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY'])
    entry_waluta_wej.grid(row=2, column=1)

    # Waluta wyjściowa
    tk.Label(app, text="Waluta wyjściowa:").grid(row=3, column=0)
    var_waluta_wyj = tk.StringVar(value='PLN')
    entry_waluta_wyj = tk.OptionMenu(app, var_waluta_wyj, *['EUR', 'USD', 'GBP', 'PLN', 'CZK', 'JPY'])
    entry_waluta_wyj.grid(row=3, column=1)

    # Punkty
    tk.Label(app, text="Liczba punktów:").grid(row=4, column=0)
    entry_punkty = tk.Entry(app)
    entry_punkty.insert(0, "0")
    entry_punkty.grid(row=4, column=1)

    # Obrót miesięczny
    tk.Label(app, text="Obrót miesięczny:").grid(row=5, column=0)
    entry_obrot = tk.Entry(app)
    entry_obrot.insert(0, "0")
    entry_obrot.grid(row=5, column=1)

    # Karta dużej rodziny
    var_karta = tk.BooleanVar()
    tk.Checkbutton(app, text="Karta dużej rodziny", variable=var_karta).grid(row=6, columnspan=2)

    # Udział w akcjach
    var_akcja = tk.BooleanVar()
    tk.Checkbutton(app, text="Udział w akcjach specjalnych", variable=var_akcja).grid(row=7, columnspan=2)

    # Wynik
    label_wynik = tk.Label(app, text="", justify="left", anchor="w")
    label_wynik.grid(row=9, column=0, columnspan=2, sticky="w", pady=10)

    def klik_oblicz():
        try:
            wynik = oblicz_wymiane(
                kwota=float(entry_kwota.get()),
                waluta_wej=var_waluta_wej.get(),
                waluta_wyj=var_waluta_wyj.get(),
                punkty=int(entry_punkty.get()),
                karta=var_karta.get(),
                akcja=var_akcja.get(),
                obrot=float(entry_obrot.get()),
                operacja=var_operacja.get()
            )
            label_wynik.config(text=wynik)
        except Exception as e:
            label_wynik.config(text=f"Błąd: {str(e)}")

    # Przycisk do obliczania
    tk.Button(app, text="Oblicz", command=klik_oblicz).grid(row=8, columnspan=2)
    app.mainloop()
