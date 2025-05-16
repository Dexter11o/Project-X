# Lag en klasse BankKonto som har følgende metoder:
class BankKonto:
    def __init__(self, saldo=0):#definisjon av konstruktør for å opprette en konto med saldo
        self.saldo = saldo

    def sett_inn(self, belop):#definisjon av metode for å sette inn penger
        if belop > 0:
            self.saldo += belop

    def ta_ut(self, belop):#definisjon av metode for å ta ut penger
        if 0 < belop <= self.saldo:
            self.saldo -= belop

    def hent_saldo(self):#definisjon av metode for å hente saldo
        return self.saldo

# Opprette en konto med 1000 kr
konto = BankKonto(1000)

# Setter inn 2600 kr
konto.sett_inn(2600)

# Tar ut 1000 kr
konto.ta_ut(1000)

# Skriver ut saldo
print(konto.hent_saldo())