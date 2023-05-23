# pYMLedger - python hledger generator

[hledger-rules](scripts/hledger-rules) ist ein Python-Skript und ein Hilfsprogramm zur Generierung von hledger-Regeln und -Buchungen aus einer Konfigurationsdatei im YAML-Format.

## Funktionen

- CSV-Bereinigung: pYMLedger bietet Funktionen zum Bereinigen von CSV-Dateien vor der Generierung von hledger-Regeln und -Buchungen.
- Generierung von hledger-Regeln: Das Skript kann hledger-Regeln basierend auf der in der `config.yml`-Datei angegebenen Konfiguration generieren.
- Generierung von hledger-Buchungen: Es kann auch hledger-Buchungen aus CSV-Eingabedateien generieren.
- Vorgegebene und häufig verwendete Aufgaben: pYMLedger enthält eine `Taskfile.yaml`, die vordefinierte Aufgaben für eine einfachere Ausführung enthält.
- Docker-Unterstützung: Das Skript kann in einem Docker-Container ausgeführt werden, zusammen mit hledger-web für eine webbasierte Oberfläche.
- Budgetierung und Prognose: pYMLedger unterstützt Funktionen zur Budgetierung und Prognose.

## Installation und Abhängigkeiten

Bevor Sie pYMLedger verwenden, stellen Sie sicher, dass die folgenden Abhängigkeiten installiert sind:

