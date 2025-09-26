#!/usr/bin/env python3

#
# cloudflare.py
# Update Cloudflare DNS record with public IP.
#

import requests

# === CONFIG ===
API_TOKEN = "AlR_wgKeMQfUYMkqhOCuNwABF-3KT1bTqqAdKVs7"
ZONE_ID = "89d2765075c816eda36ad63f96ae70ff"
RECORD_NAME = "barrysbitters.com"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Get DNS record
url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
response = requests.get(url, headers=HEADERS)
response.raise_for_status()

records = response.json()["result"]
record = next((r for r in records if r["name"] == RECORD_NAME), None)
if not record:
    raise ValueError("DNS record not found!")

record_id = record["id"]

# Get current public IP address
current_ip = requests.get("https://api.ipify.org").text

# Update the DNS record
if record["content"] != current_ip:
    update_url = f"{url}/{record_id}"
    data = {"type": "A", "name": RECORD_NAME, "content": current_ip, "ttl": 1, "proxied": False}
    r = requests.put(update_url, headers=HEADERS, json=data)
    r.raise_for_status()
    print(f"Updated {RECORD_NAME} to {current_ip}")
else:
    print(f"No update needed, IP is still {current_ip}")
