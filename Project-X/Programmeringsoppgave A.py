#definerer en funksjon som konverterer Celsius til Fahrenheit
def temp(c):
    return c * 9/5 + 32

#henter inn temperatur i Celsius fra brukeren
c = float(input("Skriv inn temperatur i Celsius: ")) 
# Konvertering fra Celsius til Fahrenheit ved hjelp av funksjonen temp
f = temp(c)  

# Skriver ut hva temperaturen i celsius er i Fahrenheit.
print(f"{c} grader Celsius er {f} grader Fahrenheit.")