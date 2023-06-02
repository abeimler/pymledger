.. _quick_start:

Schnell-Start
-------------

Um mit dein `PTA <https://plaintextaccounting.org/>`_ schnell zu
beginnen, folgen Sie einfach diesen Schritten:

1. **Eingabe und Quellen:** Verwenden Sie CSV-Exporte (**Im** `CAMT-CSV Format <https://de.wikipedia.org/wiki/Camt-Format>`_) von Ihrem
   Online-Banking oder die mitgelieferten `Beispieldateien <https://github.com/abeimler/pymledger/tree/main/examples/input/>`_ für Testzwecke und speicher die
   .csv-Dateien in `input/ <https://github.com/abeimler/pymledger/tree/main/input/>`_, siehe :ref:`Verzeichnisstruktur <folder_struct>`.

2. **CSV-Dateien bereinigen:** Führen Sie den Befehl aus, um die
   CSV-Dateien zu bereinigen und in das Verzeichnis ``source`` zu
   speichern:

   .. code:: bash

      python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml clean-up-csv 2023

3. **Regeln erstellen:** Erstellen Sie Regeln für Lastschriften,
   Überweisungen usw. im Block ``common_rules`` in der Datei ``config.yml``, siehe :ref:`Verwendung <create_rules>`
   für mehr details.

4. **Regeln generieren:** Generieren Sie die Regeln mit dem folgenden
   Befehl:

   .. code:: bash

      python3 ./scripts/hledger-rules/hledger-rules.py -c config.yml gen-rules 2023

5. **Journale erstellen:** Erstellen Sie die Journale mit den erstellten
   Regeln:

   .. code:: bash

      python3 ./scripts/hledger-rules/hledger-rules.py --hledger-path=/usr/bin/hledger -c config.yml gen-year 2023

6. **Budgetierung:** Sobald alle Ausgabenregeln eingetragen sind, können
   Sie zur :ref:`Budgetierung <budget>` übergehen.

7. **Spezielle Regeln:** Wenn Sie komplexe Regeln für
   Amazon-Bestellungen und PayPal-Käufe haben, können Sie vordefinierte Regeln in die ``config.yml`` Datei eintragen. Weitere Informationen
   finden Sie in :ref:`Amazon <special_rules_amazon>` und :ref:`PayPal <special_rules_paypal>`.

Möchten Sie weitere Informationen und detaillierte Anweisungen? 
Lesen Sie :ref:`hier mehr <usage>`.