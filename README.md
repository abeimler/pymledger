# pYMLedger - python hledger generator

pYMLedger ist eine Projekt-Vorlage fürs [PTA](https://plaintextaccounting.org/), basierent auf [hledger](https://hledger.org/).
Zusammen mit den Python-Skript [hledger-rules](scripts/hledger-rules) ist es möglich hledger-Regeln und -Buchungen aus einer Konfigurationsdatei im YAML-Format zu generieren.

## Funktionen

- CSV-Bereinigung: [hledger-rules](scripts/hledger-rules) bietet Funktionen zum Bereinigen von CSV-Dateien vor der Generierung von hledger-Regeln und -Buchungen.
- Generierung von hledger-Regeln: Das Skript kann hledger-Regeln basierend auf der in der `config.yml`-Datei angegebenen Konfiguration generieren.
- Generierung von hledger-Buchungen: Es kann auch hledger-Buchungen aus CSV-Eingabedateien generieren.
- Vorgegebene und häufig verwendete Aufgaben: pYMLedger enthält eine `Taskfile.yaml`, die vordefinierte Aufgaben für eine einfachere Ausführung enthält.
- Docker-Unterstützung: Das Skript kann in einem Docker-Container ausgeführt werden, zusammen mit [hledger-web](https://hledger.org/1.29/hledger-web.html) für eine webbasierte Oberfläche.
- Budgetierung und Prognose: [hledger-rules](scripts/hledger-rules) unterstützt Funktionen zur Budgetierung und Prognose.

## Installation und Abhängigkeiten

Bevor Sie [hledger-rules](scripts/hledger-rules/hledger-rules.py) verwenden, stellen Sie sicher, dass die folgenden Abhängigkeiten installiert sind:

- [python3](https://www.python.org/downloads/)
- Python-Abhängigkeiten: Installieren Sie die erforderlichen Python-Abhängigkeiten mit dem Befehl `pip install -r ./scripts/pymledger/requirements.txt`.
- [hledger](https://hledger.org/install.html)
- [hledger-web](https://hledger.org/install.html)
- [task](https://taskfile.dev/installation/)
- [ledger2beancount](https://github.com/beancount/ledger2beancount) (optional)


## Schnell-Start

Um mit dein [PTA](https://plaintextaccounting.org/) schnell zu beginnen, folgen Sie einfach diesen Schritten:

1. **Eingabe und Quellen:**
   Verwenden Sie CSV-Exporte (**Im [CAMT-CSV Format](https://de.wikipedia.org/wiki/Camt-Format)**) von Ihrem Online-Banking oder die mitgelieferten [Beispieldateien](examples/input/) für Testzwecke und speicher die .csv-Dateien in [`input/`](input/), siehe [Verzeichnisstruktur](doc/GETSTARTED.md#verzeichnisstruktur).

2. **CSV-Dateien bereinigen:**
   Führen Sie den Befehl aus, um die CSV-Dateien zu bereinigen und in das Verzeichnis `source` zu verschieben:
   ```bash
   python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml clean-up-csv 2023
   ```

3. **Regeln erstellen:**
   Erstellen Sie Regeln für Lastschriften, Überweisungen usw. im Block `common_rules` in der Datei `config.yml`, siehe [Erste Schritte](doc/GETSTARTED.md#erstellung-der-regeln) für mehr details.

4. **Regeln generieren:**
   Generieren Sie die Regeln mit dem folgenden Befehl:
   ```bash
   python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023
   ```

5. **Journale erstellen:**
   Erstellen Sie die Journale mit den erstellten Regeln:
   ```bash
   python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023
   ```

6. **Budgetierung:**
   Sobald alle Ausgabenregeln eingetragen sind, können Sie zur [Budgetierung](doc/BUDGET.md) übergehen.

7. **Spezielle Regeln:**
   Wenn Sie komplexe Regeln für Amazon-Bestellungen und PayPal-Käufe verwenden möchten, können Sie vordefinierte Regeln in die `config.yml` Datei eintragen. Weitere Informationen finden Sie in [doc/Amazon](doc/AMAZON.md) und [doc/PayPal](doc/PAYPAL.md).

Möchten Sie weitere Informationen und detaillierte Anweisungen? Lesen Sie [hier mehr](doc/GETSTARTED.md).


### Beispiel

Beispiel einer **config.yml**:

**config.yml**
```yml
title: 'Persönliche Finanzen'
define_accounts:
  - account: 'Assets'       
    type: Asset
  - account: 'Liabilities'  
    type: Liability
  - account: 'Equity'       
    type: Equity
  - account: 'Income'     
    type: Revenue
  - account: 'Expenses'   
    type: Expense
  - account: 'Assets:Bank'
    type: Cash
  - account: 'Assets:Cash'
    type: Cash
  - account: 'Assets:Saving'
    type: Cash
  - account: 'Assets:Saving:Cash'
    type: Cash
accounts:
  assets: 'Assets'
  expenses: 'Expenses'
  liabilities: 'Liabilities'
  equity: 'Equity'
  income: 'Income'
  opening: 'Equity:OpeningClosingBalances'
  checking: 'Assets:Bank:Checking'
  paypal_unknown: 'Expenses:unknown:PayPal'
  amazon_unknown: 'Expenses:unknown:Amazon'
  unknown: 'Expenses:unknown'
  cash: 'Assets:Cash'
  salary: 'Income:Salary'
  budget: 'Assets:Bank:Budget'
  saving: 'Assets:Bank:Saving'
  unbudget: 'Assets:Bank:Unbudget'
common_rules:
  # Defaults/Fallbacks (first)
  - if:
      - Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
      - Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
      - AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description: Amazon %verwendungszweck
    account: Expenses:unknown:Amazon
  - if: PP.6330.PP.*PayPal
    description: PayPal %verwendungszweck
    account: Expenses:unknown:PayPal
  - if: KARTENZAHLUNG
    description: Kartenzahlung %verwendungszweck 
    account: Expenses:unknown:%beguenstigter_zahlungspflichtiger
  # Bank (und Gebühren)
  - if: ABSCHLUSS.*Abrechnung
    account: Expenses:Sonstiges:Bankgebuehren 
  - if: ENTGELTABSCHLUSS.*Entgeltabrechnung
    payee_description: 'Entgeltabrechnung'
    account: Expenses:Sonstiges:Bankgebuehren 
  - if:
      - AUSZAHLUNG
      - AUSZAHLUNG
    account: Assets:Cash
    description: Kartenauszahlung
  - if:
      - EINZAHLUNG
      - EINZAHLUNG
    account: Assets:Cash
    description: Karteneinzahlung
  # Lohn
  - if: LOHN.*GEHALT
    account1: Assets:Bank:Checking                                                                                               
    account2: Income:Salary  
    income: true
  # Wohung/Miete 
  - if:
      - 546789123.*Strom GmbH
      - ONLINE-UEBERWEISUNG.*Strom GmbH
    description: Strom GmbH
    account: Expenses:Wohnen:Nebenkosten:Strom
  - if:
      - 1234/4568.00001.12.*Wohnen GmbH
    customer: 1234/4568.00001.12
    description: Wohnen GmbH
    account: Expenses:Wohnen:Miete
```

Beispiel der erstellten **common.csv.rules**:

```hledger
if Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
AMZN Mktp DE.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND'
    description %beguenstigter_zahlungspflichtiger | Amazon %verwendungszweck
    account1    Expenses:unknown:Amazon                                         


if PP.6330.PP.*, Ihr Einkauf bei.*PayPal'
PP.6330.PP.*, Ihr Einkauf bei.*PAYPAL'
PP.6330.PP.*PayPal
PP.6330.PP.*PAYPAL
    description %beguenstigter_zahlungspflichtiger | PayPal %verwendungszweck
    account1    Expenses:unknown:PayPal                                         


if KARTENZAHLUNG
    description %beguenstigter_zahlungspflichtiger | Kartenzahlung %verwendungszweck
    account1    Expenses:unknown:%beguenstigter_zahlungspflichtiger             


if AUSZAHLUNG
AUSZAHLUNG
    description Kartenauszahlung
    account1    Assets:Cash                                                     


if EINZAHLUNG
EINZAHLUNG
    description Karteneinzahlung
    account1    Assets:Cash                                                     


if LOHN.*GEHALT.*Arbeit GmbH
    description %beguenstigter_zahlungspflichtiger | Einkommen von Arbeit GmbH
    account1    Assets:Bank:Checking                                            
    account2    Income:Salary                                                   
    amount      %amount                                                         


if 546789123.*Strom GmbH
ONLINE-UEBERWEISUNG.*Strom GmbH
    description %beguenstigter_zahlungspflichtiger | Strom GmbH
    account1    Expenses:Wohnen:Nebenkosten:Strom                               


if 1234/4568.00001.12.*Wohnen GmbH
    description %beguenstigter_zahlungspflichtiger | Wohnen GmbH
    account1    Expenses:Wohnen:Miete                                           

```


---

### hledger-web

Nachdem alle möglichen Regeln, Transaktionen und Journals erstellt wurden, können wir [hledger-web](https://hledger.org/1.29/hledger-web.html) nutzen, um alles schön darzustellen:

```bash
python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023
python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml clean-up-csv 2023
python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023
python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-all 2023
hledger-web -f all.hledger --capabilities=view --auto
```


---

## Disclaimer

Ich bin kein Finanzberater und das Tool ist auch mehr zum Budgeten gedacht.
Die Tabelle und die Beispiele, die du hier siehst, sind alle fiktiv, basieren aber auf realen Kontoauszügen (wie Amazon, PayPal usw.). Verwende dieses Projekt als Vorlage für dein [PTA (Plain Text Accounting)](https://plaintextaccounting.org/), am besten in Kombination mit Git, um alles Mögliche zu verfolgen und die Automatisierung deiner Kontoauszüge (Eingabedateien im CSV-Format) zu maximieren. Behalte dabei alle privaten Daten für dich.


### Lizenz

Die Lizenz für die Software findest du in der Datei [LICENSE](LICENSE).


### Limitierung

* "Open" und "Closing" pro Monat: Derzeit bauen alle Monate noch aufeinander auf (Kontoauszüge usw.), sodass sie noch nicht unabhängig voneinander sind.
* TODO: Erstellung von Diagrammen/Charts
* Die Verwendung mehrerer Banken ist nicht möglich.
* Budget aufteile in ein Monats sind nicht möglich (es ist nur möglich den Monatstag zum budgeten zu ändern)



## Links

- https://plaintextaccounting.org/
- https://hledger.org/import-csv.html
- https://hledger.org/cookbook.html
- https://hledger.org/budgeting.html
- https://hledger.org/accounting.html