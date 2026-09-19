import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM



# ==========================================
# 1. KEY GENERATION (CSPRNG - Section 2.8)
# ==========================================
print("Generating RSA Keypairs for Alice and Bob...")

# Generates cryptographically secure keys using system entropy
alice_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
alice_public_key = alice_private_key.public_key()

bob_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
bob_public_key = bob_private_key.public_key()

print("Keys Generated Successfully!\n")




# ==========================================
# 2. ALICE SENDS MESSAGE (Section 2.7: Sign-then-Encrypt via Hybrid Cryptography)
# ==========================================
message = b"Confidential Protocol Building Blocks Data: Launch Code 9982"
print(f"Original Message: {message.decode()}")

# STEP A: Alice signs the message with HER PRIVATE KEY (Section 2.6)
# Under the hood, RSA-PSS hashes the message with SHA-256 before signing (Section 2.4)
signature = alice_private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)
print(f"👀 INSIDE LOOK -> Raw Signature (First 30 bytes): {signature[:30].hex()}...")
print(f" Digital Signature Generated (Length: {len(signature)} bytes)")

# Combine original message + signature into a single package
payload = message + b"||SIGNATURE_SEP||" + signature

# STEP B: Generate temporary AES-256 Symmetric Key (Section 2.2)
aes_key = AESGCM.generate_key(bit_length=256)
print(f"👀 INSIDE LOOK -> Raw 32-byte AES Key: {aes_key.hex()}")

aesgcm = AESGCM(aes_key)
nonce = os.urandom(12) # Random initialization vector

# Encrypt the large payload using AES-GCM
encrypted_payload = aesgcm.encrypt(nonce, payload, None)
print(f"👀 INSIDE LOOK -> AES Encrypted Payload (Ciphertext): {encrypted_payload[:40].hex()}...")

# STEP C: Encrypt ONLY the 32-byte AES Key using BOB'S RSA PUBLIC KEY (Section 2.5)
encrypted_aes_key = bob_public_key.encrypt(
    aes_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print(f"👀 INSIDE LOOK -> RSA Encrypted AES Key: {encrypted_aes_key[:40].hex()}...\n")
print("🔒 Encrypted Payload (AES-256) & Key (RSA-2048) Ready for Transmission!\n")





# ==========================================
# 3. BOB RECEIVES & PROCESSES (Section 2.7) + MALLORY ATTACKS!
# ==========================================
print("Bob received the encrypted package. Processing...")

# STEP A: Bob decrypts AES key using HIS RSA PRIVATE KEY
decrypted_aes_key = bob_private_key.decrypt(
    encrypted_aes_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# STEP B: Bob decrypts payload using recovered AES Key
bob_aesgcm = AESGCM(decrypted_aes_key)
decrypted_payload = bob_aesgcm.decrypt(nonce, encrypted_payload, None)

received_message, received_signature = decrypted_payload.split(b"||SIGNATURE_SEP||")
print(f"Decrypted Message: {received_message.decode()}")

# MALLORY TAMPERING SIMULATION
print("MALLORY INTERCEPTS THE DECRYPTED MESSAGE AND ALERTS IT!")
tampered_message = received_message + b" [HACKED BY MALLORY]"
print(f"Fake Message Bob is trying to verify: {tampered_message.decode()}\n")

# STEP C: Bob verifies signature using ALICE'S PUBLIC KEY
try:
    alice_public_key.verify(
        received_signature,
        tampered_message,    # <---- Testing the tampered message here instead of received_message
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("VERIFICATION SUCCESS: Signature is authentic! Message came from Alice and was not tampered with.")
except Exception as e:
    print(f"VERIFICATION FAILED: {type(e).__name__}!")
    print("❌ The hash of the tampered message did not match the signature. Tampering detected and stopped!")