- [python3](https://www.python.org/downloads/)
- Python-Abhängigkeiten: Installieren Sie die erforderlichen Python-Abhängigkeiten mit dem Befehl `pip install -r ./scripts/pymledger/requirements.txt`.
- [hledger](https://hledger.org/install.html)
- [hledger-web](https://hledger.org/install.html)
- [task](https://taskfile.dev/installation/)
- [ledger2beancount](https://github.com/beancount/ledger2beancount) (optional)


## Erste Schritte

### Eingabe und Quellen

Um mit pYMLedger zu beginnen, können Sie CSV-Exporte von Ihrem Online-Banking verwenden. Alternativ können Sie die mitgelieferten Beispieldateien im Verzeichnis `input/samples` für Testzwecke verwenden.

##### CSV-Dateien von der Bank

Verwenden Sie die originalen `.csv`-Dateien, die von Ihrer Bank exportiert wurden. Die Dateien sollten im **CAMT-CSV**-Format vorliegen.

**(Die Spalten in der CSV-Datei MÜSSEN durch (`,`) Kommas getrennt sein)**

_Die CSV-Datei sollte die folgenden Spalten enthalten:_
```csv
Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info
```

##### Verzeichnisstruktur

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
python3 ./scripts/pymledger/pymledger.py -c config.yml clean-up-csv 2023
```

_Die CSV-Dateien aus den [input/2023](input/2023) (für das Jahr **`2023`**) werden etwas "gesäubert" und in [source/2023](source/2023/) gepackt._



### Lastschrift, Überweisungen, etc. - (gemeinsame) Regeln

Lassen Sie uns nun die CSV-Dateien im Verzeichnis [source/2023](source/2023/) betrachten. Dort sollten alle monatlichen Kontoauszüge unserer Bank zu finden sein.
Wir können uns zunächst auf die **Ausgaben** (`Expenses`) konzentrieren und Zeile für Zeile durchgehen, um für jeden Eintrag/Ausgabe eine `rule` zu erstellen.

#### Beispiel: Wohnen

Betrachten wir beispielsweise die CSV-Datei für Januar 2023. Darin befindet sich eine Zeile mit dem Verwendungszweck "Wohnen" (wichtig sind hier nur die Spalten "Verwendungszweck" und "Begünstigter/Zahlungspflichtiger").

**([source/2023/2023-01/csv/2023-01.bank.csv](source/2023/2023-01/csv/2023-01.bank.csv))**
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
python3 ./scripts/pymledger/pymledger.py -c config.yml gen-rules 2023
```

_Die Regeln werden im Verzeichnis [journals/2023/rules/](journals/2023/rules) gespeichert._

**common.csv.rules**
```journal
if 1234/4568.00001.12.*Wohnen GmbH
    description %beguenstigter_zahlungspflichtiger | Miete
    account1    Expenses:Wohnen:Miete      
```


### Journals

Nachdem alle möglichen `rules` in unsere `config.yml` eingetragen wurden (und die Regeln erstellt wurden), können wir auch die `journal`s erstellen lassen:

```bash
python3 ./scripts/pymledger/pymledger.py -c config.yml gen-rules 2023
python3 ./scripts/pymledger/pymledger.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023
```

_Die erstellten Journals werden im Verzeichnis [journals/2023/](journals/2023) gespeichert._

**2023-01.bank.hledger**
```hledger
2023-01-02=2023-01-02 * (2023-01.0030) Wohnen GmbH | Miete  ; type:DAUERAUFTRAG, payee:Wohnen GmbH
    Expenses:Wohnen:Miete       EUR499,20
    Assets:Bank:Checking       EUR-499,20
```


### Budgetierung

#### Standard-Budget

Es wäre sinnvoll, für Ausgaben (z.B. `Expenses:Wohnen:Miete`) auch ein Budget festzulegen:

**config.yml**
```yml
monthly:
  # Standardbudget für den Monat
  budget:
    # Wohnung
    - account: Assets:Bank:Budget:Wohnen
      amount: 500.0
      comment: Miete
```

#### Transaktionen

Damit die Ausgaben (z.B. `Expenses:Wohnen:Miete`) vom Budget (z.B. `Assets:Bank:Budget:Wohnen`) abgezogen werden, müssen wir eine `transaction` in unserer `config.yml` definieren:

**config.yml**
```yml
transactions:
  # Wohnung
  - expense: Expenses:Wohnen
    asset: Assets:Bank:Budget:Wohnen
```

#### Einkommen

Schließlich müssen wir nur noch sicherstellen, dass unser Budget (z.B. `Assets:Bank:Budget:Wohnen`) auch irgendwoher kommt, idealerweise vom "Einkommen". Dazu müssen wir nur eine Regel für das `income` in unserer `config.yml` definieren:

**config.yml**
```yml
common_rules:
  # Lohn
  - if: LOHN.*GEHALT.*Arbeit GmbH
    description: Einkommen von Arbeit GmbH
    account1: Assets:Bank:Checking                                                                                               
    account2: Income:Salary  
    income: true
```

_("Arbeit GmbH" ist hier nur ein Beispiel, schauen Sie einfach nach, wie es in Ihrem Kontoauszug (CSV) aussieht)._

**2023-01.bank.csv**
```csv
***,30.01.23,30.01.23,LOHN GEHALT,LOHN / GEHALT,***,,,****,,,Arbeit GmbH,,,2100,EUR,Umsatz gebucht,2023-01.0002,Arbeit GmbH
```

### hledger-web

Nachdem alle möglichen Regeln, Transaktionen und Journals erstellt wurden, können wir [hledger-web](https://hledger.org/1.29/hledger-web.html) nutzen, um alles schön darzustellen:

```bash
python3 ./scripts/pymledger/pymledger.py -c config.yml gen-rules 2023
python3 ./scripts/pymledger/pymledger.py -c config.yml clean-up-csv 2023
python3 ./scripts/pymledger/pymledger.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023
python3 ./scripts/pymledger/pymledger.py --hledger-path=/usr/bin/hledger -c config.yml gen-all 2023
hledger-web -f all.hledger --capabilities=view --auto
```

---

### Spezielle Regeln - Amazon und PayPal

Um komplexe Regeln für Amazon-Bestellungen und PayPal-Käufe zu vermeiden, können wir vordefinierte Regeln generieren lassen.

### Amazon

#### Standardregel - allgemein

Um vorerst alle möglichen Amazon-Käufe zu kategorisieren, können wir die folgende Regel verwenden:

**config.yml**
```yml
common_rules:
  # Defaults/Fallbacks (first)
  - if:
      - Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
      - Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
      - AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
      - AMZN Mktp DE.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND'
    description: Amazon %verwendungszweck
    account: Expenses:unknown:Amazon
```
Damit werden alle Amazon-Käufe dem Konto `Expenses:unknown:Amazon` zugewiesen.



#### Monatliche Amazon-Käufe

Um die verschiedenen Amazon-Käufe zu kategorisieren, legen wir eine Regel als Fallback fest:

**config.yml**
```yml
amazon:
  # python format with order and ref, {order}.*Amazon.de.*{ref}.*AMAZON EU
  if_format:
    - '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND'
    - '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.'
    - '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.'
    - '{order}.*AMZN Mktp DE{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND'
  payee: 'AMAZON PAYMENTS EUROPE S.C.A.'
```

Passen Sie die `if_format` entsprechend Ihrer Kontenauszüge an, um die Amazon-Ausgaben zu identifizieren:

##### Beispiel

**2023-01.bank.csv**
```csv
***,30.01.23,30.01.23,FOLGELASTSCHRIFT,123-1234567-1234567 AMZN Mktp DE AAAAAAAAAAAAAAAA,***,,,****,,,AMAZON PAYMENTS EUROPE S.C.A.,,,"-55,95",EUR,Umsatz gebucht,2023-01.0007,AMAZON PAYMENTS EUROPE S.C.A.
```

Beachten Sie die Spalte "Verwendungszweck": `123-1234567-1234567 AMZN Mktp DE AAAAAAAAAAAAAAAA`.

* Bestellnummer.: `123-1234567-1234567`
* Referenz: `AAAAAAAAAAAAAAAA`

Daraus ergibt sich das `if_format`: `{order}.*Amazon .Mktplce{ref}`


#### Amazon-Bestellungen

Nachdem wir die Journale für das Jahr 2023 erstellt haben, finden Sie im Verzeichnis `source/` eine Vorlage für die Amazon-Bestellungen: [template.2023-01.amazon.yaml](source/2023/2023-01/template.2023-01.amazon.yaml)


**template.2023-01.amazon.yaml**
```yml
- account: Expenses:unknown:Amazon
  amount: -55.95
  order: 123-1234567-1234567
  payee: AMAZON PAYMENTS EUROPE S.C.A.
  ref: AAAAAAAAAAAAAAAA
```

Diese Vorlage können wir verwenden, um die echten Bestellungen in [2023-01.amazon.yaml](source/2023/2023-01/2023-01.amazon.yaml) einzutragen:

```yaml
- account: Expenses:Haushalt:Amazon
  order: 123-1234567-1234567
```

_Wir können einfach `order` verwenden, um einem (Ausgaben-)Konto zuzuweisen._
_Optional kann auch `ref` verwendet werden, wenn die Bestellnummer (`order`) mehrmals vorkommt._

```yml
- account: Expenses:Haushalt:Amazon
  order: 123-1234567-1234599
  ref: CCCCCCCCCCCCCCCC
```

_Vergleichen Sie die Bestellnummer (`order`) einfach auf [amazon.de](amazon.de) unter "Meine Bestellungen"._

**Die `template.amazon.yaml` ist nicht perfekt und es könnten Bestellungen fehlen oder nicht aus den Kontenauszügen (CSV) erkannt werden.**



#### Allgemeine Amazon-Regeln

Wenn wir wiederkehrende Ausgaben oder Regeln für Amazon haben, können wir diese einfach in der `config.yml` festlegen:

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


### PayPal

#### Standardregel - allgemein

Um vorerst alle möglichen PayPal-Käufe zu kategorisieren, legen wir eine Regel als Fallback fest:

**config.yml
```yml
common_rules:
  # Defaults/Fallbacks (first)
  - if: 
      - PP.6330.PP.*, Ihr Einkauf bei.*PayPal'
      - PP.6330.PP.*, Ihr Einkauf bei.*PAYPAL'
      - PP.6330.PP.*PayPal
      - PP.6330.PP.*PAYPAL
    description: PayPal %verwendungszweck
    account: Expenses:unknown:PayPal
```

_Damit werden alle PayPal-Käufe dem Konto `Expenses:unknown:PayPal` zugewiesen._



#### Monatliche PayPal-Käufe

Um die PayPal-Regeln zu nutzen, müssen sie zuerst in der `config.yml` definiert werden:

**config.yml**
```yml
paypal:
  # python format with ref and name, {ref}.*PP.6330.PP.*{name}, Ihr Einkauf bei.*PayPal
  if_format:
    - '{ref}.*PP.6330.PP.*{name}.*, Ihr Einkauf bei.*PayPal'
    - '{ref}.*PP.6330.PP.*{name}.*, Ihr Einkauf bei.*PAYPAL'
  payee: 'PayPal Europe S.a.r.l. et Cie S.C.A' 
```

Passen Sie die `if_format` entsprechend Ihrer Kontenauszüge an, um die PayPal-Ausgaben zu identifizieren:

##### Beispiel

**2023-01.bank.csv**
```csv
****,03.01.23,03.01.23,FOLGELASTSCHRIFT,"1234567893215 PP.6330.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com",***,,,****,,,PayPal Europe S.a.r.l. et Cie S.C.A,,,"-25,79",EUR,Umsatz gebucht,2023-01.0025,PayPal Europe S.a.r.l. et Cie S.C.A
```

Beachten Sie die Spalte "Verwendungszweck": `1234567893215 PP.6330.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com`.

* Referenz: `1234567893215`
* Suffix: `PP.6330.PP`
* Name: `www.steampowered.com`

Daraus ergibt sich das `if_format`: `{ref}.*PP.6330.PP.*{name}, Ihr Einkauf bei.*`



#### Monatliche PayPal-Käufe

Nachdem wir die Journale für das Jahr 2023 erstellt haben, finden Sie im Verzeichnis `source/` eine Vorlage für die PayPal-Käufe: [template.2023-01.paypal.yaml](source/2023/2023-01/template.2023-01.paypal.yaml)

**template.2023-01.paypal.yaml**
```yml
- account: Expenses:unknown:PayPal
  amount: -21.85
  payee: PayPal Europe S.a.r.l. et Cie S.C.A
  ref: '1234567893214'
```

Diese Vorlage können wir verwenden um die echten Käufe in [2023-01.paypal.yaml](source/2023/2023-01/2023-01.paypal.yaml) einzutragen:

**2023-01.paypal.yaml**
```yml
- account: Expenses:Lebensmittel:Essen:Pizza
  ref: '1234567893214'
```

_Wir können einfach `ref` (Referenz) verwenden, um einem (Ausgaben-)Konto zuzuweisen._

**2023-01.paypal.yaml**
```yml
- account: Expenses:Hobbies:Gaming:Steam
  description: Steam (Gaming) 
  name: steampowered
```

Idealerweise ist der `name` aussagekräftiger, leider ist dieser nicht immer vorhanden.

_Leider ist die `ref` (Referenz) nicht unter "PayPal" -> "Meine Aktivitäten" zu finden. Du musst also genauer auf das Datum, den `name` (falls vorhanden) und den `amount` (Betrag) achten, um festzustellen, was du gekauft hast und welchem `account` du es zuweisen möchtest._

**Die `template.paypal.yaml` ist nicht perfekt und es könnten Käufe fehlen oder nicht aus den Kontenauszügen (CSV) erkannt werden.**



#### Allgemeine PayPal-Regeln

Wenn wir wiederkehrende Ausgaben oder Regeln für PayPal haben, können wir diese einfach in der `config.yml` festlegen:

**config.yml**
```yml
paypal_rules:
  # Gaming
  - name:
      - Steam
      - STEAM
      - steampowered
    description: Steam
    account: Expenses:Hobbies:Gaming:Steam
  - name: 
      - GOG
    description: GOG
    account: Expenses:Hobbies:Gaming:GOG
  - name: 
      - Nintendo
      - NINTENDO
    description: Nintendo
    account: Expenses:Hobbies:Gaming:Nintendo
```



## Budgetierung

Für jeden Monat wird ein [2023-01.budget.yaml](source/2023/2023-01/2023-01.budget.yaml) erstellt, basiert `config.yml` und [template.2023-01.budget.yaml](source/2023/2023-01/template.2023-01.budget.yaml).
Diese Datei wird einmal erstellt und kann dann (ähnlich wie `2023-01.amazon.yaml` und `2023-01.paypal.yaml`) nach belieben angepasst werden, abhänig von deiner Situation und des Monats.

Für jeden Monat wird eine Budgetdatei erstellt, die auf `config.yml` und dem entsprechenden Template basiert. Die Budgetdatei für Januar 2023 befindet sich unter [source/2023/2023-01/2023-01.budget.yaml](source/2023/2023-01/2023-01.budget.yaml). Du kannst diese Datei nach Belieben anpassen, ähnlich wie die Dateien `2023-01.amazon.yaml` und `2023-01.paypal.yaml`, um sie an deine individuelle Situation und den aktuellen Monat anzupassen.

## Überprüfung (Checking)

Das `account` `Assets:Bank:Checking` sollte den Betrag auf deinem Bankkonto oder die Einnahmen/Ausgaben aus der (input) .csv-Datei widerspiegeln.

Möglicherweise musst du die Eröffnungsbilanz in der Datei [all.hledger](all.hledger) anpassen:

```hledger
2023/01/01 * opening balances   ; opening:
    Assets:Bank:Checking                                                  2179,78 EUR
    Assets:Saving:Cash                                                    2000,00 EUR  
    Assets:Cash                                                             50,50 EUR  
    Equity:OpeningClosingBalances
```

#### Abgleich (reconcile)

Um sicherzustellen, dass dein Bankkonto mit der tatsächlichen Bankübereinstimmt, kannst du einige Abgleichseinträge erstellen. Dafür kannst du für jeden Monat eine Datei mit dem Format `YYYY-MM.reconcile.yml` anlegen. Hier ist ein Beispiel für den Januar 2023:

**source/2023/2023-01/2023-01.reconcile.yml**
```yml
- day: 15
  amount: 1364.65
```

## Bargeld

Die Informationen zu den Bargeldtransaktionen findest du in der Datei `YYYY-MM.cash.yml`. Hier ein Beispiel für eine Transaktion:

**source/2023/2023-01/2023-01.cash.yml**
```yml
- day: 15
  amount: 21.84
  description: Einkaufen Rewe
  account: Expenses:Lebensmittel:Einkaufen:Rewe
```

Du kannst weitere Bargeldtransaktionen in der Datei hinzufügen, um deine Ausgaben in bar im Januar 2023 zu verfolgen.


## Weitere checks

Versuche dein Budget nicht zu überstrapazieren. Das Hauptziel des Programms ist es, dein Budget sowie Ein- und Ausgaben im Überblick zu behalten. Dein `Assets:Bank:Checking` sollte immer die Transaktionen deines realen Bankkontos widerspiegeln (das sollte einfach sein, wenn du die Eingabedatei im CSV-Format von der Bank verwendest).

Das Budget (`Assets:Bank:Budget`) sollte immer niedriger sein als der Betrag in `Assets:Bank:Checking`. Um zu sehen, wie viel du noch budgetieren kannst, kannst du den Kontostand des `Assets:Bank:Unbudget`-Kontos überprüfen (dieses Konto wird automatisch erstellt).

Halte immer ein Auge auf die Fallback-Konten `Expenses:unknown`. Hier landen Einträge, denen noch kein spezifisches Konto zugeordnet wurde (z.B. `Expenses:unknown:PayPal`, `Expenses:unknown:Amazon`, `Expenses:unknown:UnbekanntesGeschaeft`, ...).

```bash
hledger -f all.hledger -s --auto check
hledger -f all.hledger reg --auto Expenses:unknown
```

## Disclaimer

Die Tabelle und die Beispiele, die du hier siehst, sind alle fiktiv, basieren aber auf realen Kontoauszügen (wie Amazon, PayPal usw.). Verwende dieses Projekt als Vorlage für dein [PTA (Plain Text Accounting)](https://plaintextaccounting.org/), am besten in Kombination mit Git, um alles Mögliche zu verfolgen und die Automatisierung deiner Kontoauszüge (Eingabedateien im CSV-Format) zu maximieren. Behalte dabei alle privaten Daten für dich.

### Lizenz

Die Lizenz für die Software findest du in der Datei [LICENSE](LICENSE).


### Limitirungen

* "Open" und "Closing" pro Monat: Derzeit bauen alle Monate noch aufeinander auf (Kontoauszüge usw.), sodass sie noch nicht unabhängig voneinander sind.
* TODO: Erstellung von Diagrammen/Charts
* Die Verwendung mehrerer Banken ist nicht möglich.



## Links

- https://plaintextaccounting.org/
- https://hledger.org/import-csv.html
- https://hledger.org/cookbook.html
- https://hledger.org/budgeting.html
- https://hledger.org/accounting.html