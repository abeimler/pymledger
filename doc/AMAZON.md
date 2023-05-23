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
paypal_rules:
  # Gaming
  - name:
      - Steam
      - STEAM
      - steampowered
    description: Steam
    account: Expenses:Hobbies:Gaming:Steam
```



