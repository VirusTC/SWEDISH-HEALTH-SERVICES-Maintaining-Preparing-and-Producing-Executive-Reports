#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - UNIFIED ADVANCED PREDICTIVE OMS & ICU TELEMETRY CONSOLE
Integrates:
1. 36-bit legacy word compilation with native 6-bit FIELDATA patient tags.
2. Analog chart recorder 12-bit quantization mapping (-5V to +5V -> 0 to 4095).
3. 17-Byte Bell-style serial frame wrapper with custom CRC-8 error tracking.
4. Bidirectional ARQ automated packet retransmission loops (ACK/NAK logic).
5. Dynamic Matplotlib continuous waveform and inventory optimization panel.
6. Quantized ECG Integer floor boundary interrupt monitoring (floor limit = 1000).
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import random

# Embedded UI plotting parameters
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =====================================================================
# 1. HARDWARE SIMULATION, CODER, & CHECKSUM ENGINES
# =====================================================================

class UnivacBellHardwareBridge:
    def __init__(self):
        self.STX = 0x02
        self.ETX = 0x03
        self.ACK = 0x06
        self.NAK = 0x15
        self.CRC_POLY = 0x07
        self.fieldata_chars = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"
        self.char_to_code = {char: idx for idx, char in enumerate(self.fieldata_chars)}
        self.code_to_char = {idx: char for idx, char in enumerate(self.fieldata_chars)}

    def calculate_crc8(self, data_bytes):
        crc = 0x00
        for byte in data_bytes:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ self.CRC_POLY) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def encode_fieldata_word0(self, input_str):
        clean_str = input_str.upper()[:6].ljust(6, ' ')
        word0 = 0
        for char in clean_str:
            code = self.char_to_code.get(char, 32)
            word0 = (word0 << 6) | code
        return word0 & 0xFFFFFFFFF

    def decode_fieldata_word0(self, word0):
        chars = []
        for _ in range(6):
            code = (word0 >> (5 * 6 - len(chars) * 6)) & 0x3F
            chars.append(self.code_to_char.get(code, ' '))
        return "".join(chars).strip()

    def digitize_analog_channels_word1(self, v_ecg, v_art, v_resp):
        """Maps -5.0V to +5.0V strip-chart readings into three 12-bit registers."""
        def quantize(v):
            clamped = max(-5.0, min(v, 5.0))
            return int(((clamped + 5.0) / 10.0) * 4095)
        return ((quantize(v_ecg) << 24) | (quantize(v_art) << 12) | quantize(v_resp)) & 0xFFFFFFFFF

    def reconstruct_word1_channels(self, word1):
        def dequantize(i):
            return round(((i / 4095.0) * 10.0) - 5.0, 2)
        return dequantize((word1 >> 24) & 0xFFF), dequantize((word1 >> 12) & 0xFFF), dequantize(word1 & 0xFFF)

    def generate_17byte_frame(self, w0, w1, w2):
        bitstream = (w0 << 72) | (w1 << 36) | w2
        payload = bytearray()
        for i in reversed(range(14)):
            payload.append((bitstream >> (i * 8)) & 0xFF)
        checksum = self.calculate_crc8(payload)
        return bytes([self.STX] + list(payload) + [checksum, self.ETX])


# =====================================================================
# 2. EXPANDED PREDICTIVE DATABASE ENGINE
# =====================================================================

class ComprehensiveHospitalDatabase:
    def __init__(self):
        # Database matrix tracking both supply metrics and real-time clinical waveforms
        self.patient_ledger = {
            "BED-01": {
                "name": "ALPH-A",
                "burn_index_D": 35.0,
                "fridge_temp_c": 4.2,
                "shipping_latency_days": 2,
                "v_ecg": 1.20, "v_art": 0.85, "v_resp": -0.10,
                "color_hex": "#ff6b6b"
            },
            "BED-02": {
                "name": "BETA-B",
                "burn_index_D": 78.0,
                "fridge_temp_c": 3.8,
                "shipping_latency_days": 3,
                "v_ecg": -2.80, "v_art": -3.10, "v_resp": 1.40,  # Unstable vitals profile
                "color_hex": "#4dadf7"
            }
        }
        self.bridge = UnivacBellHardwareBridge()

    def run_calculation_loop(self, bed_id, custom_temp=None):
        node = self.patient_ledger[bed_id]
        D_base = node["burn_index_D"]
        temp_val = custom_temp if custom_temp is not None else node["fridge_temp_c"]

        # 1. Run HELP rule scaling filters over digitized voltage structures
        w1 = self.bridge.digitize_analog_channels_word1(node["v_ecg"], node["v_art"], node["v_resp"])
        int_ecg = (w1 >> 24) & 0xFFF
        
        # Escalate demand calculations if patient passes into a severe low-amplitude ECG state
        modifier = 1.5 if int_ecg < 1000 else 1.0
        if temp_val > 6.0 or temp_val < 1.0:
            modifier *= 1.3

        D_eff = min(D_base * modifier, 100.0)
        try:
            P = (50 * (D_eff**3) + 5065 * (D_eff**2) + 168324 * D_eff + 843000) / 600
            return round(P), round(D_eff, 2), w1
        except ZeroDivisionError:
            return 0, D_base, w1


