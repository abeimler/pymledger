.. _budget:

Budgetierung
~~~~~~~~~~~~

Standard-Budget
^^^^^^^^^^^^^^^

Es wäre sinnvoll, für Ausgaben (z.B. ``Expenses:Wohnen:Miete``) auch ein
Budget festzulegen:

**config.yml**

.. code:: yml

   monthly:
     # Standardbudget für den Monat
     budget:
       # Wohnung
       - account: Assets:Bank:Budget:Wohnen
         amount: 500.0
         comment: Miete

Transaktionen
^^^^^^^^^^^^^

Damit die Ausgaben (z.B. ``Expenses:Wohnen:Miete``) vom Budget (z.B.``Assets:Bank:Budget:Wohnen``) abgezogen werden, müssen wir eine
``transaction`` in unserer ``config.yml`` definieren:

**config.yml**

.. code:: yml

   transactions:
     # Wohnung
     - expense: Expenses:Wohnen
       asset: Assets:Bank:Budget:Wohnen

Einkommen
^^^^^^^^^

Schließlich müssen wir nur noch sicherstellen, dass unser Budget (z.B. ``Assets:Bank:Budget:Wohnen``) auch irgendwoher kommt, idealerweise vom
“Einkommen”. Dazu müssen wir nur eine Regel für das ``income`` in unserer ``config.yml`` definieren:

**config.yml**

.. code:: yml

   common_rules:
     # Lohn
     - if: LOHN.*GEHALT.*Arbeit GmbH
       description: Einkommen von Arbeit GmbH
       account1: Assets:Bank:Checking                                                                                               
       account2: Income:Salary  
       income: true

*(“Arbeit GmbH” ist hier nur ein Beispiel, schauen Sie einfach nach, wie es in Ihrem Kontoauszug (CSV) aussieht).*

**2023-01.bank.csv**

.. code:: csv

   ***,30.01.23,30.01.23,LOHN GEHALT,LOHN / GEHALT,***,,,****,,,Arbeit GmbH,,,2100,EUR,Umsatz gebucht,2023-01.0002,Arbeit GmbH

Monatliche Budgetierung
~~~~~~~~~~~~~~~~~~~~~~~

Für jeden Monat wird ein
`source/2023/2023-01/2023-01.budget.yaml <https://github.com/abeimler/pymledger/tree/main/source/2023/2023-01/2023-01.budget.yaml>`_
erstellt, basiert ``config.yml`` und `source/2023/2023-01/template.2023-01.budget.yaml <https://github.com/abeimler/pymledger/tree/main/source/2023/2023-01/template.2023-01.budget.yaml>`_.
Diese Datei wird einmal erstellt und kann dann (ähnlich wie ``2023-01.amazon.yaml`` und ``2023-01.paypal.yaml``) nach belieben
angepasst werden, abhänig von deiner Situation und des Monats.

Für jeden Monat wird eine Budgetdatei erstellt, die auf ``config.yml``
und dem entsprechenden Template basiert. Die Budgetdatei für Januar 2023 befindet sich unter
`source/2023/2023-01/2023-01.budget.yaml <https://github.com/abeimler/pymledger/tree/main/source/2023/2023-01/2023-01.budget.yaml>`_.
Du kannst diese Datei nach Belieben anpassen, ähnlich wie die Dateien ``2023-01.amazon.yaml`` und ``2023-01.paypal.yaml``, um sie an deine
individuelle Situation und den aktuellen Monat anzupassen.