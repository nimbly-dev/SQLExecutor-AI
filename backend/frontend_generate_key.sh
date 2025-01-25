#!/bin/bash

# Check if two parameters are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <type_of_env> <version>"
  exit 1
fi

# Get the parameters
TYPE_OF_ENV=$1
VERSION=$2

# Generate a UUID-like string using /dev/urandom
RANDOM_UUID=$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 32 | head -n 1)
UUID="${RANDOM_UUID:0:8}-${RANDOM_UUID:8:4}-${RANDOM_UUID:12:4}-${RANDOM_UUID:16:4}-${RANDOM_UUID:20:12}"

# Combine the parameters and UUID to form the key
GENERATED_KEY="${TYPE_OF_ENV}_${VERSION}_${UUID}"

# Output the key
echo "Generated Key: $GENERATED_KEY"
