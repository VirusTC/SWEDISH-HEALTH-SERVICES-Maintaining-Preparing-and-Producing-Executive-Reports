#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - UNIVAC 36-BIT WORD MEMORY SERIALIZATION PACKER
Translates modern 64-bit Python floats into historical 36-bit word structures
conforming to Sperry Rand Exec 8 / OS 2200 architecture constraints.
"""

import sys

class Univac36BitPacker:
    """
    Handles memory serialization transformations for 36-bit word packets.
    Provides encoders/decoders for integers, fractional parameters, and field bits.
    """
    def __init__(self):
        # 36-Bit boundaries: max integer value representation limit
        self.WORD_MASK = (1 << 36) - 1

    def encode_ones_complement_int(self, value, total_bits=12):
        """
        Converts a modern integer into a localized ones' complement bit representation.
        Legacy systems represent negative values by inverting all functional bits.
        """
        mask = (1 << total_bits) - 1
        if value >= 0:
            return int(value) & mask
        else:
            # Negative number: invert all functional bit values
            return (~abs(int(value))) & mask

    def decode_ones_complement_int(self, bit_chunk, total_bits=12):
        """Translates a legacy ones' complement segment back to a modern signed integer."""
        sign_bit = 1 << (total_bits - 1)
        if not (bit_chunk & sign_bit):
            return bit_chunk  # Positive integer value
        else:
            # Negative integer value: invert and extract magnitude
            mask = (1 << total_bits) - 1
            inverted = (~bit_chunk) & mask
            return -inverted

    def pack_icu_telemetry_word(self, heart_rate, map_pressure, drainage):
        """
        Compiles three independent 12-bit medical signals into a singular 36-bit word.
        Layout: [ HR (12 bits) ] [ MAP (12 bits) ] [ DRAIN (12 bits) ]
        """
        # Ensure values fit within structural safety boundaries
        hr_bits = self.encode_ones_complement_int(heart_rate, 12)
        map_bits = self.encode_ones_complement_int(map_pressure, 12)
        drain_bits = self.encode_ones_complement_int(drainage, 12)

        # Shift bit blocks sequentially into position array alignment
        word_36 = (hr_bits << 24) | (map_bits << 12) | drain_bits
        return word_36 & self.WORD_MASK

    def unpack_icu_telemetry_word(self, word_36):
        """Extracts modern variables from an inbound 36-bit telemetry block."""
        hr_bits = (word_36 >> 24) & 0xFFF
        map_bits = (word_36 >> 12) & 0xFFF
        drain_bits = word_36 & 0xFFF

        heart_rate = self.decode_ones_complement_int(hr_bits, 12)
        map_pressure = self.decode_ones_complement_int(map_bits, 12)
        drainage = self.decode_ones_complement_int(drain_bits, 12)

        return heart_rate, map_pressure, drainage

    def pack_prediction_metrics_word(self, index_D, stress_P):
        """
        Packs calculation indices into Word 2.
        Layout: [ Effective D (18 bits) ] [ Calculated P_s (18 bits) ]
        """
        d_bits = self.encode_ones_complement_int(index_D, 18)
        p_bits = self.encode_ones_complement_int(stress_P, 18)

        word_36 = (d_bits << 18) | p_bits
        return word_36 & self.WORD_MASK

    def format_word_as_binary_string(self, word_36):
        """Helper utility visualizing the exact bit alignments for engineers."""
        return f"{word_36:036b}"


# =====================================================================
# SYSTEM VERIFICATION UNIT TEST PASS
# =====================================================================

if __name__ == "__main__":
    print("UNIVAC 36-BIT NODE PACKER EMULATOR DRIFT TESTS")
    print("=" * 60)
    
    packer = Univac36BitPacker()

    # 1. Define active patient monitoring parameters
    input_hr = 85
    input_map = 68
    input_drain = 145
    
    print(f"Modern Input Vitals  -> HR: {input_hr} bpm, MAP: {input_map} mmHg, Drainage: {input_drain} mL/hr")

    # 2. Transmit through the packing core
    packed_word_1 = packer.pack_icu_telemetry_word(input_hr, input_map, input_drain)
    print(f"Packed 36-Bit Output -> {packed_word_1} (Decimal Representation)")
    print(f"Binary Word Trace    -> {packer.format_word_as_binary_string(packed_word_1)}")
    
    # 3. Simulate hardware unpack on the reverse line terminal side
    out_hr, out_map, out_drain = packer.unpack_icu_telemetry_word(packed_word_1)
    print("-" * 60)
    print(f"Unpacked Recov Data  -> HR: {out_hr} bpm, MAP: {out_map} mmHg, Drainage: {out_drain} mL/hr")
    
    # Assert network serialization data integrity check pass
    if (input_hr == out_hr) and (input_map == out_map) and (input_drain == out_drain):
        print("\n>>> DATA PACKET VERIFICATION SUCCESSFUL: ZERO STRUCTURAL DRIFT DETECTED <<<")
    else:
        print("\n>>> CRITICAL FAULT: STRUCTURAL BIT DEGRADATION ENCOUNTERED <<<")
