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

# Lunii device parameters - replace with your own values
SNU = "XXXXXXXXXXXXXXXX"  # 16 characters serial number
VERSION_MAJOR = 2
VERSION_MINOR = 19

def create_blocks():
    # First block (unencrypted) - exactly 256 bytes
    block1 = bytearray([0] * 256)

    # Block 1 structure initialization
    block1[0] = 0x03
    block1[1] = 0x00
    block1[2:6] = bytes([0xff, 0xff, 0xff, 0xff])
    block1[6:8] = bytes([0x02, 0x00])
    block1[8:10] = bytes([VERSION_MINOR, 0x00])
    block1[10:17] = bytes.fromhex(SNU[:14])
    block1[17] = 0x00
    block1[18:31] = bytes.fromhex("830441A34E5350454349414C")  # Static identifier
    block1[31] = 0x00

    # Ensure exact block size of 256 bytes
    if len(block1) != 256:
        block1.extend([0] * (256 - len(block1)))

    # Second block initialization (260 bytes for safe padding)
    block2 = bytearray([0] * 260)
    
    # Block 2 data setup
    device_id = SNU[8:14]  # Extract device ID from SNU
    block2[0:6] = bytes.fromhex(device_id)
    block2[6:8] = bytes.fromhex("0007")
    block2[8:10] = struct.pack('<H', 0x0026)
    block2[10:15] = bytes.fromhex("3EF0112233")

    # Final size verification
    assert len(block1) == 256, f"Block1 size is {len(block1)}, expected 256"
    
    return block1, block2

# Create both blocks
block1, block2 = create_blocks()

# Encrypt second block using XXTEA
lunii_generic_key = vectkey_to_bytes(raw_key_generic)

# Prepare block2 for encryption with proper padding
data_to_encrypt = bytes(block2)
if len(data_to_encrypt) < 8:
    # Add padding to reach minimum 8 bytes
    data_to_encrypt += bytes([0] * (8 - len(data_to_encrypt)))

# Ensure data length is multiple of 4 for XXTEA
while len(data_to_encrypt) % 4 != 0:
    data_to_encrypt += bytes([0])

# Encrypt block2
encrypted_block2 = xxtea.encrypt(data_to_encrypt, lunii_generic_key, padding=False)

# Combine both blocks into final MD file
full_md = bytes(block1) + encrypted_block2[:256]

# Save to file
with open('new.md', 'wb') as f:
    f.write(full_md)

# Output results
print("MD file generated successfully!")
print("\nFirst block (unencrypted):")
hex_dump(block1)
print("\nSecond block (encrypted):")
hex_dump(encrypted_block2[:256], 256)
print(f"\nTotal file size: {len(full_md)} bytes")

# Size verification output
print(f"Block1 size: {len(block1)} bytes")
print(f"Data to encrypt size: {len(data_to_encrypt)} bytes") 
print(f"Encrypted block2 size: {len(encrypted_block2)} bytes")
