.. _special_rules_paypal:

PayPal
~~~~~~

Standardregel - allgemein
^^^^^^^^^^^^^^^^^^^^^^^^^

Um vorerst alle möglichen PayPal-Käufe zu kategorisieren, legen wir eine
Regel als Fallback fest:

**config.yml**

.. code:: yml

   common_rules:
     # Defaults/Fallbacks (first)
     - if: 
         - PP.6330.PP.*, Ihr Einkauf bei.*PayPal'
         - PP.6330.PP.*, Ihr Einkauf bei.*PAYPAL'
         - PP.6330.PP.*PayPal
         - PP.6330.PP.*PAYPAL
       description: PayPal %verwendungszweck
       account: Expenses:unknown:PayPal

*Damit werden alle PayPal-Käufe dem Konto* ``Expenses:unknown:PayPal``
*zugewiesen.*

Monatliche PayPal-Käufe
^^^^^^^^^^^^^^^^^^^^^^^

Um die PayPal-Regeln zu nutzen, müssen sie zuerst in der ``config.yml``
definiert werden:

**config.yml**

.. code:: yml

   paypal:
     # python format with ref and name, {ref}.*PP.6330.PP.*{name}, Ihr Einkauf bei.*PayPal
     if_format:
       - '{ref}.*PP.6330.PP.*{name}.*, Ihr Einkauf bei.*PayPal'
       - '{ref}.*PP.6330.PP.*{name}.*, Ihr Einkauf bei.*PAYPAL'
     payee: 'PayPal Europe S.a.r.l. et Cie S.C.A' 

Passen Sie die ``if_format`` entsprechend Ihrer Kontenauszüge an, um die
PayPal-Ausgaben zu identifizieren:

Beispiel
''''''''

**2023-01.bank.csv**

.. code:: csv

   ****,03.01.23,03.01.23,FOLGELASTSCHRIFT,"1234567893215 PP.6330.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com",***,,,****,,,PayPal Europe S.a.r.l. et Cie S.C.A,,,"-25,79",EUR,Umsatz gebucht,2023-01.0025,PayPal Europe S.a.r.l. et Cie S.C.A

Beachten Sie die Spalte “Verwendungszweck”: ``1234567893215 PP.6330.PP . www.steampowered.com, Ihr Einkauf bei www.steampowered.com``.

-  Referenz: ``1234567893215``
-  Suffix: ``PP.6330.PP``
-  Name: ``www.steampowered.com``

Daraus ergibt sich das ``if_format``:
``{ref}.*PP.6330.PP.*{name}, Ihr Einkauf bei.*``

.. _monatliche-paypal-kaeufe-1:

Monatliche PayPal-Käufe
^^^^^^^^^^^^^^^^^^^^^^^

Nachdem wir die Quellen für das Jahr 2023 erstellt haben, finden Sie im
Verzeichnis ``source/`` eine Vorlage für die PayPal-Käufe:
`source/2023/2023-01/template.2023-01.paypal.yaml <https://github.com/abeimler/pymledger/blob/main/examples/source/template.2023-01.paypal.yaml>`_

**source/2023/2023-01/template.2023-01.paypal.yaml**

.. code:: yml

   - account: Expenses:unknown:PayPal
     amount: -21.85
     payee: PayPal Europe S.a.r.l. et Cie S.C.A
     ref: '1234567893214'

Diese Vorlage können wir verwenden um die echten Käufe in
`source/2023/2023-01/2023-01.paypal.yaml <https://github.com/abeimler/pymledger/tree/main/source/2023/2023-01/2023-01.paypal.yaml>`_
einzutragen:

**2023-01.paypal.yaml**

.. code:: yml

   - account: Expenses:Lebensmittel:Essen:Pizza
     ref: '1234567893214'

*Wir können einfach* ``ref`` *(Referenz) verwenden, um einem
(Ausgaben-)Konto zuzuweisen.*

**2023-01.paypal.yaml**

.. code:: yml

   - account: Expenses:Hobbies:Gaming:Steam
     description: Steam (Gaming) 
     name: steampowered

Idealerweise ist der ``name`` aussagekräftiger, leider ist dieser nicht
immer vorhanden.

*Leider ist die* ``ref`` *(Referenz) nicht unter “PayPal” -> “Meine
Aktivitäten” zu finden. Du musst also genauer auf das Datum, den*
``name`` *(falls vorhanden) und den* ``amount`` *(Betrag) achten, um
festzustellen, was du gekauft hast und welchem* ``account`` *du es
zuweisen möchtest.*

**Die** ``template.paypal.yaml`` **ist nicht perfekt und es könnten Käufe
fehlen oder nicht aus den Kontenauszügen (CSV) erkannt werden.**

Allgemeine PayPal-Regeln
^^^^^^^^^^^^^^^^^^^^^^^^

Wenn wir wiederkehrende Ausgaben oder Regeln für PayPal haben, können
wir diese einfach in der ``config.yml`` festlegen:

**config.yml**

.. code:: yml

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