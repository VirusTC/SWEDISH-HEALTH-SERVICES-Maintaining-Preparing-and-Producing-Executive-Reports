#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - OMNIPRESENT CLINICAL DIGITIZER & ACCOUNTING PIPELINE
Fulfills capabilities:
1. Analog Temperature Probe 12-bit quantization translation (-2.0C to +45.0C).
2. Automated QuickBooks ledger counter reset upon Epic confirmation.
3. Persistent archiving of outbound transaction payloads to 'telemetry_history.json'.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import random

class CompleteSystemOrchestrator:
    def __init__(self):
        self.log_filename = "telemetry_history.json"
        
        # QuickBooks Service Catalog Definition Matrix
        self.billing_catalog = {
            "TRUNK_POLL": {"qb_code": "QB-UNIVAC-TRUNK", "unit_price": 0.05, "units_consumed": 15},
            "CUBIC_COMPUTE": {"qb_code": "QB-MAPPER-POLY", "unit_price": 0.02, "units_consumed": 120},
            "ANALOG_QUANT": {"qb_code": "QB-ICU-QUANT", "unit_price": 1.50, "units_consumed": 8}
        }

    # =====================================================================
    # FEATURE 1: THERMISTOR TEMPERATURE QUANTIZATION SUBROUTINE
    # =====================================================================
    def digitize_vitals_to_word1(self, v_ecg, v_art, temp_c):
        """
        Quantizes medical waveforms alongside analog temperature probes into a 36-bit word.
        Temperature range parameters: -2.0C to +45.0C -> maps to 0-4095 integers.
        """
        def quantize_wave(v):
            clamped = max(-5.0, min(v, 5.0))
            return int(((clamped + 5.0) / 10.0) * 4095)

        def quantize_temp(t):
            clamped = max(-2.0, min(t, 45.0))
            return int(((clamped + 2.0) / 47.0) * 4095)

        int_ecg = quantize_wave(v_ecg)
        int_art = quantize_wave(v_art)
        int_temp = quantize_temp(temp_c)

        word1_36 = (int_ecg << 24) | (int_art << 12) | int_temp
        return word1_36 & 0xFFFFFFFFF

    def reconstruct_word1_channels(self, word1_36):
        """Dequantizes 36-bit word registers back into physical physiological scales."""
        int_ecg = (word1_36 >> 24) & 0xFFF
        int_art = (word1_36 >> 12) & 0xFFF
        int_temp = word1_36 & 0xFFF

        v_ecg = round(((int_ecg / 4095.0) * 10.0) - 5.0, 2)
        v_art = round(((int_art / 4095.0) * 10.0) - 5.0, 2)
        temp_c = round(((int_temp / 4095.0) * 47.0) - 2.0, 1)

        return v_ecg, v_art, temp_c

    # =====================================================================
    # FEATURE 2 & 3: EPIC BACKUP LOGGING & RESET DRIVERS
    # =====================================================================
    def compile_transaction_invoice(self):
        line_items = []
        grand_total = 0.0
        for key, data in self.billing_catalog.items():
            cost = data["units_consumed"] * data["unit_price"]
            grand_total += cost
            line_items.append({
                "qb_code": data["qb_code"],
                "units": data["units_consumed"],
                "rate": data["unit_price"],
                "total_cost": round(cost, 2)
            })
        
        return {
            "transaction_id": f"TX-EPIC-{int(time.time())}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "total_invoice_charge": round(grand_total, 2),
            "items": line_items
        }

    def append_to_telemetry_history(self, payload):
        """Appends outbound text blocks directly to the persistent JSON storage map."""
        history = []
        if os.path.exists(self.log_filename):
            try:
                with open(self.log_filename, "r") as f:
                    history = json.load(f)
                    if not isinstance(history, list): history = []
            except json.JSONDecodeError:
                history = []

        history.append(payload)
        if len(history) > 100: history.pop(0)  # Safe rotation boundary limit

        with open(self.log_filename, "w") as f:
            json.dump(history, f, indent=4)

    def execute_epic_handshake_reset(self):
        """Simulates an upload handshake receipt; zeroes all accrued ledger items."""
        invoice = self.compile_transaction_invoice()
        
        # 1. First save complete copy out to local JSON file systems
        self.append_to_telemetry_history(invoice)
        
        # 2. Reset resource utilization counters immediately upon confirmation
        for key in self.billing_catalog:
            self.billing_catalog[key]["units_consumed"] = 0
            
        return invoice


# =====================================================================
# 3. INTERFACE TERMINAL REGISTRY CONSOLE
# =====================================================================

class UnifiedSystemConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Swedish Health Services - Centralized Integrated Pipeline Terminal")
        self.root.geometry("1100x650")

        self.core = CompleteSystemOrchestrator()

        # Design Theme Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#0c0e12", foreground="#ffffff", fieldbackground="#141821")
        self.style.configure("TLabelframe", background="#10141a", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#10141a", foreground="#61afef", font=("Courier", 10, "bold"))
        self.style.configure("TButton", background="#212631", foreground="#ffffff", font=("Courier", 9, "bold"))

        # Workspace Layout
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=380)

        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Column: Inputs and Overrides
        temp_frame = ttk.LabelFrame(left_panel, text=" analog temperature input ")
        temp_frame.pack(fill=tk.X, pady=5)

        ttk.Label(temp_frame, text="Probe Celsius Configuration:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.temp_spin = tk.Spinbox(temp_frame, from_=-2.0, to=45.0, increment=0.1, bg="#141821", fg="#98c379", buttonbackground="#212631")
        self.temp_spin.pack(fill=tk.X, padx=5, pady=5)
        self.temp_spin.insert(0, "37.0")

        test_digit_btn = ttk.Button(temp_frame, text="⚡ TEST CODER QUANTIZATION", command=self.test_temperature_digitizer)
        test_digit_btn.pack(fill=tk.X, padx=5, pady=5)

        billing_frame = ttk.LabelFrame(left_panel, text=" billing synchronization ")
        billing_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Button(billing_frame, text="Log Simulative Activity Units", command=self.add_mock_charges).pack(fill=tk.X, padx=5, pady=5)
        
        self.sync_btn = ttk.Button(billing_frame, text="🔗 POST TO EPIC & RESET LEDGER", command=self.process_epic_upload_and_clear)
        self.sync_btn.pack(fill=tk.X, padx=5, pady=15)

        # Right Column: Displays
        ledger_frame = ttk.LabelFrame(right_panel, text=" active quickbooks queue ")
        ledger_frame.pack(fill=tk.X, height=220, pady=5)

        self.tree = ttk.Treeview(ledger_frame, columns=("code", "units", "rate", "subtotal"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col, head in [("code", "QB CODE IDENTIFIER"), ("units", "UNITS LOGGED"), ("rate", "UNIT RATE"), ("subtotal", "SUBTOTAL CHARGE")]:
            self.tree.heading(col, text=head, anchor=tk.W)
            self.tree.column(col, width=160)

        console_frame = ttk.LabelFrame(right_panel, text=" interface terminal transaction activity stream ")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console = tk.Text(console_frame, bg="#050608", fg="#abb2bf", font=("Courier", 10))
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Render first matrix configuration
        self.update_ledger_display_grid()

    # =====================================================================
    # GUI COMPONENT CONTROLLER INTERFACES
    # =====================================================================
    def push_log(self, text):
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.console.see(tk.END)

    def test_temperature_digitizer(self):
        try:
            t_input = float(self.temp_spin.get())
            w1 = self.core.digitize_vitals_to_word1(1.0, 1.0, t_input)
            _, _, t_output = self.core.reconstruct_word1_channels(w1)
            
            self.push_log(f"[DIGITIZER] Analog Temp: {t_input}°C -> Word 1 Bin Slot -> Restored Float: {t_output}°C")
        except ValueError:
            messagebox.showerror("Error", "Invalid temperature integer string value entered.")

    def add_mock_charges(self):
        for k in self.core.billing_catalog:
            self.core.billing_catalog[k]["units_consumed"] += random.randint(5, 20)
        self.update_ledger_display_grid()
        self.push_log("[BILLING] Simulative machine operations appended to QuickBooks queues.")

    def update_ledger_display_grid(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for _, data in self.core.billing_catalog.items():
            sub = data["units_consumed"] * data["unit_price"]
            self.tree.insert("", tk.END, values=(data["qb_code"], data["units_consumed"], f"${data['unit_price']:.2f}", f"${sub:.2f}"))

    def process_epic_upload_and_clear(self):
        # 1. Run serialization backing file update and flush counters inside core modules
        invoice = self.core.execute_epic_handshake_reset()
        
        # 2. Render output information blocks to screen display channels
self.push_log(f"[EPIC_HANDSHAKE] Transaction {invoice['transaction_id']} Upload Complete. Total Cleared: ${invoice['total_invoice_charge']:.2f}")
self.push_log(f"[JSON_BACKUP] Data payload safely backed up to {self.core.log_filename}")
self.push_log("[CLEANUP] QuickBooks tracking buffers reset to zero.")
# 3. Force ledger update loop to reflect zeroed data entries
self.update_ledger_display_grid()
messagebox.showinfo("Epic Interface Synced", f"Transaction {invoice['transaction_id']} successfully uploaded.\nLedger buffers cleared.")
if name == "main":
root = tk.Tk()
app = UnifiedSystemConsole(root)
root.mainloop()
