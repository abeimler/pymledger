# CSV Dateien von der Bank

Original `.csv`-Dateien von der Bank (Monatliche exports) im CAMT-CSV Format.

## Ordner Struktur

Folgende Struktur sollten die Ordner haben in [input/](input/):

```
├── input/
│   ├── 2023-01/
│   │   └── 2023-01.bank.csv
│   └── 2023-02/
│   │   └── 2023-02.bank.csv
│   └── 2023-03/
```

Mit "YYYY-MM"-Format für den Ordner und "YYYY-MM.bank.csv" für die CAMT-CSV Datei.

## git

Ich persönlich hab die input's aus den git ignored.

### input/ -> source/

Aus den `input/**/*.bank.csv`'s werden die Quelle Dateien für das Journals, "gesäubert" und in [source/](source/) abgelegt.