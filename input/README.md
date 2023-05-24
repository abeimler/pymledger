# CSV Dateien von der Bank

Original `.csv`-Dateien von der Bank (Monatliche exports) im [CAMT-CSV Format](https://de.wikipedia.org/wiki/Camt-Format).

## CAMT-CSV Format

Folge Header muss die CSV beinhalten:
```csv
Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info
```

## Ordner Struktur

Folgende Struktur sollten die Ordner haben in [input/](../input/):

```
├── input/
│   ├── 2023-01/
│   │   └── 2023-01.bank.csv
│   └── 2023-02/
│   │   └── 2023-02.bank.csv
│   └── 2023-03/
```

Mit "YYYY-MM"-Format für den Ordner und "YYYY-MM.bank.csv" für die CAMT-CSV Datei.

### input/ -> source/

Aus den `input/**/*.bank.csv`'s werden die CSV-Quelle-Dateien für die Journals, "gesäubert" und in [source/](../source/) abgelegt.