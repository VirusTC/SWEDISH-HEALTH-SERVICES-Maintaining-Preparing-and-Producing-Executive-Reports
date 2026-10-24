#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - SPERRY/STERLING OMS PREDICTIVE INVENTORY CORE
Integrates cubic polynomial progression models for predictive asset scaling.
Includes an automated 60-second background polling loop and cause-and-effect telemetry.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math

# =====================================================================
# 1. PREDICTIVE MATH ENGINE & EXTENDED DATA MATRIX
# =====================================================================

class PredictiveOMSDatabase:
    """
    Expanded memory database tracking cause-and-effect relationships
    for automated hospital inventory replenishment.
    """
    def __init__(self):
        # Extended database layout: items track use-rates, expiration speeds, and dynamic burn indices (D)
        self.inventory_nodes = {
            "INV-O-NEG": {
                "name": "O-Negative Packed RBCs",
                "stock_level": 45,
                "expiration_days": 35,
                "burn_index_D": 65.0,  # Dynamic usage scale (1-100)
                "cause_effect_log": "High emergency room intake driving consumption."
            },
            "INV-VENT-KIT": {
                "name": "Mechanical Ventilator Cassettes",
                "stock_level": 65,
                "expiration_days": 365,
                "burn_index_D": 40.0,
                "cause_effect_log": "Respiratory seasonal tracking within nominal boundaries."
            },
            "INV-ICU-SED": {
                "name": "Critical ICU Sedative Packs",
                "stock_level": 210,
                "expiration_days": 180,
                "burn_index_D": 78.0,
                "cause_effect_log": "Surgical theater expansions causing accelerated depletion."
            }
        }

    def calculate_predictive_target(self, D):
        """
        Applies the repository's cubic polynomial progression algorithm
        to determine the optimal replenishment order target (P).
        """
        try:
            P = (50 * (D**3) + 5065 * (D**2) + 168324 * D + 843000) / 600
            return round(P)
        except Exception:
            return 0

    def run_newton_raphson_adjustment(self, current_P):
        """
        Inverse solver: uses the Newton-Raphson root-finding loop to calculate
        the exact underlying system friction index D based on incoming order targets.
        """
        D_n = 50.0  # Initial guess midpoint
        tolerance = 0.001
        max_iterations = 20
        
        for _ in range(max_iterations):
            # Function: f(D) - P = 0
            f_D = 0.08333 * (D_n**3) + 8.44167 * (D_n**2) + 280.54 * D_n + 1405 - current_P
            # Derivative: f'(D)
            f_prime_D = 0.25 * (D_n**2) + 16.8833 * D_n + 280.54
            
            if abs(f_prime_D) < 1e-5:
                break
                
            D_next = D_n - (f_D / f_prime_D)
            if abs(D_next - D_n) < tolerance:
                return round(D_next, 2)
            D_n = D_next
        return round(D_n, 2)


# =====================================================================
# 2. STAFF WORKSTATION & RUNTIME CONSOLE
# =====================================================================

class OMSPredictiveConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Sperry/Sterling OMS - Autonomous Predictive Terminal")
        self.root.geometry("1150x700")

        # Initialize Backend Node Layer
        self.db = PredictiveOMSDatabase()
        self.is_looping = False

        # Apply Console Styling Parameters
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#14171c", foreground="#ffffff", fieldbackground="#1d212a")
        self.style.configure("TLabelframe", background="#1a1d24", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#1a1d24", foreground="#61afef", font=("Courier", 11, "bold"))
        self.style.configure("TButton", background="#2c313c", foreground="#ffffff", font=("Courier", 10, "bold"))
        
        # Primary Workspace Layout Split
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=400)
        
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Panel: Automation Settings and Typer Simulation
        loop_frame = ttk.LabelFrame(left_panel, text=" background execution engine ")
        loop_frame.pack(fill=tk.X, pady=5)

        self.toggle_btn = ttk.Button(loop_frame, text="▶ START 60s REPLENISHMENT LOOP", command=self.toggle_background_loop)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=10)

        self.loop_status_lbl = ttk.Label(loop_frame, text="Status: IDLE (Manual Checks Enforced)", foreground="#e06c75", font=("Courier", 9, "bold"))
        self.loop_status_lbl.pack(pady=5)

        typer_frame = ttk.LabelFrame(left_panel, text=" active terminal typer input ")
        typer_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(typer_frame, text="Select Target Supply Node:", font=("Courier", 10)).pack(anchor=tk.W, padx=5, pady=2)
        self.node_selector = ttk.Combobox(typer_frame, values=list(self.db.inventory_nodes.keys()), state="readonly")
        self.node_selector.pack(fill=tk.X, padx=5, pady=5)
        self.node_selector.current(0)
        self.node_selector.bind("<<ComboboxSelected>>", lambda e: self.load_node_to_inputs())

        ttk.Label(typer_frame, text="Modify System Burn Index (D):", font=("Courier", 10)).pack(anchor=tk.W, padx=5, pady=2)
        self.burn_slider = ttk.Scale(typer_frame, from_=1.0, to=100.0, command=self.on_slider_adjustment)
        self.burn_slider.pack(fill=tk.X, padx=5, pady=5)

        self.slider_val_lbl = ttk.Label(typer_frame, text="Current D: 50.0", font=("Courier", 10, "bold"), foreground="#98c379")
        self.slider_val_lbl.pack(pady=2)

        ttk.Label(typer_frame, text="Cause and Effect Relationship Parameter:", font=("Courier", 10)).pack(anchor=tk.W, padx=5, pady=2)
        self.cause_text = tk.Text(typer_frame, bg="#1d212a", fg="#abb2bf", height=5, font=("Courier", 10), insertbackground="white")
        self.cause_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        save_node_btn = ttk.Button(typer_frame, text="💾 COMMIT NODE RELATIONSHIP", command=self.commit_node_changes)
        save_node_btn.pack(fill=tk.X, padx=5, pady=10)

        # Right Panel: Live Ledger and Telemetry Stream
        ledger_frame = ttk.LabelFrame(right_panel, text=" extended dms inventory prediction ledger ")
        ledger_frame.pack(fill=tk.X, height=280, pady=5)

        cols = ("NODE ID", "ASSET DESCRIPTION", "STOCK", "BURN INDEX (D)", "PREDICTED ORDER REQ (P)")
        self.tree = ttk.Treeview(ledger_frame, columns=cols, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=140)

        telemetry_frame = ttk.LabelFrame(right_panel, text=" edwards fireworks external telemetry pipeline ")
        telemetry_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console_output = tk.Text(telemetry_frame, bg="#0f1115", fg="#5c6370", font=("Courier", 10))
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Load initial values
        self.load_node_to_inputs()
        self.refresh_ledger_display()

    # =====================================================================
    # ENGINE CONTROLLER LOGIC
    # =====================================================================

    def log_telemetry(self, message):
        """Streams operational warning updates to the text window."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.console_output.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console_output.see(tk.END)

    def load_node_to_inputs(self):
        node_id = self.node_selector.get()
        node = self.db.inventory_nodes[node_id]
        self.burn_slider.set(node["burn_index_D"])
        self.slider_val_lbl.config(text=f"Current D: {node['burn_index_D']}")
        self.cause_text.delete("1.0", tk.END)
        self.cause_text.insert(tk.END, node["cause_effect_log"])

    def on_slider_adjustment(self, val):
        self.slider_val_lbl.config(text=f"Current D: {round(float(val), 2)}")

    def commit_node_changes(self):
        node_id = self.node_selector.get()
        new_D = round(float(self.burn_slider.get()), 2)
        new_cause = self.cause_text.get("1.0", tk.END).strip()
        
        self.db.inventory_nodes[node_id]["burn_index_D"] = new_D
        self.db.inventory_nodes[node_id]["cause_effect_log"] = new_cause
        
        self.log_telemetry(f"Typer write complete: Update node {node_id} relationship profiles.")
        self.refresh_ledger_display()
        self.evaluate_critical_thresholds()

    def refresh_ledger_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for node_id, data in self.db.inventory_nodes.items():
            predicted_P = self.db.calculate_predictive_target(data["burn_index_D"])
            self.tree.insert("", tk.END, values=(node_id, data["name"], data["stock_level"], data["burn_index_D"], predicted_P))

    def evaluate_critical_thresholds(self):
        """Scans database records and routes exceptions to the Edwards Fireworks telemetry line."""
        for node_id, data in self.db.inventory_nodes.items():
            predicted_P = self.db.calculate_predictive_target(data["burn_index_D"])
            
            # If our cubic progression flags an aggressive order spike, flag as CRITICAL
            if predicted_P > 1500:
