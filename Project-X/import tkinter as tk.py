import tkinter as tk
import customtkinter
import sv_ttk as sv
import darkdetect
import pywinstyles, sys
from flask import Flask, jsonify, Response, render_template
import threading
import json
import webbrowser
from mysql.connector import connect, Error
from tkinter import ttk, messagebox

# --- Variabel for passord ---
mysql_password = ""
conn = None
cursor = None

# --- Flask API---
api_app = Flask(__name__)

@api_app.route('/')
def index():
    connection = connect(
            user='root',
            password=mysql_password,
            host='localhost',
            database='varehusdb'
        )
    cur = connection.cursor()
    cur.execute("SELECT VNr, Betegnelse, Antall, Pris FROM vare")
    rows = cur.fetchall()
    connection.close()

    varer = []
    for row in rows:
        varer.append({
            "VNr": row[0],
            "Betegnelse": row[1],
            "Antall": row[2],
            "Pris": float(row[3])
            })
    return render_template('varer.html', varer=varer)


def start_api():
    api_app.run(port=5001)  # Flask API kjører på port 5001
# --- Flask API---

# --- GUI Funksjoner ---
def fetch_kunder():
    # Fjern gamle oppføringer i GUI
    for row in kunde_tree.get_children():
        kunde_tree.delete(row)

    # Opprett stored procedure hvis den ikke allerede eksisterer
    cursor.execute("DROP PROCEDURE IF EXISTS VisAlleKunder")
    procedure_sql = """
    CREATE PROCEDURE VisAlleKunder()
    BEGIN
        SELECT Knr, Fornavn, Etternavn, Adresse, PostNr FROM kunde;
    END
    """
    try:
        cursor.execute(procedure_sql)        #Oppretter stored procedure
        conn.commit()                        #Lagrer endringene i databasen
        print("Stored procedure 'VisAlleKunder' opprettet.")
    except Exception as e:
        print(f"Feil ved opprettelse av stored procedure: {e}")
        return

    # Kall stored procedure for å hente kunder
    try:
        cursor.callproc('VisAlleKunder')        #Kaller stored procedure
        for result in cursor.stored_results():  #Henter resultatene fra stored procedure
            for row in result.fetchall():
                kunde_tree.insert("", tk.END, values=row)
        print("Kundedata hentet med stored procedure.")
    except Exception as e:
        print(f"Feil ved henting av kunder: {e}")   #Printer ut feilmeldingen

def add_kunde():

    try:
        cursor.execute("SELECT MAX(Knr) FROM kunde")    #Henter den høyeste kunde ID
        max_id = cursor.fetchone()[0]                   #Henter den høyeste kunde ID
        next_id = (max_id or 0) + 1                     #Max ID + 1 eller 1 om ingen kunder finnes

        values = (
            next_id,
            entry_vars["Fornavn"].get(),            #Henter verdien fra tekstfeltet
            entry_vars["Etternavn"].get(),          #Henter verdien fra tekstfeltet
            entry_vars["Adresse"].get(),            #Henter verdien fra tekstfeltet
            entry_vars["PostNr"].get()              #Henter verdien fra tekstfeltet
        )
        query = """
            INSERT INTO kunde (Knr, Fornavn, Etternavn, Adresse, PostNr) 
            VALUES (%s, %s, %s, %s, %s)
        """                                                             #Setter inn verdiene i databasen i riktig rekkefølge, med %s for å unngå SQL injeksjon
        cursor.execute(query, values)                                   #Setter inn verdiene i databasen
        conn.commit()                                                   #Lagrer endringene i databasen
        label_status.config(text="Kunde lagt til!")                     #Printer ut at kunden er lagt til i GUI
        print("Kunde lagt til:", values)                                #Printer ut kunden i terminalen    
        for field in entry_vars.values():
            field.delete(0, tk.END)
        fetch_kunder()
    except Exception as e:
        label_status.config(text=f"Feil: {e}")  #Printer ut feilmeldingen ved feil

