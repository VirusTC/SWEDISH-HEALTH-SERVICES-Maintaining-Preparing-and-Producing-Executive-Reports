#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - UNIVAC FIELDATA CODER & RS-232 TELEMETRY STREAMER
Implements native 6-bit character string extraction into 36-bit register frameworks,
paired with an 8-bit byte serialization loop for retro serial lines.
"""

import sys
import struct

try:
    import serial
except ImportError:
    # Safe fallback if pySerial is not installed during staging tests
    serial = None

class UnivacFieldataRS232Driver:
    def __init__(self):
        # 1. Initialize the standard 64-character UNIVAC 1100 FIELDATA matrix
        self.fieldata_chars = (
            "@ABCDEFGHIJKLMNO"
            "PQRSTUVWXYZ[\\]^_"
            " !\"#$%&'()*+,-./"
            "0123456789:;<=>?"
        )
        # Create ultra-fast twin lookup hash tables
        self.char_to_code = {char: idx for idx, char in enumerate(self.fieldata_chars)}
        self.code_to_char = {idx: char for idx, char in enumerate(self.fieldata_chars)}

    def encode_string_to_fieldata_word(self, input_str):
        """
        Packs a standard text string into a single 36-bit word cell.
        Max capacity: Exactly 6 characters (6 bits * 6 chars = 36 bits).
        """
        # Enforce strict uppercase standard and pad with master space if under 6 chars
        clean_str = input_str.upper()[:6].ljust(6, ' ')
        word_36 = 0
        
        for char in clean_str:
            code = self.char_to_code.get(char, 32) # Fallback to Master Space (Index 32) if invalid
            word_36 = (word_36 << 6) | code
            
        return word_36 & 0xFFFFFFFFF

    def decode_fieldata_word_to_string(self, word_36):
        """Extracts 6 text characters back out from a legacy 36-bit integer cell."""
        chars = []
        for _ in range(6):
            # Extract trailing 6-bit chunk
            code = (word_36 >> (5 * 6 - len(chars) * 6)) & 0x3F
            chars.append(self.code_to_char.get(code, ' '))
        return "".join(chars).strip()

    def serialize_108bit_block_to_rs232_bytes(self, word0, word1, word2):
        """
        Transforms three 36-bit words into a sequential 14-byte array block.
        Ensures perfect 8-bit framing continuity for RS-232 transmission.
        """
        # Combine independent register slots into a singular 108-bit bitstream integer
        bitstream = (word0 << 72) | (word1 << 36) | word2
        
        byte_array = bytearray()
        # Extract 14 separate 8-bit bytes sequentially
        for i in reversed(range(14)):
            byte_array.append((bitstream >> (i * 8)) & 0xFF)
            
        return bytes(byte_array)

    def deserialize_rs232_bytes_to_108bit_block(self, raw_bytes):
        """Reconstructs 36-bit word blocks from an incoming 14-byte array sequence."""
        if len(raw_bytes) != 14:
            raise ValueError(f"Payload error: Expected exactly 14 data bytes, read {len(raw_bytes)}")
            
        bitstream = 0
        for b in raw_bytes:
            bitstream = (bitstream << 8) | b
            
        # Re-partition back into separate 36-bit arrays
        word0 = (bitstream >> 72) & 0xFFFFFFFFF
        word1 = (bitstream >> 36) & 0xFFFFFFFFF
        word2 = bitstream & 0xFFFFFFFFF
        
        return word0, word1, word2

    def open_hardware_serial_port(self, port_name="COM1", baud=9600):
        """Configures a communication session over historical RS-232 lines."""
        if not serial:
            print("pyserial dependency missing. Running in dry-run loop mode.")
            return None
        # Deploy standard legacy configuration bounds: 8 data bits, no parity, 1 stop bit
        return serial.Serial(
            port=port_name,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )


# =====================================================================
# INTEGRATED VERIFICATION RUNNER
# =====================================================================

if __name__ == "__main__":
    print("UNIVAC 6-BIT FIELDATA & RS-232 OVER-THE-WIRE LOOPBACK TEST")
    print("=" * 65)

    driver = UnivacFieldataRS232Driver()

    # 1. Define Patient and Clinical Values
    patient_name_input = "DOE J"
    mock_word1_vitals = 0x555AAA333  # Packaged integers (HR, MAP, Drainage)
    mock_word2_metrics = 0x777FFF111 # Computational telemetry outputs (D, P)

    print(f"Original Patient Tag : '{patient_name_input}'")

    # 2. Encode to 6-Bit FIELDATA Word 0 Register
    word0_packed = driver.encode_string_to_fieldata_word(patient_name_input)
    print(f"Packed Word 0 (Hex)  : 0x{word0_packed:09X}")

    # 3. Serialize the 3-Word Data Block to an 8-Bit Byte Stream for RS-232 Hardware
    rs232_payload = driver.serialize_108bit_block_to_rs232_bytes(word0_packed, mock_word1_vitals, mock_word2_metrics)
    print(f"RS-232 Wire Payload  : {list(rs232_payload)} ({len(rs232_payload)} Bytes)")

    # 4. Simulate Terminal Extraction on the main frame receiver line
    w0, w1, w2 = driver.deserialize_rs232_bytes_to_108bit_block(rs232_payload)
    decoded_name = driver.decode_fieldata_word_to_string(w0)
    
    print("-" * 65)
    print(f"Extracted Word 0 Hex : 0x{w0:09X}")
    print(f"Decoded Patient Tag  : '{decoded_name}'")

    # Final Data Integrity Assertion Check
    if decoded_name == patient_name_input:
        print("\n>>> SUCCESS: FIELDATA TO SERIAL LOOPBACK VERIFIED WITH NO BIT SHIFTS <<<")
    else:
        print("\n>>> ERROR: SERIAL ARCHITECTURE BUFFER ALIGNMENT MISMATCH <<<")
