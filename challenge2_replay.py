import os
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

print("CHALLENGE 2: Replay Attack Prevention (Timestamps)\n")

aes_key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(aes_key)
nonce = os.urandom(12)

# ==========================================
# 1. ALICE SENDS MESSAGE WITH TIMESTAMP
# ==========================================
message = b"TRANSFER $500 TO MALLORY"

# Add the message to payload along with current time
current_time = str(int(time.time())).encode()
payload = current_time + b"||" + message

print(f"Alice prepares payload: {payload.decode()}")
encrypted_payload = aesgcm.encrypt(nonce, payload, None)
print("Message Encrypted & Sent Over Network!\n")

# ==========================================
# 2. BOB RECEIVES IMMEDIATELY (NORMAL FLOW)
# ==========================================
print("Bob receives the message immediately...")
decrypted_payload = aesgcm.decrypt(nonce, encrypted_payload, None)
received_time, received_message = decrypted_payload.split(b"||")

time_difference = int(time.time()) - int(received_time)
print(f"Time since message was created: {time_difference} seconds")

# Bob's Condition: Message should not be old than 5 seconds
if time_difference <= 5:
    print(f"SUCCESS: Message accepted! Action: '{received_message.decode()}'\n")
else:
    print("REJECTED: Message too old!\n")

# ==========================================
# 3. MALLORY PERFORMS REPLAY ATTACK
# ==========================================
print("Mallory secretly recorded the encrypted packet.")
print("Mallory waits for 6 seconds to trick the system (Replay Attack)...")
time.sleep(6) # Pauses the code for 6 secs

print("\nMallory resends the EXACT SAME encrypted packet to Bob!")

# ==========================================
# 4. BOB RECEIVES MALLORY'S REPLAYED MESSAGE
# ==========================================
print("Bob receives a message...")
# Decryption will work because the packet is perfectly valid and unaltered
decrypted_replayed = aesgcm.decrypt(nonce, encrypted_payload, None)
replayed_time, replayed_message = decrypted_replayed.split(b"||")

replayed_time_difference = int(time.time()) - int(replayed_time)
print(f"Time since message was created: {replayed_time_difference} seconds")

if replayed_time_difference <= 5:
    print(f"SUCCESS: Message accepted! Action: '{replayed_message.decode()}'")
else:
    print(f"BLOCKED! Replay Attack Detected. Timestamp shows message is {replayed_time_difference} seconds old. Action ignored!")