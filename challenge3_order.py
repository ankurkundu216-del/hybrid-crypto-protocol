import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

print("⚖️ CHALLENGE 3: Encrypt-then-Sign Architecture ⚖️\n")

# Setup Keys
alice_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
alice_public = alice_private.public_key()

aes_key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(aes_key)
nonce = os.urandom(12)

message = b"Initiate Protocol Alpha"

# ==========================================
# 1. ALICE: ENCRYPT FIRST, THEN SIGN
# ==========================================
# Step A: Encrypt the plaintext
ciphertext = aesgcm.encrypt(nonce, message, None)
print(f"1. Alice encrypted the message. Ciphertext: {ciphertext[:10].hex()}...")

# Step B: Sign CIPHERTEXT instead of Plaintext
signature = alice_private.sign(
    ciphertext,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256()
)
print("2. Alice signed the CIPHERTEXT (Not the plaintext).\n")

# ==========================================
# 2. BOB: VERIFY FIRST, THEN DECRYPT
# ==========================================
print("Bob receives the package (Signature + Ciphertext)...")

# Step A: Verify the Signatures first, Then Decrypt
try:
    alice_public.verify(
        signature,
        ciphertext,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    print("✅ 1. Signature Verified! Bob confirms Alice sent this exact ciphertext.")

    # Step B: Only if verification is successfull, time will be added to CPU decryption
    decrypted_message = aesgcm.decrypt(nonce, ciphertext, None)
    print(f"🔓 2. Decryption Successful! Message: '{decrypted_message.decode()}'")
    
except Exception as e:
    print(f"🚨 Verification failed! Intruder detected. Dropping packet without decrypting.")