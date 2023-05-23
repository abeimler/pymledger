#!/bin/bash

echo "host:         ${HLEDGER_HOST}"
echo "port:         ${HLEDGER_PORT}"
echo "base url:     ${HLEDGER_BASE_URL}"
echo "file url:     ${HLEDGER_FILE_URL}"
echo "input file:   ${HLEDGER_JOURNAL_FILE}"
echo "debug level:  ${HLEDGER_DEBUG}"
echo "rules file:   ${HLEDGER_RULES_FILE}"
echo "capabilities: ${HLEDGER_CAPABILITIES}"
echo "extra_args:   ${HLEDGER_ARGS}"
echo "---------------------------------------------------------------"

exec hledger-web \
     --serve \
     --host=$HLEDGER_HOST \
     --port=$HLEDGER_PORT \
     --file="$HLEDGER_JOURNAL_FILE" \
     --debug=$HLEDGER_DEBUG \
     --base-url=$HLEDGER_BASE_URL \
     --file-url=$HLEDGER_FILE_URL \
     --rules-file="$HLEDGER_RULES_FILE" \
     --capabilities=$HLEDGER_CAPABILITIES \
     ${HLEDGER_ARGS:="$@"}