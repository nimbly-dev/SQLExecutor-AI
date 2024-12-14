#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 TENANT_ID"
  exit 1
fi

TENANT_ID="$1"

# Generate a SHA-256 hash from TENANT_ID
HASH_KEY=$(echo -n "$TENANT_ID" | sha256sum | awk '{print $1}')
echo "Generated 256-bit hash key for TENANT_ID '$TENANT_ID':"
echo "$HASH_KEY"
