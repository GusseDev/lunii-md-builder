import struct
import xxtea

# Cette version nécessite d'ajouter manuelle 00 à l'adresse #000000FF
# Clé générique identifiée
raw_key_generic = [0x91BD7A0A, 0xA75440A9, 0xBBD49D6C, 0xE0DCC0E3]

def vectkey_to_bytes(key_vect):
    joined = [k.to_bytes(4, 'little') for k in key_vect]
    return b''.join(joined)

def hex_dump(data, start_address=0):
    for i in range(0, len(data), 16):
        # Obtenez 16 octets de données
        chunk = data[i:i+16]
        # Créez la partie hexadécimale
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        # Créez la partie ASCII (pour les caractères imprimables)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        # Remplissez avec des espaces si nécessaire
        hex_part = f"{hex_part:<48}"
        # Affichez la ligne
        print(f"{start_address + i:08x}: {hex_part} | {ascii_part}")

# Paramètres pour votre Lunii
SNU = "0000000000000000"  # Votre numéro de série
VERSION_MAJOR = 2
VERSION_MINOR = 19

def create_block1():
    # Premier bloc (non chiffré)
    block = bytearray(256)  # Initialise avec des zéros

    # Structure du bloc - avec correction du header
    block[0] = 0x03
    block[1] = 0x00  # Ajout du 0x00 manquant
    block[2:6] = bytes([0xff, 0xff, 0xff, 0xff])  # Séquence de FF corrigée
    block[6:8] = bytes([0x02, 0x00])  # Version majeure
    block[8:10] = bytes([VERSION_MINOR, 0x00])  # Version mineure
    block[10:17] = bytes.fromhex(SNU[:14])  # SNU
    block[17] = 0x00  # Null terminator
    block[18:31] = bytes.fromhex("830441A34E5350454349414C")  # Static data "AENSPECIAL"
    block[31] = 0x00  # Null terminator
    
    return block

def create_block2():
    # Second bloc (à chiffrer)
    block = bytearray(256)  # Initialise avec des zéros

    # Données pour le bloc
    device_id = SNU[8:14]  # Prend une partie du SNU comme device ID
    block[0:7] = bytes.fromhex(device_id + "0007")  # Device ID suivi de 0007
    block[7:9] = struct.pack('<H', 0x0026)  # Static
    block[9:14] = bytes.fromhex("3EF0112233")  # Static

    return block

# Création des blocs
block1 = create_block1()
block2 = create_block2()

# S'assurer que block2 est un multiple de 4 avant le chiffrement
while len(block2) % 4 != 0:
    block2.append(0)

# Chiffrement du second bloc
lunii_generic_key = vectkey_to_bytes(raw_key_generic)
encrypted_block2 = xxtea.encrypt(bytes(block2), lunii_generic_key, padding=False, rounds=32)

# Combine les deux blocs
full_md = bytes(block1) + encrypted_block2

# Sauvegarde du fichier
with open('new.md', 'wb') as f:
    f.write(full_md)

print("Fichier .md généré avec succès !")

print("\nPremier bloc (non chiffré):")
hex_dump(block1)

print("\nSecond bloc (chiffré):")
hex_dump(encrypted_block2, 256)  # Commence à l'adresse 0x100 (256)
