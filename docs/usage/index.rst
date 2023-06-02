.. _usage:

Verwendung
----------

Um pYMLedger nutzen zu können, müssen Sie zunächst CSV-Exporte von Ihrem
Online-Banking erstellen, um Ihre Finanzdaten zu verwalten. Sie können entweder die originalen CSV-Dateien verwenden, die von Ihrer Bank
exportiert wurden, oder die mitgelieferten Beispieldateien im Verzeichnis `examples/input <https://github.com/abeimler/pymledger/tree/main/examples/input/2023>`_ zum Testen nutzen.

Eingabe und Quellen
~~~~~~~~~~~~~~~~~~~

Bitte stellen Sie sicher, dass jeder Kontoauszug (CAMT-CSV-Export) nur einen Monat abdeckt.

CSV-Dateien von der Bank
^^^^^^^^^^^^^^^^^^^^^^^^

Die CSV-Dateien sollten im CAMT-CSV-Format vorliegen und die folgenden
Spalten enthalten, wobei die Spalten durch Kommas getrennt sein müssen:

**(Die Spalten in der CSV-Datei MÜSSEN durch (``,``) Kommas getrennt sein)**

*Die CSV-Datei sollte die folgenden Spalten enthalten:*

.. code:: csv

   Auftragskonto,Buchungstag,Valutadatum,Buchungstext,Verwendungszweck,Glaeubiger ID,Mandatsreferenz,Kundenreferenz (End-to-End),Sammlerreferenz,Lastschrift Ursprungsbetrag,Auslagenersatz Ruecklastschrift,Beguenstigter/Zahlungspflichtiger,Kontonummer/IBAN,BIC (SWIFT-Code),Betrag,Waehrung,Info


.. _folder_struct:

Verzeichnisstruktur
^^^^^^^^^^^^^^^^^^^

Stellen Sie sicher, dass das Eingabe-Verzeichnis (``input/``) folgende Struktur aufweist:

::

   ├── input/
   │   ├── 2023/
   │   │   ├── 2023-01/
   │   │   │   └── 2023-01.bank.csv
   │   │   ├── 2023-02/
   │   │   │   └── 2023-02.bank.csv
   │   │   └── 2023-03/

*Verwenden Sie das Format “YYYY” für das Jahr, “YYYY-MM” für den Ordner
(pro Monat) und “YYYY-MM.bank.csv” für die CAMT-CSV-Datei.*

CSV Dateien bereinigen
^^^^^^^^^^^^^^^^^^^^^^

Bevor wir aus den CSV-Dateien ``rules`` und ``journals`` generieren,
sollten wir diese erstmal etwas “säuber”, mit den Befehl:

.. code:: bash

   python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml clean-up-csv 2023

*Die CSV-Dateien aus den* ``input/2023`` *werden etwas “gesäubert” und in*
`source/2023/ <https://github.com/abeimler/pymledger/tree/main/source/2023>`_ *gespeichert.*

Lastschrift, Überweisungen, etc. - (allgemeine) Regeln
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lassen Sie uns nun die CSV-Dateien im Verzeichnis
`source/2023/ <https://github.com/abeimler/pymledger/tree/main/source/2023>`_ betrachten. 
Dort sollten alle monatlichen Kontoauszüge unserer Bank zu finden sein. 
Wir können uns zunächst auf die **Ausgaben** (``Expenses``) konzentrieren und Zeile für
Zeile durchgehen, um für jeden Eintrag/Ausgabe eine ``rule`` zu erstellen.

Beispiel: Wohnen
^^^^^^^^^^^^^^^^

Betrachten wir beispielsweise die CSV-Datei für Januar 2023. Darin befindet sich eine Zeile mit dem Verwendungszweck “Wohnen” 
(wichtig sind hier nur die Spalten **“Verwendungszweck”** und **“Begünstigter/Zahlungspflichtiger”**).

`source/2023/2023-01/csv/2023-01.bank.csv <https://github.com/abeimler/pymledger/blob/main/source/2023/2023-01/csv/2023-01.bank.csv>`_

.. code:: csv

   ****,02.01.23,02.01.23,DAUERAUFTRAG,1234/4568.00001.12,***,,,****,,,Wohnen GmbH,,,"-499,2",EUR,Umsatz gebucht,2023-01.0031,Wohnen GmbH


-  Verwendungszweck: ``1234/4568.00001.12``
-  Beguenstigter/Zahlungspflichtiger: ``Wohnen GmbH``

Für diesen Eintrag könnten wir ganz einfach eine ``rule`` in unserer `config.yml <https://github.com/abeimler/pymledger/blob/main/config.yml>`_ anlegen:

**config.yml**

.. code:: yml

   common_rules:
     # Wohung/Miete 
     - if:
         - 1234/4567.00001.12.*Wohnen GmbH
       description: Miete
       account: Expenses:Wohnen:Miete

*Regeln für Lastschrift, Überweisungen usw. befinden sich im Block ``common_rules``.*

.. _create_rules:

Erstellung der Regeln
^^^^^^^^^^^^^^^^^^^^^

Nachdem wir die Regeln in unsere ``config.yml`` eingetragen haben,
können wir die `hledger rules <https://hledger.org/1.29/hledger.html#csv-rules-cheatsheet>`_
mit dem folgenden Befehl erstellen:

.. code:: bash

   python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023

*Die Regeln werden im Verzeichnis* `journals/2023/rules/ <https://github.com/abeimler/pymledger/blob/main/journals/2023/rules/>`_ *gespeichert.*

**common.csv.rules**

.. code:: journal

   if 1234/4568.00001.12.*Wohnen GmbH
       description %beguenstigter_zahlungspflichtiger | Miete
       account1    Expenses:Wohnen:Miete      

Journals
~~~~~~~~

Nachdem alle möglichen ``rules`` in unsere ``config.yml`` eingetragen
wurden (und die Regeln erstellt wurden), können wir auch die
``journal``\ s erstellen lassen:

.. code:: bash

   python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023
   python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023

*Die erstellten Journals werden im Verzeichnis* `journals/2023/ <https://github.com/abeimler/pymledger/tree/main/journals/2023>`_ *gespeichert.*

`journals/2023/2023-01/2023-01.bank.hledger <https://github.com/abeimler/pymledger/blob/main/journals/2023/2023-01/2023-01.bank.hledger>`_

.. code:: hledger

   2023-01-02=2023-01-02 * (2023-01.0030) Wohnen GmbH | Miete  ; type:DAUERAUFTRAG, payee:Wohnen GmbH
       Expenses:Wohnen:Miete       EUR499,20
       Assets:Bank:Checking       EUR-499,20

Budgetierung
~~~~~~~~~~~~

Wenn alle Regeln für die Ausgaben eingetragen wurde, geht weiter zum Budgetieren:

.. toctree::

   budget


Spezielle Regeln
~~~~~~~~~~~~~~~~

Um komplexe Regeln für Amazon-Bestellungen und PayPal-Käufe zu verwenden, können wir
vordefinierte Regeln generieren lassen.

**config.yml**

.. code:: yml

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


.. toctree::

   special_rules/index


Mehr
~~~~

.. toctree::

   more
