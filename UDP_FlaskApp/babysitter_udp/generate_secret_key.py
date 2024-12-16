import secrets

# Generate a random secret key
secret_key = secrets.token_hex(16)  # You can adjust the length (16 bytes in this case)

# Print the generated key
print("Your secret key is:", secret_key)
