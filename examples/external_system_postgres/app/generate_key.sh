#!/bin/bash

# === CONFIG ===
OUTPUT_FILE="dev.env"

# Prompt for secret
read -p "Enter the secret to encrypt: " SECRET

# === KEY AND IV GENERATION ===
# Generate AES-256 key and IV
ENCRYPTION_KEY=$(openssl rand -base64 32)  # 32 bytes for AES-256
ENCRYPTION_IV=$(openssl rand -base64 16)  # 16 bytes for IV

# === ENCRYPT SECRET ===
# Generate raw key and IV (Hexadecimal)
HEX_KEY=$(openssl rand -hex 32)  # 32 bytes = 256 bits
HEX_IV=$(openssl rand -hex 16)  # 16 bytes = 128 bits

# Encrypt the secret
ENC_SECRET=$(echo -n "$SECRET" | openssl enc -aes-256-cbc -base64 -K "$HEX_KEY" -iv "$HEX_IV" 2>/dev/null)

# === OUTPUT ENV FILE ===
if [ -z "$ENC_SECRET" ]; then
    echo "Encryption failed. Please check your OpenSSL command."
    exit 1
fi

echo "Appending values to $OUTPUT_FILE..."

cat <<EOL >> $OUTPUT_FILE
# Encryption Key and IV for Secret Encryption
ENCRYPTION_KEY=$ENCRYPTION_KEY
ENCRYPTION_IV=$ENCRYPTION_IV

# Encrypted Secret
ENCRYPTED_SECRET=$ENC_SECRET
EOL

echo "Encryption Key, IV, and Encrypted Secret appended to $OUTPUT_FILE"