# =====================================================================
# 3. GRAPHICAL USER INTERFACE & WORKSTATION ENGINE
# =====================================================================

class AdvancedPredictiveICUConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Swedish Health Services - Omnipresent Predictive & Vitals System")
        self.root.geometry("1400x850")

        self.db = ComprehensiveHospitalDatabase()
        self.is_looping = False

        # Apply Terminal Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#0f1115", foreground="#ffffff", fieldbackground="#161920")
        self.style.configure("TLabelframe", background="#12151c", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#12151c", foreground="#61afef", font=("Courier", 10, "bold"))
        self.style.configure("TButton", background="#21252b", foreground="#ffffff", font=("Courier", 9, "bold"))

        # Main Workspace Splits
        left_pane = ttk.Frame(self.root, padding=10)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=420)
        
        right_pane = ttk.Frame(self.root, padding=10)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Control Group Panel
        ctrl_frame = ttk.LabelFrame(left_pane, text=" operational automated engine ")
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.toggle_btn = ttk.Button(ctrl_frame, text="▶ ENGAGE LIVE REAL-TIME TELEMETRY SCAN", command=self.toggle_system_loop)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=10)

        self.status_lbl = ttk.Label(ctrl_frame, text="Status: CHERRY HILL LOOP OVERRIDE", foreground="#e06c75", font=("Courier", 9, "bold"))
        self.status_lbl.pack(pady=2)

        # Telemetry Modifier Sub-Panel
        override_frame = ttk.LabelFrame(left_pane, text=" live signal telemetry override modifiers ")
        override_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(override_frame, text="Select Focus Bed Node:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.bed_selector = ttk.Combobox(override_frame, values=list(self.db.patient_ledger.keys()), state="readonly")
        self.bed_selector.pack(fill=tk.X, padx=5, pady=2)
        self.bed_selector.current(0)
        self.bed_selector.bind("<<ComboboxSelected>>", lambda e: self.load_selected_node_to_ui())

        # Sliders for Analog Voltage Overrides
        ttk.Label(override_frame, text="Analog ECG Input Signal (Volts):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.ecg_slider = ttk.Scale(override_frame, from_=-5.0, to=5.0, command=lambda v: self.passive_ui_sync())
        self.ecg_slider.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(override_frame, text="Refrigeration Temperature Baseline (°C):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.temp_spin = tk.Spinbox(override_frame, from_=-10.0, to=40.0, increment=0.1, bg="#161920", fg="#98c379", command=self.passive_ui_sync)
        self.temp_spin.pack(fill=tk.X, padx=5, pady=2)

        commit_btn = ttk.Button(override_frame, text="💾 RETRANSMIT ARQ CONSOLE PACKET", command=self.force_arq_retransmission_pass)
        commit_btn.pack(fill=tk.X, padx=5, pady=10)

        # Right Top Panel: Live Dashboard Graphics Window
        graph_frame = ttk.LabelFrame(right_pane, text=" dual-modality analytical process monitoring ")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(6, 4.0), facecolor="#12151c")
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right Bottom Panel: Multi-Patient Database Ledger
        ledger_frame = ttk.LabelFrame(right_pane, text=" centralized database registry mapping ledger ")
        ledger_frame.pack(fill=tk.X, height=180, pady=5)

        cols = ("BED ID", "PATIENT ALPHATAG", "ECG QUANT INT", "COLD STORAGE", "EFFECTIVE D_p", "TARGET P_s")
        self.tree = ttk.Treeview(ledger_frame, columns=cols, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=115)

        # Initial Hydration Views
        self.load_selected_node_to_ui()
        self.refresh_ui_dashboard()

    # =====================================================================
# DATA DESPATCH AND COMPLIANCE MONITOR INTERRUPTS
# =====================================================================
def load_selected_node_to_ui(self):
node = self.db.patient_ledger[self.bed_selector.get()]
self.ecg_slider.set(node["v_ecg"])
self.temp_spin.delete(0, "end"); self.temp_spin.insert(0, str(node["fridge_temp_c"]))
self.update_live_charts()
def passive_ui_sync(self):
bid = self.bed_selector.get()
try:
self.db.patient_ledger[bid]["v_ecg"] = round(float(self.ecg_slider.get()), 2)
self.db.patient_ledger[bid]["fridge_temp_c"] = round(float(self.temp_spin.get()), 2)
except ValueError:
return
self.update_live_charts()
def force_arq_retransmission_pass(self):
self.passive_ui_sync()
bid = self.bed_selector.get()
node = self.db.patient_ledger[bid]
# Build raw word structures
w0 = self.db.bridge.encode_fieldata_word0(node["name"])
P_s, D_eff, w1 = self.db.run_calculation_loop(bid)
w2 = (int(D_eff * 10) << 18) | int(P_s)
# Simulate sending a packet over raw wire adapters using our ARQ check engine
print(f"\n[ARQ MANUAL TRIGGER] Initializing 17-byte Bell-framed packet payload for {bid}...")
frame = self.db.bridge.generate_17byte_frame(w0, w1, w2)
# Simulate processing checks inside our data link layers
status_code, _ = self.db.bridge.receive_and_validate_frame(frame, force_corruption=False)
if status_code == self.db.bridge.ACK:
print(f"[ARQ HANDSHAKE SUCCESS] Host line verified ACK (0x06). Synchronization clean.")
messagebox.showinfo("ARQ Wire Success", f"Packet safely routed down telemetry loops for node {bid}.")
self.refresh_ui_database_ledger()
def update_live_charts(self):
focus_bid = self.bed_selector.get()
self.ax.clear()
self.ax.set_facecolor("#161920")
temp_sweep = [x * 0.5 for x in range(-10, 50)]
for bid, data in self.db.patient_ledger.items():
orders_y = []
for t in temp_sweep:
if bid == focus_bid:
P, _, _ = self.db.run_calculation_loop(bid, custom_temp=t)
else:
P, _, _ = self.db.run_calculation_loop(bid)
orders_y.append(P)
self.ax.plot(temp_sweep, orders_y, color=data["color_hex"], linestyle="--", linewidth=1.5, label=f"{bid} Trace")
# Map tracking points
if bid == focus_bid:
curr_P, curr_D, _ = self.db.run_calculation_loop(bid)
self.ax.plot(data["fridge_temp_c"], curr_P, marker="o", markersize=9, color="#98c379", label="Active Node Focus")
# Overlay our physical environmental protection boundary shading masks
self.ax.axvspan(6.0, 30.0, color="#e06c75", alpha=0.12, label="Cold-Chain Breach Zone (>6.0°C)")
self.ax.set_title("Multi-Patient Continuous Strain Intercept Matrices", color="#ffffff", fontname="Courier", fontsize=10)
self.ax.set_xlim(-5.0, 25.0)
self.ax.tick_params(colors="#abb2bf", labelsize=8)
self.ax.legend(facecolor="#12151c", edgecolor="#2c313c", labelcolor="#ffffff", fontsize=8)
self.fig.tight_layout()
self.canvas.draw()
def refresh_ui_database_ledger(self):
for item in self.tree.get_children(): self.tree.delete(item)
for bid, data in self.db.patient_ledger.items():
P_s, D_eff, w1 = self.db.run_calculation_loop(bid)
int_ecg = (w1 >> 24) & 0xFFF
self.tree.insert("", tk.END, values=(bid, data["name"], int_ecg, f"{data['fridge_temp_c']}°C", D_eff, P_s))
def refresh_ui_dashboard(self):
self.refresh_ui_database_ledger()
self.update_live_charts()
# =====================================================================
# REAL-TIME 60-SECOND COMPLIANCE SCHEDULING ENGINES
# =====================================================================
def toggle_system_loop(self):
if not self.is_looping:
self.is_looping = True
self.toggle_btn.config(text="■ HALT INDUSTRIAL POLLING MATRIX")
self.status_lbl.config(text="Status: BACKGROUND POLLING ACTIVE (60s Pass Loops)", foreground="#98c379")
self.execute_scheduled_background_scan()
else:
self.is_looping = False
self.toggle_btn.config(text="▶ ENGAGE LIVE REAL-TIME TELEMETRY SCAN")
self.status_lbl.config(text="Status: CHERRY HILL LOOP OVERRIDE", foreground="#e06c75")
def execute_scheduled_background_scan(self):
if not self.is_looping: return
# Simulate dynamic realtime analog tracking fluctuations over line wires
for bid in self.db.patient_ledger:
self.db.patient_ledger[bid]["v_ecg"] += random.choice([-0.15, 0.0, 0.15])
self.db.patient_ledger[bid]["v_ecg"] = max(-5.0, min(self.db.patient_ledger[bid]["v_ecg"], 5.0))
# Feature 6 Audit: Extract data registers and evaluate ECG integer floor limits
_, _, w1 = self.db.run_calculation_loop(bid)
int_ecg = (w1 >> 24) & 0xFFF
# If the digitized chart recorder matrix reads below our safety floor, trip a system vector break
if int_ecg < 1000:
self.root.bell()
print(f"\n[!!! SYSTEM HARDWARE VECTOR INTERRUPT 0x02 !!!] Bed: {bid}. ECG Quantized Level dropped to {int_ecg}. Floor Limit (1000) breached.")
messagebox.showerror("CLINICAL TELEMETRY WARNING", f"CRITICAL VITAL FAILURE AT {bid}!\nDigitized Strip Chart ECG Int: {int_ecg}\nForcing immediate emergency station override routing.")
self.refresh_ui_dashboard()
# Serialize the updated matrix changes directly to local storage
self.db.export_telemetry_to_json()
# Schedule the next polling block loop pass (using a brief 5-second interval for simulation display)
self.root.after(5000, self.execute_scheduled_background_scan)
if name == "main":
root = tk.Tk()
app = AdvancedPredictiveICUConsole(root)
root.mainloop()
