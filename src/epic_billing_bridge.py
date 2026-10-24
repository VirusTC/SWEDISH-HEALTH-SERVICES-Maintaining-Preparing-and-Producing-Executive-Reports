#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - EPIC BILLING & QUICKBOOKS CODING BRIDGE
Fulfills financial infrastructure capabilities:
1. Automated runtime cost tracking across legacy and modern software nodes.
2. Staff-adjustable unit price fields for dynamic financial modifications.
3. Automated conversion to QuickBooks item codes (e.g., QB-UNIVAC-TRUNK).
4. Outbound JSON payload compiler configured for Epic Billing ingestion pipelines.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json

# =====================================================================
# 1. CORE FINANCIAL MAPPING & SERIALIZATION ENGINE
# =====================================================================

class EpicQuickBooksCostEngine:
    def __init__(self):
        # QuickBooks Service/Item Code Mapping Schema
        self.billing_catalog = {
            "TRUNK_POLL": {
                "qb_code": "QB-UNIVAC-TRUNK",
                "description": "UNIVAC-IX Core Trunk Line Active Telemetry Monitoring",
                "unit": "60s Cycle",
                "unit_price": 0.05,  # Staff can modify this in the GUI
                "units_consumed": 0
            },
            "CUBIC_COMPUTE": {
                "qb_code": "QB-MAPPER-POLY",
                "description": "MAPPER 4GL Cubic Regression Risk Calculation Execution",
                "unit": "Compute Pass",
                "unit_price": 0.02,
                "units_consumed": 0
            },
            "ANALOG_QUANT": {
                "qb_code": "QB-ICU-QUANT",
                "description": "Analog Chart Recorder 12-Bit Quantization Mapping Loop",
                "unit": "Hour",
                "unit_price": 1.50,
                "units_consumed": 0
            }
        }

    def increment_usage(self, service_key, amount=1):
        """Passively accrues resource consumption counters during background execution."""
        if service_key in self.billing_catalog:
            self.billing_catalog[service_key]["units_consumed"] += amount

    def calculate_running_costs(self):
        """Computes subtotal matrix balances across all active system nodes."""
        grand_total = 0.0
        itemized_report = []
        
        for key, data in self.billing_catalog.items():
            cost = data["units_consumed"] * data["unit_price"]
            grand_total += cost
            itemized_report.append({
                "item_key": key,
                "qb_code": data["qb_code"],
                "description": data["description"],
                "units": data["units_consumed"],
                "unit": data["unit"],
                "unit_price": data["unit_price"],
                "total_cost": round(cost, 2)
            })
            
        return round(grand_total, 2), itemized_report

    def compile_epic_billing_payload(self):
        """Formats active balances into a standardized JSON payload structure for Epic."""
        grand_total, itemized = self.calculate_running_costs()
        
        epic_payload = {
            "epic_transaction_id": f"TX-SWED-OMS-{int(time.time())}",
            "transmission_timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "clearing_house_source": "SWEDISH-CHERRY-HILL-CAMPUS",
            "accounting_ledger_type": "QUICKBOOKS_MAPPED_CHARGE",
            "total_invoice_charge": grand_total,
            "line_items": itemized
        }
        return epic_payload


# =====================================================================
# 2. GRAPHICAL MANAGEMENT CONSOLE
# =====================================================================

class EpicBillingBridgeConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Sperry/Sterling OMS - Epic Financial Billing Bridge")
        self.root.geometry("1200x700")

        # Instantiate financial processor
        self.cost_engine = EpicQuickBooksCostEngine()
        self.is_transmitting = False

        # Apply Console Terminal Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#0e1014", foreground="#ffffff", fieldbackground="#15181f")
        self.style.configure("TLabelframe", background="#11141a", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#11141a", foreground="#61afef", font=("Courier", 10, "bold"))
        self.style.configure("TButton", background="#21252b", foreground="#ffffff", font=("Courier", 9, "bold"))

        # Main Layout Configuration Panels
        left_pane = ttk.Frame(self.root, padding=10)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=420)

        right_pane = ttk.Frame(self.root, padding=10)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Column: Unit Price Override Controls
        price_frame = ttk.LabelFrame(left_pane, text=" unit price configurations ")
        price_frame.pack(fill=tk.X, pady=5)

        ttk.Label(price_frame, text="Select Target Service Component:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.service_selector = ttk.Combobox(price_frame, values=list(self.cost_engine.billing_catalog.keys()), state="readonly")
        self.service_selector.pack(fill=tk.X, padx=5, pady=5)
        self.service_selector.current(0)
        self.service_selector.bind("<<ComboboxSelected>>", lambda e: self.load_selected_price_to_ui())

        ttk.Label(price_frame, text="Adjust Active Unit Price ($):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.price_spin = tk.Spinbox(price_frame, from_=0.01, to=100.0, increment=0.01, bg="#15181f", fg="#98c379", buttonbackground="#21252b")
        self.price_spin.pack(fill=tk.X, padx=5, pady=5)

        commit_price_btn = ttk.Button(price_frame, text="⚡ COMMIT FINANCIAL RATE ADJUSTMENT", command=self.save_price_modification)
        commit_price_btn.pack(fill=tk.X, padx=5, pady=10)

        # Simulation Tool Parameters
        sim_frame = ttk.LabelFrame(left_pane, text=" system activity simulator tools ")
        sim_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Button(sim_frame, text="Simulate Trunk Polling Activity (+10 Cycles)", command=lambda: self.inject_mock_usage("TRUNK_POLL", 10)).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sim_frame, text="Simulate Dynamic Calculation Runs (+50 Passes)", command=lambda: self.inject_mock_usage("CUBIC_COMPUTE", 50)).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sim_frame, text="Simulate ICU Bed Quantization (+4 Hours)", command=lambda: self.inject_mock_usage("ANALOG_QUANT", 4)).pack(fill=tk.X, padx=5, pady=5)

        self.transmit_btn = ttk.Button(sim_frame, text="▶ START INTERFACE TRANSMISSION INTERCEPT", command=self.toggle_epic_upload_stream)
        self.transmit_btn.pack(fill=tk.X, padx=5, pady=15)

        # Right Column Top: Live QuickBooks ledger display grid
        ledger_lbl = ttk.LabelFrame(right_pane, text=" running quickbooks mapped cost ledger ")
        ledger_lbl.pack(fill=tk.X, height=250, pady=5)

        cols = ("QUICKBOOKS CODE", "DESCRIPTION UNIT TYPE", "UNITS LOGGED", "UNIT RATE", "ACCERUED COST")
        self.tree = ttk.Treeview(ledger_lbl, columns=cols, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=140)

        # Right Column Bottom: Live Epic outbound transmission log stream
        epic_lbl = ttk.LabelFrame(right_pane, text=" epic hl7 / billing transaction outbound pipeline ")
        epic_lbl.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console = tk.Text(epic_lbl, bg="#06080a", fg="#61afef", font=("Courier", 10))
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Populate baseline outputs
        self.load_selected_price_to_ui()
        self.refresh_billing_display_grid()

    # =====================================================================
    # ENGINE CONTROLLER CORES
    # =====================================================================

    def load_selected_price_to_ui(self):
        key = self.service_selector.get()
        current_rate = self.cost_engine.billing_catalog[key]["unit_price"]
        self.price_spin.delete(0, "end")
        self.price_spin.insert(0, f"{current_rate:.2f}")

    def save_price_modification(self):
        key = self.service_selector.get()
        try:
            new_rate = round(float(self.price_spin.get()), 2)
            self.cost_engine.billing_catalog[key]["unit_price"] = new_rate
            self.refresh_billing_display_grid()
            
            ts = time.strftime("%H:%M:%S")
            self.console.insert(tk.END, f"[{ts}] [CONFIG_CHANGE] Modified unit rate for {key} to ${new_rate:.2f}/{self.cost_engine.billing_catalog[key]['unit']}\n")
            self.console.see(tk.END)
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid floating point value submitted for component billing rate.")

    def inject_mock_usage(self, service_key, amount):
        self.cost_engine.increment_usage(service_key, amount)
        self.refresh_billing_display_grid()

    def refresh_billing_display_grid(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        _, itemized_list = self.cost_engine.calculate_running_costs()
        
        for row in itemized_list:
            self.tree.insert("", tk.END, values=(
                row["qb_code"], row["description"], row["units"],
                f"${row['unit_price']:.2f}", f"${row['total_cost']:.2f}"
            ))

    def toggle_epic_upload_stream(self):
        if not self.is_transmitting:
            self.is_transmitting = True
            self.transmit_btn.config(text="■ STOP EPIC PIPELINE STREAM")
            self.execute_scheduled_epic_upload_pass()
else:
self.is_transmitting = False
self.transmit_btn.config(text="▶ START INTERFACE TRANSMISSION INTERCEPT")
def execute_scheduled_epic_upload_pass(self):
if not self.is_transmitting: return
# Compile and generate standard Epic outbound billing schema data payload
payload = self.cost_engine.compile_epic_billing_payload()
ts = time.strftime("%H:%M:%S")
self.console.insert(tk.END, f"[{ts}] [EPIC_UPLOAD] Transmitting Transaction: {payload['epic_transaction_id']}\n")
self.console.insert(tk.END, json.dumps(payload, indent=2) + "\n")
self.console.insert(tk.END, "-" * 70 + "\n")
self.console.see(tk.END)
# Schedule next automatic background sync loop interval (simulating live background posting)
self.root.after(5000, self.execute_scheduled_epic_upload_pass)
if name == "main":
root = tk.Tk()
app = EpicBillingBridgeConsole(root)
root.mainloop()
