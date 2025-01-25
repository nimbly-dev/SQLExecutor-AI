#!/bin/bash

# Check if two parameters are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <type_of_env> <version>"
  exit 1
fi

# Get the parameters
TYPE_OF_ENV=$1
VERSION=$2

# Generate a UUID
UUID=$(uuidgen)

# Combine the parameters and UUID to form the key
GENERATED_KEY="${TYPE_OF_ENV}_${VERSION}_${UUID}"

# Output the key
echo "Generated Key: $GENERATED_KEY"
