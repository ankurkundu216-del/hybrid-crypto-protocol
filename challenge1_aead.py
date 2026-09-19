import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

print("🛡️ CHALLENGE 1: AES-GCM Ciphertext Tampering (AEAD) 🛡️\n")

# ==========================================
# 1. SETUP & ENCRYPTION
# ==========================================
# Generate 256-bit AES Key and 12-byte Nonce
aes_key = AESGCM.generate_key(bit_length=256)
nonce = os.urandom(12)
aesgcm = AESGCM(aes_key)

message = b"TOP SECRET: Attack at dawn!"
print(f"Original Plaintext : {message.decode()}")

# Encrypt the message
ciphertext = aesgcm.encrypt(nonce, message, None)
print(f"Ciphertext (Hex) : {ciphertext[:15].hex()}... (truncated)")


# ==========================================
# 2. MALLORY TAMPERS WITH THE CIPHERTEXT
# ==========================================
print("\n Malloc intercepts the ciphertext over the network...")
print("Mallory flips just ONE byte of the ciphertext to corrupt it!")

# Convert to bytearray so we can modify it
tampered_ciphertext = bytearray(ciphertext)
# Flipping the bits of the very first byte using XOR (^)
tampered_ciphertext[0] ^= 0xFF
tampered_ciphertext = bytes(tampered_ciphertext)

print(f"Tampered C-text : {tampered_ciphertext[:15].hex()}... (truncated)")


# ==========================================
# 3. BOB ATTEMPTS DECRYPTION
# ==========================================
print("\n Bob receives the data and tries to decrypt...")

print("\n--- Test A: Decrypting the Original Ciphertext ---")
try:
    decrypt_original = aesgcm.decrypt(nonce, ciphertext, None)
    print(f"SUCCESS: {decrypt_original.decode()}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}")

print("\n--- Test B: Decrypting the Tampered Ciphertext ---")
try:
    decrypted_tampered = aesgcm.decrypt(nonce, tampered_ciphertext, None)
    print(f"SUCCESS: {decrypted_tampered.decode()}")
except Exception as e:
    print(f"DECRYPTION BLOCKED! Error type: {type(e).__name__}")
    print("Reason: AES-GCM uses an 'Authentication Tag'. Tampering changed the math, so AES refused to even output the wrong text!")