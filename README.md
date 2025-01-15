# Lunii MD File Generator

A Python script to generate authentication `.md` files for Lunii (v2 maybe other...) storyteller devices.

## Description

This tool generates the `.md` authentication file required for Lunii storyteller devices based on the device's unique serial number (SNU). The `.md` file consists of two 256-byte blocks:
- First block: Unencrypted data containing version information and device SNU
- Second block: XXTEA-encrypted data containing device-specific information

## Requirements

- Python 3.6+
- xxtea library (`pip install xxtea`)

## Usage

1. Clone this repository
2. Install dependencies:
```bash
pip install xxtea
```
3. Adjust SNU, VERSION_MAJOR, VERSION_MINOR with your information (you can retrieve them via UART Debug)

4. Run the script:
```bash
python md_generator.py
```
5. I have a bug actually I have a missing 00 value at address #000000FF so add it before use it.

The script will create a `new.md` file in the current directory. Rename it to `.md` (with the leading dot) and place it at the root of your Lunii's SD card.
And change it to hidden file.

## File Structure

- The first block contains:
  - Firmware version (2.19)
  - Device SNU (Serial Number)
  - Static data ("AENSPECIAL" string)
- The second block contains:
  - Device-specific data
  - Encrypted using XXTEA algorithm with known key

## Technical Details

- Uses XXTEA encryption
- Fixed block size of 256 bytes
- Compatible with Lunii firmware 2.19+
- Generates SD card authentication file

## Disclaimer

This tool is for educational and backup purposes only. Please respect intellectual property rights and use responsibly.

## Credits / Special Thanks

Special thanks to:

- [o-daneel](https://github.com/o-daneel) for the excellent [Lunii.RE](https://github.com/o-daneel/Lunii.RE) project which provided invaluable research and documentation about Lunii's architecture and file formats. This tool would not have been possible without their detailed reverse engineering work.

This project builds upon the findings and documentation from their research into the Lunii storyteller device, particularly regarding the authentication file structure and encryption methods.

Their work on documenting the .md file format, XXTEA implementation, and overall device architecture has been instrumental in creating this tool.
