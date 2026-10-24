#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - BELL-STYLE FRAMED RS-232 SERIAL LINK DRIVER
Implements STX/ETX character framing, custom CRC-8 mathematical validation,
and device abstractions for legacy Western Electric / Bell acoustic hardware lines.
"""

import sys
import time

try:
    import serial
except ImportError:
    serial = None

class BellFramedUnivacDriver:
    def __init__(self):
        # STX (Start of Text) and ETX (End of Text) hardware frame flags
        self.STX = 0x02
        self.ETX = 0x03
        
        # Standard CRC-8 Polynomial: x^8 + x^2 + x + 1 (Maxim/Dallas Standard)
        self.CRC_POLY = 0x07

    def calculate_crc8(self, data_bytes):
        """
        Computes a bitwise cyclic redundancy check value over a byte array payload.
        Ensures absolute data transmission fidelity over noisy telephone wire lines.
        """
        crc = 0x00
        for byte in data_bytes:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ self.CRC_POLY) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def serialize_and_frame_packet(self, word0, word1, word2):
        """
        Compiles three 36-bit words, wraps them inside an STX/ETX framework,
        and appends a calculated CRC-8 validation byte. Total Frame Size = 17 Bytes.
        """
        # 1. Combine registers into a flat 108-bit bitstream integer
        bitstream = (word0 << 72) | (word1 << 36) | word2
        
        # 2. Slice bitstream into the standard 14 separate data bytes
        payload_bytes = bytearray()
        for i in reversed(range(14)):
            payload_bytes.append((bitstream >> (i * 8)) & 0xFF)
            
        # 3. Calculate the CRC-8 byte over the raw 14 data bytes
        checksum_byte = self.calculate_crc8(payload_bytes)
        
        # 4. Construct the complete 17-byte hardware frame envelope
        final_frame = bytearray()
        final_frame.append(self.STX)
        final_frame.extend(payload_bytes)
        final_frame.append(checksum_byte)
        final_frame.append(self.ETX)
        
        return bytes(final_frame)

    def unframe_and_deserialize_packet(self, raw_frame):
        """
        Validates envelope markers and verifies checksum integrity.
        Reconstructs the internal 36-bit words if validation succeeds.
        """
        if len(raw_frame) != 17:
            return None, "FRAME_SIZE_ERROR: Incomplete transmission block length."
            
        if raw_frame[0] != self.STX or raw_frame[16] != self.ETX:
            return None, "FRAME_MARKER_ERROR: Corrupted STX or ETX framing bits."
            
        # Isolate payload and extracted checksum
        payload_bytes = raw_frame[1:15]
        extracted_checksum = raw_frame[15]
        
        # Recalculate local checksum to cross-reference line distortions
        computed_checksum = self.calculate_crc8(payload_bytes)
        if computed_checksum != extracted_checksum:
            return None, f"CHECKSUM_MISMATCH: Computed 0x{computed_checksum:02X} != Read 0x{extracted_checksum:02X}. Frame dropped."
            
        # Rebuild 108-bit chunk from valid byte stream
        bitstream = 0
        for b in payload_bytes:
            bitstream = (bitstream << 8) | b
            
        # Partition back to native Univac architecture words
        word0 = (bitstream >> 72) & 0xFFFFFFFFF
        word1 = (bitstream >> 36) & 0xFFFFFFFFF
        word2 = bitstream & 0xFFFFFFFFF
        
        return (word0, word1, word2), "SUCCESS_OK"

    def initialize_bell_modem_port(self, override_port=None):
        """
        Maps standard device names to traditional Bell-style hardware loops.
        Historically, Bell modems run at optimized transmission bounds like 1200 or 2400 baud.
        """
        if not serial:
            return None
            
        # Automated port resolution hierarchy matching classic hospital terminal maps
        target_port = override_port if override_port else ("/dev/ttyUSB0" if sys.platform != "win32" else "COM3")
        
        return serial.Serial(
            port=target_port,
            baudrate=1200,                # Standard Bell 212A modulation rate
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2.0                   # Extended latch window for high-latency leased lines
        )


# =====================================================================
# SYSTEM VERIFICATION COMPLIANCE SUITE
# =====================================================================

if __name__ == "__main__":
    print("UNIVAC AUTOMATED DATA SYSTEM - CHECKSUM FRAMING UNIT TESTS")
    print("=" * 70)
    
    driver = BellFramedUnivacDriver()

    # Mock 36-bit register allocations matching patient records
    w0_patient = 0x123456789   # "DOE J" FIELDATA representation
    w1_vitals  = 0x555AAA333   # Patient vital constants
    w2_metrics = 0x777FFF111   # Calculated algorithmic output metrics

    print("Step 1: Compiling registers and computing mathematical checksum envelope...")
    transmission_packet = driver.serialize_and_frame_packet(w0_patient, w1_vitals, w2_metrics)
    print(f"-> Generated Full Hardware Frame Size: {len(transmission_packet)} Bytes")
    print(f"-> Byte Array Stream: {list(transmission_packet)}")

    print("\nStep 2: Processing inbound loopback parsing sequence...")
    data_block, status_log = driver.unframe_and_deserialize_packet(transmission_packet)
    print(f"-> Link Response Log Status: {status_log}")
    if data_block:
        print(f"-> Restored Register Word 0: 0x{data_block[0]:09X}")

    print("\nStep 3: Simulating line static / analog wire signal corruption test...")
    corrupted_packet = bytearray(transmission_packet)
    corrupted_packet[5] ^= 0x01 # Force a bit flip to simulate physical cable crackle noise
    
    failed_block, error_log = driver.unframe_and_deserialize_packet(bytes(corrupted_packet))
    print(f"-> Link Response Log Status: {error_log}")
    
    if not failed_block:
        print("\n>>> SUCCESS: AUTOMATED ALERTS DROP CRACKLED CORRUPTED TRANSMISSIONS NATIVELY <<<")
    else:
        print("\n>>> SECURITY VIOLATION: INVALID MEMORY WRITES PASSED PARSING BUFFER <<<")
