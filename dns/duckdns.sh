#!/bin/bash

#
# duckdns.sh
# DuckDNS public IP updater
#

DOMAINS=("barrysbitters", "barrysbitters-pi")
TOKEN="8093db05-7182-4f87-b2f8-6d5475dcf5c5"

# Send update request
for DOMAIN in "${DOMAINS[@]}"; do
    curl -s "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=" >/dev/null
done

