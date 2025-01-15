import struct
import xxtea

# Generic key identified from firmware
raw_key_generic = [0x91BD7A0A, 0xA75440A9, 0xBBD49D6C, 0xE0DCC0E3]

def vectkey_to_bytes(key_vect):
    joined = [k.to_bytes(4, 'little', signed=False) for k in key_vect]
    return b''.join(joined)

def hex_dump(data, start_address=0):
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        hex_part = f"{hex_part:<48}"
        print(f"{start_address + i:08x}: {hex_part} | {ascii_part}")

# Lunii device parameters
# YOUR SERIAL NUMBER
SNU = "0012345678912345" 
# YOUR VERSION
VERSION_MAJOR = 2
# YOUR MINOR VERSION
VERSION_MINOR = 19

def create_blocks():
    # First block (unencrypted) - exactly 256 bytes
    block1 = bytearray(256)  # Create block initialized with zeros

    # Block 1 structure
    block1[0] = 0x03
    block1[1] = 0x00
    block1[2:6] = bytes([0xff, 0xff, 0xff, 0xff])
    block1[6:8] = bytes([0x02, 0x00])
    block1[8:10] = bytes([VERSION_MINOR, 0x00])
    block1[10:17] = bytes.fromhex(SNU[:14])
    block1[17] = 0x00
    block1[18:31] = bytes.fromhex("830441A34E5350454349414C")  # Static "AENSPECIAL"
    block1[31] = 0x00

    # Second block (to encrypt) - ensure multiple of 4 bytes
    block2 = bytearray(260)  # Slightly larger than 256 to be safe

    # Block 2 data
    device_id = SNU[8:14]
    block2[0:6] = bytes.fromhex(device_id)
    block2[6:8] = bytes.fromhex("0007")
    block2[8:10] = struct.pack('<H', 0x0026)
    block2[10:15] = bytes.fromhex("3EF0112233")

    return block1, block2

# Create blocks
block1, block2 = create_blocks()

# Encrypt second block
lunii_generic_key = vectkey_to_bytes(raw_key_generic)

# Prepare block2 for encryption 
data_to_encrypt = bytes(block2)
if len(data_to_encrypt) < 8:
    # Add padding if needed to reach minimum 8 bytes
    data_to_encrypt += bytes([0] * (8 - len(data_to_encrypt)))

# Ensure length is multiple of 4
while len(data_to_encrypt) % 4 != 0:
    data_to_encrypt += bytes([0])

encrypted_block2 = xxtea.encrypt(data_to_encrypt, lunii_generic_key, padding=False)

# Combine blocks, ensuring second block is exactly 256 bytes
full_md = bytes(block1) + encrypted_block2[:256]

# Save file
with open('new.md', 'wb') as f:
    f.write(full_md)

print("MD file generated successfully!")
print("\nFirst block (unencrypted):")
hex_dump(block1)
print("\nSecond block (encrypted):")
hex_dump(encrypted_block2[:256], 256)

print(f"\nTotal file size: {len(full_md)} bytes")

# Additional checks
print(f"Block1 size: {len(block1)} bytes")
print(f"Data to encrypt size: {len(data_to_encrypt)} bytes") 
print(f"Encrypted block2 size: {len(encrypted_block2)} bytes")
