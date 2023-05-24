## Erste Schritte

### Eingabe und Quellen

Um mit pYMLedger zu beginnen, können Sie CSV-Exporte von Ihrem Online-Banking verwenden. Alternativ können Sie die mitgelieferten Beispieldateien im Verzeichnis `input/samples` für Testzwecke verwenden.

#### CSV-Dateien von der Bank

Verwenden Sie die originalen `.csv`-Dateien, die von Ihrer Bank exportiert wurden. Die Dateien sollten im **CAMT-CSV**-Format vorliegen.

**(Die Spalten in der CSV-Datei MÜSSEN durch (`,`) Kommas getrennt sein)**

_Die CSV-Datei sollte die folgenden Spalten enthalten:_
```csv
Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info
```

#### Verzeichnisstruktur

Stellen Sie sicher, dass das Eingabe-Verzeichnis (`input/`) folgende Struktur aufweist:

```
├── input/
│   ├── 2023/
│   │   ├── 2023-01/
│   │   │   └── 2023-01.bank.csv
│   │   ├── 2023-02/
│   │   │   └── 2023-02.bank.csv
│   │   └── 2023-03/
```

_Verwenden Sie das Format "YYYY" für das Jahr, "YYYY-MM" für den Ordner (pro Monat) und "YYYY-MM.bank.csv" für die CAMT-CSV-Datei._

#### CSV Dateien bereinigen

Bevor wir aus den CSV-Dateien `rules` und `journals` generieren, sollten wir diese erstmal etwas "säuber", mit den Befehl:

```bash
python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml clean-up-csv 2023
```

_Die CSV-Dateien aus den [../input/2023](input/2023) (für das Jahr **`2023`**) werden etwas "gesäubert" und in [../source/2023](source/2023/) gepackt._



### Lastschrift, Überweisungen, etc. - (gemeinsame) Regeln

Lassen Sie uns nun die CSV-Dateien im Verzeichnis [../source/2023](source/2023/) betrachten. Dort sollten alle monatlichen Kontoauszüge unserer Bank zu finden sein.
Wir können uns zunächst auf die **Ausgaben** (`Expenses`) konzentrieren und Zeile für Zeile durchgehen, um für jeden Eintrag/Ausgabe eine `rule` zu erstellen.

#### Beispiel: Wohnen

Betrachten wir beispielsweise die CSV-Datei für Januar 2023. Darin befindet sich eine Zeile mit dem Verwendungszweck "Wohnen" (wichtig sind hier nur die Spalten "Verwendungszweck" und "Begünstigter/Zahlungspflichtiger").

**([source/2023/2023-01/csv/2023-01.bank.csv](../source/2023/2023-01/csv/2023-01.bank.csv))**
```csv
****,02.01.23,02.01.23,DAUERAUFTRAG,1234/4568.00001.12,***,,,****,,,Wohnen GmbH,,,"-499,2",EUR,Umsatz gebucht,2023-01.0031,Wohnen GmbH
```

* Verwendungszweck: `1234/4568.00001.12`
* Beguenstigter/Zahlungspflichtiger: `Wohnen GmbH`

Für diesen Eintrag könnten wir ganz einfach eine `rule` in unserer [config.yml](config.yml) anlegen:

**[config.yml](config.yml)**
```yml
common_rules:
  # Wohung/Miete 
  - if:
      - 1234/4567.00001.12.*Wohnen GmbH
    description: Miete
    account: Expenses:Wohnen:Miete
```

_Regeln für Lastschrift, Überweisungen usw. befinden sich im Block `common_rules`._




#### Erstellung der Regeln

Nachdem wir die Regeln in unsere `config.yml` eingetragen haben, können wir die [hledger rules](https://hledger.org/1.29/hledger.html#csv-rules-cheatsheet) mit dem folgenden Befehl erstellen:

```bash
python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023
```

_Die Regeln werden im Verzeichnis [journals/2023/rules/](../journals/2023/rules) gespeichert._

**common.csv.rules**
```journal
if 1234/4568.00001.12.*Wohnen GmbH
    description %beguenstigter_zahlungspflichtiger | Miete
    account1    Expenses:Wohnen:Miete      
```


### Journals

Nachdem alle möglichen `rules` in unsere `config.yml` eingetragen wurden (und die Regeln erstellt wurden), können wir auch die `journal`s erstellen lassen:

```bash
python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023
python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023
```

_Die erstellten Journals werden im Verzeichnis [journals/2023/](../journals/2023) gespeichert._

**2023-01.bank.hledger**
```hledger
2023-01-02=2023-01-02 * (2023-01.0030) Wohnen GmbH | Miete  ; type:DAUERAUFTRAG, payee:Wohnen GmbH
    Expenses:Wohnen:Miete       EUR499,20
    Assets:Bank:Checking       EUR-499,20
```



### Budgetierung

Wenn alle Regeln für die Ausgaben eingetragen wurde, geht weiter zum [budgetieren](BUDGET.md)


### Spezielle Regeln - Amazon

Um komplexe Regeln für [Amazon-Bestellungen](AMAZON.md) und [PayPal-Käufe](PAYPAL.md) zu vermeiden, können wir vordefinierte Regeln generieren lassen.

**config.yml**
```yml
amazon_rules:
  - if: 
      - Audible.de.*AUDIBLE GMBH
      - Audible GmbH.*AUDIBLE GMBH
    description: Amazon Audible GmbH Hörbuch
    account: Expenses:Unterhaltung:Multimedia:Streaming:Abo:Amazon:Audible
  - if: 
      - AMZNPrime DE.*AMAZON EU S.A R.L.
      - Prime Video.*AMAZON DIGITAL GERMANY GMBH
    description: Amazon Prime
    account: Expenses:Unterhaltung:Multimedia:Streaming:Abo:Amazon:Prime
```


### Mehr

Siehe [mehr](MORE.md), um zu erfahren wie Bargeld, Abgleichungen und weitere Checks funktionieren.