def delete_selected_kunde():
    selected = kunde_tree.selection()   #Henter den valgte kunden i GUI
    if not selected:
        messagebox.showwarning("Ingen valgt", "Vennligst velg en kunde å slette.")  #Viser en advarsel om at ingen er valgt
        return

    item = kunde_tree.item(selected[0]) #Henter den valgte kunden i GUI
    kunde_id = item['values'][0]        #Henter kunde ID fra den valgte kunden i GUI

    confirm = messagebox.askyesno("Bekreft sletting", f"Vil du slette kunde {kunde_id}?")   #Spør om bekreftelse på sletting
    if confirm:
        try:
            cursor.execute("DELETE FROM kunde WHERE Knr = %s", (kunde_id,)) #Sletter kunden fra databasen1
            conn.commit()                                                   #Lagrer endringene i databasen
            fetch_kunder()                                                  #Henter kundene på nytt for å oppdatere GUI
            label_status.config(text="Kunde slettet.")                      #Printer ut at kunden er slettet i GUI
        except Exception as e:
            label_status.config(text=f"Feil: {e}")  #Printer ut feilmeldingen ved feil

def rediger_kunde():
    selected = kunde_tree.selection()
    if not selected:
        messagebox.showwarning("Ingen valgt", "Vennligst velg en kunde å redigere.")
        return

    item = kunde_tree.item(selected[0])
    values = item['values']
    kunde_id = values[0]

    rediger_win = tk.Toplevel(root)
    rediger_win.geometry("300x200")
    rediger_win.title(f"Rediger kunde {kunde_id}")

    rediger_win.grid_columnconfigure(0, weight=1)
    rediger_win.grid_columnconfigure(1, weight=1)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(rediger_win)

    labels = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
    entries = {}


    for i, label in enumerate(labels):
        tk.Label(rediger_win, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry = customtkinter.CTkEntry(rediger_win, width=200)              #Oppretter et tekstfelt for hvert felt
        entry.grid(row=i, column=1, padx=20, pady=5)
        entry.insert(0, values[i+1])  # +1 because values[0] is Knr
        entries[label] = entry

    def lagre():
        try:
            cursor.execute(
                "UPDATE kunde SET Fornavn=%s, Etternavn=%s, Adresse=%s, PostNr=%s WHERE Knr=%s",
                (
                    entries["Fornavn"].get(),
                    entries["Etternavn"].get(),
                    entries["Adresse"].get(),
                    entries["PostNr"].get(),
                    kunde_id
                )
            )
            conn.commit()
            label_status.config(text="Kunde oppdatert!")
            fetch_kunder()
            rediger_win.destroy()
        except Exception as e:
            messagebox.showerror("Feil", f"Kunne ikke oppdatere kunde:\n{e}")

    customtkinter.CTkButton(rediger_win, text="Lagre endringer", command=lagre).grid(row=len(labels), column=0, columnspan=2, pady=10)

def open_vare_window():
    vare_win = tk.Toplevel(root)    
    vare_win.title("Vareoversikt")  #Tittel på vindu

    cursor.execute("SHOW COLUMNS FROM vare")                #Henter kolonnene fra vare tabellen
    all_columns = [col[0] for col in cursor.fetchall()]     #Henter kolonnenavnene fra vare tabellen
    visible_columns = [col for col in all_columns if col.lower() != "katnr"]    #Fjerner KatNr kolonnen fra listen

    vare_tree = ttk.Treeview(vare_win, columns=visible_columns, show="headings")    #Oppretter en Treeview for å vise varer
    for col in visible_columns:
        vare_tree.heading(col, text=col)
        vare_tree.column(col, width=100)
    vare_tree.pack(padx=10, pady=10, fill="both", expand=True)

    cursor.execute(f"SELECT {', '.join(visible_columns)} FROM vare")    #Henter alle varene fra vare tabellen
    for row in cursor.fetchall():
        vare_tree.insert("", tk.END, values=row)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(vare_win)

def open_ordre_window():
    ordre_win = tk.Toplevel(root)
    ordre_win.title("Ordreoversikt")    #Tittel på vindu

    cursor.execute("SHOW COLUMNS FROM ordre")             #Henter kolonnene fra ordre tabellen
    ordre_columns = [col[0] for col in cursor.fetchall()]   

    ordre_tree = ttk.Treeview(ordre_win, columns=ordre_columns, show="headings")    #Oppretter en Treeview for å vise ordre
    for col in ordre_columns:
        ordre_tree.heading(col, text=col)
        ordre_tree.column(col, width=100)
    ordre_tree.pack(padx=10, pady=10, fill="both", expand=True)

    cursor.execute("SELECT * FROM ordre")             #Henter alle ordrene fra ordre tabellen
    for row in cursor.fetchall():
        ordre_tree.insert("", tk.END, values=row)

    def show_ordrelinjer_for_selected(event):       #Funksjon for å vise ordrelinjer for valgt ordre
        selected = ordre_tree.selection()           #Henter den valgte ordren i GUI
        if not selected:
            return
        item = ordre_tree.item(selected[0])     #Henter den valgte ordren i GUI
        ordrenr = item['values'][0]

        try:
            knr_index = ordre_columns.index("KNr")      #Henter indeksen til KundeNr kolonnen
            knr = item['values'][knr_index]
        except ValueError:
            messagebox.showerror("Feil", "Kolonnen 'KundeNr' ble ikke funnet i ordre-tabellen.")    #Viser en feilmelding
            return

        cursor.execute("""
            SELECT 
                ordrelinje.OrdreNr, 
                ordrelinje.VNr, 
                vare.Betegnelse,
                ordrelinje.Antall, 
                ordrelinje.PrisPrEnhet,
                (ordrelinje.Antall * ordrelinje.PrisPrEnhet) AS LinjeTotal
            FROM ordrelinje 
            JOIN vare ON ordrelinje.VNr = vare.VNr 
            WHERE ordrelinje.OrdreNr = %s
        """, (ordrenr,))
        rows = cursor.fetchall()

        cursor.execute("SELECT Fornavn, Etternavn, Adresse, PostNr FROM kunde WHERE Knr = %s", (knr,))
        kundeinfo = cursor.fetchone()

        if not rows:
            messagebox.showinfo("Ingen ordrelinjer", f"Ingen ordrelinjer for Ordre {ordrenr}.")
            return

        column_names = ["OrdreNr", "VNr", "Betegnelse", "Antall", "Pris", "LinjeTotal"]
        linje_win = tk.Toplevel(ordre_win)
        linje_win.title(f"Ordrelinjer for Ordre {ordrenr}")
        sv.set_theme(darkdetect.theme())
        apply_theme_to_titlebar(linje_win)

        if kundeinfo:
            kunde_label = tk.Label(
                linje_win,
                text=f"Kunde: {kundeinfo[0]} {kundeinfo[1]}, {kundeinfo[2]}, {kundeinfo[3]}",
                font=("Arial", 11, "italic")
            )
            kunde_label.pack(pady=(10, 5))

        tree = ttk.Treeview(linje_win, columns=column_names, show="headings")
        for col in column_names:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(padx=10, pady=10, fill='both', expand=True)

        total = 0
        total_items = 0
        for row in rows:
            tree.insert("", tk.END, values=row)
            total += float(row[5])
            total_items += row[3]

        summary = f"Antall produkter: {len(rows)}\nAntall varer: {total_items}\nOrdreverdi: {total:.2f} kr"
        total_label = tk.Label(linje_win, text=summary, font=("Arial", 12, "bold"), justify="left")
        total_label.pack(pady=10)
        customtkinter.CTkButton(linje_win, text="skriv ut PDF", command=lambda: print("PDF")).pack(pady=5)  #Knapp for å lage PDF

    ordre_tree.bind("<<TreeviewSelect>>", show_ordrelinjer_for_selected)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(ordre_win)

def start_main_gui():
    global root, entry_vars, kunde_tree, label_status

    root = tk.Tk()
    root.title("Kunderegister (uten Telefonnr)")
    root.geometry("1000x1000")

    frame_form = tk.Frame(root)
    frame_form.pack(pady=10)

    entry_vars = {}
    fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
    for i, field in enumerate(fields):
        tk.Label(frame_form, text=field + ": ").grid(row=i, column=0, sticky="e")
        entry = tk.Entry(frame_form)
        entry.grid(row=i, column=1)
        entry_vars[field] = entry

    customtkinter.CTkButton(frame_form, text="Legg til kunde", command=add_kunde).grid(row=len(fields), column=0, columnspan=2, pady=5)

    label_status = tk.Label(root, text="")
    label_status.pack()

    KUNDE_COLUMNS = ["Knr", "Fornavn", "Etternavn", "Adresse", "PostNr"]
    kunde_tree = ttk.Treeview(root, columns=KUNDE_COLUMNS, show="headings")
    for col in KUNDE_COLUMNS:
        kunde_tree.heading(col, text=col)
        kunde_tree.column(col, width=100)
    kunde_tree.pack(padx=10, pady=10, fill='both', expand=True)

    button_frame = customtkinter.CTkFrame(root)
    button_frame.pack(pady=5)

    customtkinter.CTkButton(button_frame, text="Rediger valgt kunde", command=rediger_kunde).pack(side='left', padx=5)
    customtkinter.CTkButton(button_frame, text="Slett valgt kunde", command=delete_selected_kunde).pack(side='left', padx=5)
    customtkinter.CTkButton(button_frame, text="Vis Vareoversikt", command=open_vare_window).pack(side='left', padx=5)
    customtkinter.CTkButton(button_frame, text="Vis Ordreoversikt", command=open_ordre_window).pack(side='left', padx=5)
    customtkinter.CTkButton(button_frame, text="Vis API", command=lambda: webbrowser.open("http://localhost:5001")).pack(side='left', padx=5)

    sv.set_theme(darkdetect.theme())
    apply_theme_to_titlebar(root)

    fetch_kunder()
    root.mainloop()

def apply_theme_to_titlebar(window):
    version = sys.getwindowsversion()
    if version.major == 10 and version.build >= 22000:
        pywinstyles.change_header_color(window, "#1c1c1c" if sv.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(window, "dark" if sv.get_theme() == "dark" else "normal")
        window.wm_attributes("-alpha", 0.99)
        window.wm_attributes("-alpha", 1)

# --- GUI Funksjoner ---

# --- Innloggingsvindu ---
def Login():
    global mysql_password, conn, cursor
    if Passord.get():
        mysql_password = Passord.get()
        try:
            conn = connect(
                user='root',
                password=mysql_password,
                host='localhost',
                database='varehusdb'
            )
            cursor = conn.cursor()
            api_thread = threading.Thread(target=start_api, daemon=True)
            api_thread.start()                                              #Starter Flask API i bakgrunnen
            login_window.destroy()                                          #Lukker innloggingsvinduet
            start_main_gui()                                                #Starter hovedvinduet
        except Error as e:
            messagebox.showerror("Feil", f"Kunne ikke koble til databasen:\n{e} Feil Passord?") #Ved feil passord

login_window = tk.Tk()
login_window.title("VarehusDB Innlogging")      #Tittel på vindu
login_window.geometry("300x200")                #Størrelse på vindu

label = tk.Label(login_window, text="MySQL root Passord:", font=("Arial", 12, "bold"))  #teksten i vindu
label.pack()

Passord = customtkinter.CTkEntry(login_window, show="*")    #passordfelt
Passord.pack(pady=10)

myButton = customtkinter.CTkButton(login_window, text="Logg inn", command=Login)    #knapp
myButton.pack()

sv.set_theme(darkdetect.theme())
apply_theme_to_titlebar(login_window)

login_window.mainloop()
# --- Innloggingsvindu ---