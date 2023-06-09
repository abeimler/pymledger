.. _more:

Überprüfung (Checking)
=======================

Der ``account`` ``Assets:Bank:Checking`` sollte den Betrag auf deinem Bankkonto oder die Einnahmen/Ausgaben aus der (input) .csv-Datei wiederspiegeln.

Möglicherweise musst du die Eröffnungsbilanz in der Datei `all.hledger` anpassen:

.. code-block:: hledger
   :linenos:

   2023/01/01 * opening balances   ; opening:
       Assets:Bank:Checking                                                  2179,78 EUR
       Assets:Saving:Cash                                                    2000,00 EUR  
       Assets:Cash                                                             50,50 EUR  
       Equity:OpeningClosingBalances


Abgleich (reconcile)
--------------------

Um sicherzustellen, dass dein Bankkonto mit der tatsächlichen Bank übereinstimmt, kannst du einige Abgleichseinträge erstellen. 
Dafür kannst du für jeden Monat eine Datei mit dem Format `YYYY-MM.reconcile.yml` anlegen. Hier ist ein Beispiel für den Januar 2023:

**source/2023/2023-01/2023-01.reconcile.yml**

.. code-block:: yaml
   :linenos:

   - day: 15
     amount: 1364.65


Weitere checks
--------------

Versuche dein Budget nicht zu überstrapazieren. 
Das Hauptziel des Programms ist es, dein Budget sowie Ein- und Ausgaben im Überblick zu behalten. 
Dein ``Assets:Bank:Checking`` sollte immer die Transaktionen deines realen Bankkontos wiederspiegeln 
(das sollte einfach sein, wenn du die Eingabedatei im CSV-Format von der Bank verwendest).

Das Budget (``Assets:Bank:Budget``) sollte immer niedriger sein als der Betrag in ``Assets:Bank:Checking``. 
Um zu sehen, wie viel du noch budgetieren kannst, kannst du den Kontostand des ``Assets:Bank:Unbudget``-Kontos überprüfen 
(dieses Konto wird automatisch erstellt).

Halte ausschau auf die Fallback-Konten ``Expenses:unknown``. 
Hier landen Einträge, denen noch kein spezifisches Konto zugeordnet wurde 
(z.B. ``Expenses:unknown:PayPal``, ``Expenses:unknown:Amazon``, ``Expenses:unknown:UnbekanntesGeschaeft``, ...).

.. code-block:: bash

   hledger -f all.hledger -s --auto check
   hledger -f all.hledger reg --auto Expenses:unknown


Bargeld
=======

Die Informationen zu den Bargeldtransaktionen findest du in der Datei ``YYYY-MM.cash.yml``. Hier ein Beispiel für eine Transaktion:

**source/2023/2023-01/2023-01.cash.yml**

.. code-block:: yaml
   :linenos:

   - day: 15
     amount: 21.84
     description: Einkaufen Rewe
     account: Expenses:Lebensmittel:Einkaufen:Rewe

Du kannst weitere Bargeldtransaktionen in der Datei hinzufügen, um deine Ausgaben in bar zu verfolgen.
