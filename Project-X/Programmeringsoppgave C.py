# funksjonen som sjekker om en streng er palindrom
def palindrom(tekst):
    # Fjerner mellomrom og gjør teksten til små bokstaver
    tekst = tekst.replace(" ", "").lower()
    # Sjekker om teksten er lik sin egen reverserte versjon
    return tekst == tekst[::-1]  # returnerer True hvis teksten er et palindrom, ellers False

# hovedprogrammet
bruker_input = input("Skriv inn en tekst: ")  # Henter inn tekst fra brukeren
if palindrom(bruker_input):  # Sjekker om teksten er et palindrom
    print(f"{bruker_input} er et palindrom.")  # bekrefterer at teksten er et palindrom
else:
    print(f"{bruker_input} er ikke et palindrom.")  # bekrefterer at teksten ikke er et palindrom
