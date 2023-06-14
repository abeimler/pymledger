# hledger-rules

This is a command-line interface (CLI) Python script allows you to generate ledger rules and journals using YAML and CSV files. The script provides various commands and options to perform different tasks related to [hledger](https://github.com/simonmichael/hledger).

## Installation

1. Clone the repository or download the script file.
2. Make sure you have Python installed on your system (version 3.6 or later).
3. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

## Usage

The script provides the following commands and options:


### Generate Rules

#### `gen-rules`

Generate hledger rules files from the configuration.

Usage:
```
hledger-rules [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-rules [<year>] [--verbose]
```

- `<year>`: Optional parameter to generate rules for a specific year. If not provided, rules will be generated for the current year.
- `--output-dir=OUTPUT_DIR`: Optional flag to specify the output directory for the generated rules files.
- `--templates-dir=TEMPLATES_DIR`: Optional flag to specify the templates directory containing hledger and rules templates.

This command generates hledger rules files based on the provided configuration. If a specific year is specified, rules will be generated for that year.
The generated rules files will be saved in the output directory. If no output directory is specified, the files will be saved in the current directory.
Make sure to have a valid configuration file (`config.yml`) containing the necessary rules and settings before running this command.

Note: The `gen-rules` command assumes that the necessary templates are available in the templates directory. Ensure that the templates are properly configured and accessible for the script to generate accurate rules files.

#### Example

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
  - if: PP.[0-9]+.PP.*PayPal
    description: PayPal %verwendungszweck
    account: Expenses:unknown:PayPal
  - if: KARTENZAHLUNG
    description: Kartenzahlung %verwendungszweck 
    account: Expenses:unknown:%beguenstigter_zahlungspflichtiger
  # Bank
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
  # Salery
  - if: LOHN.*GEHALT
    account1: Assets:Bank:Checking                                                                                               
    account2: Income:Salary  
    income: true
  # Rent
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

**common.csv.rules**:

```hledger
if Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
AMZN Mktp DE.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND'
    description %beguenstigter_zahlungspflichtiger | Amazon %verwendungszweck
    account1    Expenses:unknown:Amazon                                         


if PP.1234.PP.*, Ihr Einkauf bei.*PayPal'
PP.1234.PP.*, Ihr Einkauf bei.*PAYPAL'
PP.1234.PP.*PayPal
PP.1234.PP.*PAYPAL
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


### Cleaup input files (.csv files)

#### `clean-up-csv`

Clean up a CSV file for input.

Usage:
```bash
hledger-rules [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] clean-up-csv <year> [--input-csv-delimiter=DELIMITER] [<month>] [--verbose]
```

- `year`: The year associated with the CSV file.
- `<month>`: Optional parameter to specify the month associated with the CSV file.


##### Example

```bash
hledger-rules -c config.yml clean-up-csv 2023 1
```

**input/2023/2023-01/2023-01.bank.csv**:
```csv
Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info
DE71234567891234567891,31.01.23,31.01.23,FOLGELASTSCHRIFT,Netflix Monthly Subscription ,123,asdfasdfasdf1,qwertz1,asdf1,,,NETFLIX SERVICES GERMANY GMBH,123123123,456456456,"-12,99",EUR,Umsatz gebucht
DE1,30.01.23,30.01.23,LOHN  GEHALT,LOHN / GEHALT ,124,asdfasdfasdf2,qwertz2,asdf2,,,Arbeit GmbH,123123124,456456457,2100,EUR,Umsatz gebucht
DE2,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-27 Debitk.2 2025-12 ,125,asdfasdfasdf3,qwertz3,asdf3,,,DB AUTOMAT,123123125,456456458,-10,EUR,Umsatz gebucht
DE3,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-27 Debitk.2 2025-12 ,126,asdfasdfasdf4,qwertz4,asdf4,,,SCHLOSS BURGER GMBH,123123126,456456459,-9,EUR,Umsatz gebucht
DE4,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-28 Debitk.2 2025-12 ,127,asdfasdfasdf5,qwertz5,asdf5,,,LIDL DIENSTLEISTUNG GMBH UND CO KG,123123127,456456460,"-30,99",EUR,Umsatz gebucht
DE5,30.01.23,30.01.23,FOLGELASTSCHRIFT,"123456789951 PP.1234.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com ",128,asdfasdfasdf6,qwertz6,asdf6,,,PayPal Europe S.a.r.l. et Cie S.C.A,123123128,456456461,"-19,99",EUR,Umsatz gebucht
```

**source/2023/2023-01/csv/2023-01.bank.csv**:
```csv
Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info,code,payee
**********************,31.01.23,31.01.23,FOLGELASTSCHRIFT,Netflix Monthly Subscription,***,*************,qwertz1,*****,,,NETFLIX SERVICES GERMANY GMBH,*********,*********,"-12,99",EUR,Umsatz gebucht,qwertz1,NETFLIX SERVICES GERMANY GMBH                                       
***,30.01.23,30.01.23,LOHN GEHALT,LOHN / GEHALT,***,*************,qwertz2,*****,,,Arbeit GmbH,*********,*********,2100,EUR,Umsatz gebucht,qwertz2,Arbeit GmbH
***,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-27 Debitk.2 2025-12,***,*************,qwertz3,*****,,,DB AUTOMAT,*********,*********,-10,EUR,Umsatz gebucht,qwertz3,DB AUTOMAT
***,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-27 Debitk.2 2025-12,***,*************,qwertz4,*****,,,SCHLOSS BURGER GMBH,*********,*********,-9,EUR,Umsatz gebucht,qwertz4,SCHLOSS BURGER GMBH
***,30.01.23,30.01.23,KARTENZAHLUNG,2023-01-28 Debitk.2 2025-12,***,*************,qwertz5,*****,,,LIDL DIENSTLEISTUNG GMBH UND CO KG,*********,*********,"-30,99",EUR,Umsatz gebucht,qwertz5,LIDL DIENSTLEISTUNG GMBH UND CO KG
***,30.01.23,30.01.23,FOLGELASTSCHRIFT,"123456789951 PP.1234.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com",***,*************,qwertz6,*****,,,PayPal Europe S.a.r.l. et Cie S.C.A,*********,*********,"-19,99",EUR,Umsatz gebucht,qwertz6,PayPal Europe S.a.r.l. et Cie S.C.A
```

### Generate Journals

#### `gen-year`/`gen-month`

Generate source, hledger rules, and journals for a specific month of a year or entire year.

Usage:
```bash
hledger-rules [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-year <year> [--all-months] [--strict] [--verbose]

hledger-rules [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-month <year> <month> [--strict] [--verbose]
```

- `year`: The year for which you want to generate the journals.
- `month`: The month for which you want to generate the journals.
- `--all-months`: Optional flag to generate source files for all months of the year.
- `--strict`: Optional flag to use hledger with strict option.


##### Example

```bash
hledger-rules -c config.yml gen-year 2023
```

#### `gen-all`

Generate source, hledger rules, and journals for multiple years.

Usage:
```bash
hledger-rules [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-all [--strict] [--verbose] <years>...
```

- `<years>`: One or more years for which you want to generate the journals.
- `--strict`: Optional flag to use hledger with strict option.

##### Example

```bash
hledger-rules -c configs/2022.config.yml gen-year 2022
hledger-rules -c config.yml gen-year 2023
hledger-rules -c config.yml gen-all 2022 2023
```


### Misc

#### `gen-all-forecast`

Generate source, hledger rules, and journals for multiple years, including forecasted data.

Usage:
```bash
hledger-rules [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-all-forecast [--verbose] <years>...
```

- `<years>`: One or more years for which you want to generate the journals with forecasted data.
- `--verbose`: Optional flag to print more details.

##### Example

```bash
hledger-rules -c configs/2022.config.yml gen-year 2022
hledger-rules -c config.yml gen-year 2023
hledger-rules -c config.yml gen-all 2022 2023
hledger-rules -c config.yml gen-all-forecast 2023
```

#### `beancount`

Convert hledger journals to the Beancount format.

Usage:
```bash
hledger-rules [--hledger-path=HLEDGER] [--ledger2beancount-path=LEDGER2BEANCOUNT] [-c config.yml] beancount -f JOURNAL [-o OUTPUT] [--verbose]
```

- `JOURNAL`: The input .journal file to convert to Beancount format.
- `-o OUTPUT`: Optional parameter to specify the output file name for the Beancount conversion.


##### Example

```bash
hledger-rules -c config.yml beancount -f all.hledger -o journals/all.beancount
```


#### `accounts`

Print accounts from the configuration file.

Usage:
```bash
hledger-rules [-c config.yml] accounts [--verbose]
```

#### `beancount-options`

Print Beancount options for Fava.

Usage:
```bash
hledger-rules [-c config.yml] beancount-options [--verbose]
```

#### `budget`

Print monthly budget balance.

Usage:
```bash
hledger-rules [-c config.yml] budget [--balance] [--verbose]
```

- `--balance`: Optional flag to only print the balance from the monthly budget.

##### Example

```bash
hledger-rules -c config.yml budget
```

```bash
 Forecast                                                                       ||        monthly 
================================================================================++================
 Budget                                                                         ||                
--------------------------------------------------------------------------------++----------------
 Assets:Bank:Budget:Telekommunikation                                           ||     105.00 EUR 
 Assets:Bank:Budget:Kleidung                                                    ||      20.00 EUR 
 Assets:Bank:Budget:Lebensmittel                                                ||     250.00 EUR 
 Assets:Bank:Budget:Versicherungen                                              ||       0.83 EUR 
 Assets:Bank:Budget:Fahrgeld                                                    ||      20.00 EUR 
 Assets:Bank:Budget:Abo:DTicket                                                 ||      49.00 EUR 
 Assets:Bank:Budget:Wohnen                                                      ||     550.00 EUR 
 Assets:Bank:Budget:Wunschliste                                                 ||     100.00 EUR 
 Assets:Bank:Budget:Abo:Multimedia                                              ||      45.00 EUR 
 Assets:Bank:Budget:Haushalt                                                    ||      50.00 EUR 
 Assets:Bank:Budget:Sonstiges                                                   ||      25.00 EUR 
 Assets:Bank:Budget:Abo:Amazon:Prime                                            ||       7.50 EUR 
--------------------------------------------------------------------------------++----------------
                                                                                ||    1222.33 EUR 
================================================================================++================
 Income                                                                         ||                
--------------------------------------------------------------------------------++----------------
 Income (Budget)                                                                ||    2100.00 EUR 
--------------------------------------------------------------------------------++----------------
                                                                                ||    2100.00 EUR 
================================================================================++================
 Net:                                                                           ||     877.67 EUR
```

### Options

The script also provides the following options:

- `--hledger-path=HLEDGER`: Path to the hledger executable binary. (Default: ./hledger)
- `--ledger2beancount-path=LEDGER2BEANCOUNT`: Path to the ledger2beancount executable binary. (Default: ./ledger2beancount)
- `-c config.yml`: Path to the .yml config file with rules and settings. (Default: config.yml)
- `--output-dir=OUTPUT_DIR`: Output directory for generated files.
- `--templates-dir=TEMPLATES_DIR`: Templates directory containing hledger and rules templates.
- `--source-account=ACCOUNT`: Account name for the source in the Sankey Diagram.
- `-i INPUT`: Input .csv file for clean-up operation or as input for the Senkey-Diagram.
- `-o OUTPUT`: Output .csv file for clean-up operation or output filename for the Sankey Diagram or Beancount conversion.
- `-f JOURNAL`: Input .journal file for the Beancount conversion.
- `--input-csv-delimiter=DELIMITER`: Delimiter used in the input .csv file. (Default: ,)

## General Options

- `-h, --help`: Show help information.
- `-v, --version`: Show version information.
- `-V, --verbose`: Print more details.
- `-s, --strict`: Use hledger with strict option.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please create an issue or submit a pull request on the GitHub repository.

## License

This script is licensed under the [MIT License](LICENSE).