#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - UNIVAC ARQ AUTOMATED RETRY & ANALOG TRANSLATION SYSTEM
Implements an Automatic Repeat reQuest (ARQ) pipeline over serial channels
combined with 12-bit quantization mapping for early analog chart recorders.
"""

import sys
import time
import random

class UnivacARQDigitizerSuite:
    def __init__(self):
        self.STX = 0x02
        self.ETX = 0x03
        self.ACK = 0x06  # Hardware Handshake: Acknowledge Packet
        self.NAK = 0x15  # Hardware Handshake: Negative Acknowledge (Error/Resend)
        self.CRC_POLY = 0x07

    def calculate_crc8(self, data_bytes):
        """Computes a bitwise cyclic redundancy check value over a byte array payload."""
        crc = 0x00
        for byte in data_bytes:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ self.CRC_POLY) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    # =====================================================================
    # FEATURE 1: ANALOG CHART RECORDER TRANSLATION MAPS
    # =====================================================================

    def digitize_analog_voltages_to_word1(self, v_ecg, v_art, v_resp):
        """
        Translates raw analog inputs (-5.0V to +5.0V range) from legacy recorders
        into a singular 36-bit UNIVAC data word containing three 12-bit integer channels.
        """
        # Quantize function: maps -5.0V -> 0 and +5.0V -> 4095
        def quantize(v):
            clamped = max(-5.0, min(v, 5.0))
            normalized = (clamped + 5.0) / 10.0
            return int(normalized * 4095)

        int_ecg = quantize(v_ecg)
        int_art = quantize(v_art)
        int_resp = quantize(v_resp)

        # Shift the 12-bit unsigned components into Word 1 array geometry
        word1_36 = (int_ecg << 24) | (int_art << 12) | int_resp
        return word1_36 & 0xFFFFFFFFF

    def reconstruct_word1_to_voltages(self, word1_36):
        """Converts a 36-bit UNIVAC data word back to physiological voltages."""
        int_ecg = (word1_36 >> 24) & 0xFFF
        int_art = (word1_36 >> 12) & 0xFFF
        int_resp = word1_36 & 0xFFF

        def dequantize(i):
            return round(((i / 4095.0) * 10.0) - 5.0, 2)

        return dequantize(int_ecg), dequantize(int_art), dequantize(int_resp)

    # =====================================================================
    # FEATURE 2: AUTOMATIC REPEAT REQUEST (ARQ) LOOP
    # =====================================================================

    def generate_hardware_frame(self, w0, w1, w2):
        """Builds a standardized 17-byte Bell-style telemetry envelope."""
        bitstream = (w0 << 72) | (w1 << 36) | w2
        payload_bytes = bytearray()
        for i in reversed(range(14)):
            payload_bytes.append((bitstream >> (i * 8)) & 0xFF)
        
        checksum = self.calculate_crc8(payload_bytes)
        
        frame = bytearray()
        frame.append(self.STX)
        frame.extend(payload_bytes)
        frame.append(checksum)
        frame.append(self.ETX)
        return bytes(frame)

    def receive_and_validate_frame(self, frame_bytes, force_corruption=False):
        """Simulates receiving hardware processing logic with built-in validation checks."""
        if len(frame_bytes) != 17 or frame_bytes[0] != self.STX or frame_bytes[-1] != self.ETX:
            return self.NAK, None

        payload = bytearray(frame_bytes[1:15])
        if force_corruption:
            payload[0] ^= 0xFF  # Induce line static / bit flip to test error handling

        transmitted_checksum = frame_bytes[15]
        computed_checksum = self.calculate_crc8(payload)

        if computed_checksum != transmitted_checksum:
            return self.NAK, None  # Checksum failed: request a retransmission
        return self.ACK, payload

    def transmit_packet_with_arq_protection(self, w0, w1, w2, simulate_line_noise=True):
        """
        Transmits telemetry payload data with an active ARQ retry architecture.
        Continuously loops and re-sends packets if lines log a CHECKSUM_MISMATCH.
        """
        base_frame = self.generate_hardware_frame(w0, w1, w2)
        max_attempts = 5
        attempt = 1

        print(f"[ARQ INITIALIZE] Outbound packet prepared. Frame envelope size: {len(base_frame)} bytes.")

        while attempt <= max_attempts:
            print(f"[ARQ LOOP] Attempt {attempt} of {max_attempts}: Transmitting over physical copper loops...")
            
            # Simulate high line static probability on the initial run over analog systems
            induce_noise = simulate_line_noise and (attempt < 3)
            if induce_noise:
                print(" ! Line Static Intercepted: Simulating telephone line attenuation breach.")

            # Process inbound terminal loop response code
            response_code, verified_payload = self.receive_and_validate_frame(base_frame, force_corruption=induce_noise)

            if response_code == self.ACK:
                print(f"[ARQ SUCCESS] Line Handshake ACK (0x06) received. Synchronization validated in {attempt} cycles.\n")
                return True
            else:
                print(f" ? Line Handshake NAK (0x15) trapped: CHECKSUM_MISMATCH flagged. Scheduling immediate link resend...")
                attempt += 1
                time.sleep(0.1)  # Settling delay window to clear noisy lines

        print("[ARQ TIMEOUT FAULT] System connection dropped. Line exceeded maximum retry bounds.\n")
        return False


# =====================================================================
# INTEGRATION TESTING RUNSUITE
# =====================================================================

if __name__ == "__main__":
    print("UNIVAC ARQ RETRY DAEMON & RECORDER DIGITIZER TEST LOGS")
    print("=" * 70)
    
    suite = UnivacARQDigitizerSuite()

    # 1. Simulate reading real-time inputs from an analog ECG strip recorder
    analog_ecg_v = 1.25     # +1.25V trace
    analog_art_v = -2.40     # -2.40V trace
    analog_resp_v = 0.05     # +0.05V trace
    
    print("Step 1: Quantizing raw chart recorder analog voltages into 36-bit telemetry positions...")
    packed_word1 = suite.digitize_analog_voltages_to_word1(analog_ecg_v, analog_art_v, analog_resp_v)
    print(f"-> Compiled Word 1 Register (Hex): 0x{packed_word1:09X}")

    # 2. Cross-verify precision loss limits
    rec_ecg, rec_art, rec_resp = suite.reconstruct_word1_to_voltages(packed_word1)
    print(f"-> Reconstructed Check Voltages : ECG: {rec_ecg}V, ART: {rec_art}V, RESP: {rec_resp}V")

    # 3. Fire the ARQ transmission loops using fake Word 0 and Word 2 constants
    print("\nStep 2: Engaging automated ARQ transmission daemon...")
    word0_patient = 0x123456789
    word2_metrics = 0x999FFF111
    
    suite.transmit_packet_with_arq_protection(word0_patient, packed_word1, word2_metrics, simulate_line_noise=True)
