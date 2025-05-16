#programmeringsoppgave B

# Definerer en funksjon som lager en liste med de første 10 Fibonaccitallene
def fibonacci():
    fib_liste = [0, 1]  # Starter listen med de to første Fibonaccitallene
    while len(fib_liste) < 10:  # Fortsetter å legge til tall til listen har 10 elementer
        # Legger til summen av de to siste tallene i listen
        fib_liste.append(fib_liste[-1] + fib_liste[-2])
    return fib_liste  # Returnerer listen med Fibonaccitallene

# Kaller funksjonen og lagrer resultatet i variabelen 'fib_tall'
fib_tall = fibonacci()

# Skriver ut listen med Fibonaccitall
print(fib_tall)

# Definerer en funksjon som lager en liste med de første 10 primtallene
def primtall():
    prim_liste = []  # Starter en tom liste for primtall
    num = 2  # Starter med det første primtallet
    while len(prim_liste) < 10:  # Fortsetter til listen har 10 primtall
        is_prime = True  # Anta at tallet er primtall
        for i in range(2, int(num**0.5) + 1):  # Sjekker om tallet er delelig med noen tall opp til kvadratroten av tallet
            if num % i == 0:  # Hvis det er delelig, er det ikke et primtall
                is_prime = False
                break
        if is_prime:  # Hvis tallet er et primtall, legg det til listen
            prim_liste.append(num)
        num += 1  # Gå videre til neste tall
    return prim_liste  # Returnerer listen med primtallene
# Kaller funksjonen og lagrer resultatet i variabelen 'prim_tall'
prim_tall = primtall()
# Skriver ut listen med primtall
print(prim_tall)