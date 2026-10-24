#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - SPERRY/STERLING PREDICTIVE OMS CORE (v4.0)
Fulfills advanced analytical graphing metrics:
1. Multi-Line Real-Time Graphing (Plots all inventory nodes simultaneously)
2. Translucent Safety Boundary Shading (Highlights temperatures > 6.0°C in light red)
3. Dynamic Node State Trackers (Color-coded indicator rings for active system states)
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import math

# Import Matplotlib libraries for embedded UI layout operations
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =====================================================================
# 1. ADVANCED DATA STRUCTURE WITH ENVIRONMENTAL SENSORS
# =====================================================================

class PredictiveOMSDatabaseV4:
    def __init__(self):
        # Extended database layout with cold-chain, latency, and hardware constraints
        self.inventory_nodes = {
            "INV-O-NEG": {
                "name": "O-Negative Packed RBCs",
                "stock_level": 45,
                "burn_index_D": 65.0,
                "fridge_temp_c": 4.2,        # Target: 1.0C - 6.0C
                "shipping_latency_days": 2,  # Baseline: 2 days
                "cause_effect_log": "High emergency room intake driving consumption.",
                "color_hex": "#ff6b6b"       # Crimson marker
            },
            "INV-VENT-KIT": {
                "name": "Mechanical Ventilator Cassettes",
                "stock_level": 65,
                "burn_index_D": 40.0,
                "fridge_temp_c": 21.5,       # Room temp storage nominal
                "shipping_latency_days": 5,  # Baseline: 5 days
                "cause_effect_log": "Respiratory seasonal tracking within nominal boundaries.",
                "color_hex": "#4dadf7"       # Electric Blue marker
            },
            "INV-ICU-SED": {
                "name": "Critical ICU Sedative Packs",
                "stock_level": 210,
                "burn_index_D": 78.0,
                "fridge_temp_c": 3.8,        # Cold storage required
                "shipping_latency_days": 3,  # Baseline: 3 days
                "cause_effect_log": "Surgical theater expansions causing accelerated depletion.",
                "color_hex": "#cc5de8"       # Violet marker
            }
        }

    def calculate_predictive_target(self, node_id, custom_temp=None, custom_latency=None):
        """
        Applies cubic progression algorithms adjusted for cold-chain 
        temperature spikes and shipping delivery latencies.
        """
        node = self.inventory_nodes[node_id]
        D_base = node["burn_index_D"]
        
        temp_val = custom_temp if custom_temp is not None else node["fridge_temp_c"]
        latency_val = custom_latency if custom_latency is not None else node["shipping_latency_days"]

        # Environmental Modifier Calculations
        temp_modifier = 1.0
        if node_id == "INV-O-NEG":
            if temp_val > 6.0 or temp_val < 1.0:
                temp_modifier = 1.4
        elif node_id == "INV-ICU-SED":
            if temp_val > 8.0:
                temp_modifier = 1.2

        # Latency Scaling
        latency_factor = 1.0
        if node_id == "INV-O-NEG" and latency_val > 2:
            latency_factor = latency_val / 2.0

        D_effective = min(D_base * temp_modifier * latency_factor, 100.0)

        # Run core continuous polynomial calculation loop
        try:
            P = (50 * (D_effective**3) + 5065 * (D_effective**2) + 168324 * D_effective + 843000) / 600
            return round(P), round(D_effective, 2)
        except Exception:
            return 0, D_base


# =====================================================================
# 2. RUNTIME WORKSTATION CONSOLE WITH MULTI-LINE OVERLAYS
# =====================================================================

class MultiLineGraphingConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Sperry/Sterling OMS - Continuous Multi-Line Analytics Console (v4.0)")
        self.root.geometry("1350x850")

        self.db = PredictiveOMSDatabaseV4()
        self.is_looping = False

        # Apply Visual Theme Parameters
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#11141a", foreground="#ffffff", fieldbackground="#1b1e26")
        self.style.configure("TLabelframe", background="#171a21", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#171a21", foreground="#61afef", font=("Courier", 10, "bold"))
        self.style.configure("TButton", background="#2a2e38", foreground="#ffffff", font=("Courier", 9, "bold"))

        # Main Workspace Splits
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=420)
        
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Controls Block
        control_frame = ttk.LabelFrame(left_panel, text=" operational automated engine ")
        control_frame.pack(fill=tk.X, pady=5)

        self.toggle_btn = ttk.Button(control_frame, text="▶ START 60s REPLENISHMENT LOOP", command=self.toggle_loop)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=10)

        self.status_lbl = ttk.Label(control_frame, text="Status: MANUAL OVERRIDE", foreground="#e06c75", font=("Courier", 9, "bold"))
        self.status_lbl.pack(pady=2)

        editor_frame = ttk.LabelFrame(left_panel, text=" sensor telemetry overrides ")
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(editor_frame, text="Select Focus Inventory Node:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.node_selector = ttk.Combobox(editor_frame, values=list(self.db.inventory_nodes.keys()), state="readonly")
        self.node_selector.pack(fill=tk.X, padx=5, pady=2)
        self.node_selector.current(0)
        self.node_selector.bind("<<ComboboxSelected>>", lambda e: self.load_node_telemetry())

        ttk.Label(editor_frame, text="Refrigeration Temperature (°C):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.temp_spin = tk.Spinbox(editor_frame, from_=-10.0, to=40.0, increment=0.1, bg="#1b1e26", fg="#98c379", buttonbackground="#2a2e38", command=self.update_multi_graph)
        self.temp_spin.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(editor_frame, text="Transit Latency Burden (Days):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.latency_spin = tk.Spinbox(editor_frame, from_=1, to=30, increment=1, bg="#1b1e26", fg="#98c379", buttonbackground="#2a2e38", command=self.update_multi_graph)
        self.latency_spin.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(editor_frame, text="Narrative Cause/Effect Vector:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.cause_text = tk.Text(editor_frame, bg="#1b1e26", fg="#abb2bf", height=4, font=("Courier", 10), insertbackground="white")
        self.cause_text.pack(fill=tk.X, padx=5, pady=2)

        commit_btn = ttk.Button(editor_frame, text="💾 COMMIT NODE AND TELEMETRY LOGS", command=self.save_node_telemetry)
        commit_btn.pack(fill=tk.X, padx=5, pady=10)

        # Right Panel Top: Live Multi-Line Analytical Graph with Shading Bounds
        graph_lbl = ttk.LabelFrame(right_panel, text=" integrated multi-department order load metrics ")
        graph_lbl.pack(fill=tk.BOTH, expand=True, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(6, 4.2), facecolor="#171a21")
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_lbl)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right Panel Bottom: Output Grid Ledger
        ledger_lbl = ttk.LabelFrame(right_panel, text=" telemetry log ledger ")
        ledger_lbl.pack(fill=tk.X, height=180, pady=5)

        cols = ("NODE ID", "ASSET TYPE", "TEMP (°C)", "LATENCY", "EFFECTIVE INDEX D", "ORDER RESP P")
        self.tree = ttk.Treeview(ledger_lbl, columns=cols, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=120)

        # Hydrate system displays
        self.load_node_telemetry()
        self.refresh_display_grid()

    # =====================================================================
    # MULTI-LINE ANALYSIS & OVERLAY GENERATOR
    # =====================================================================

    def load_node_telemetry(self):
        node = self.db.inventory_nodes[self.node_selector.get()]
        self.temp_spin.delete(0, "end")
        self.temp_spin.insert(0, str(node["fridge_temp_c"]))
        self.latency_spin.delete(0, "end")
        self.latency_spin.insert(0, str(node["shipping_latency_days"]))
        self.cause_text.delete("1.0", tk.END)
        self.cause_text.insert(tk.END, node["cause_effect_log"])
        self.update_multi_graph()

    def update_multi_graph(self):
        """Plots all inventory trajectory loops in parallel and overlays cold-chain alerts."""
        focus_nid = self.node_selector.get()
        
        try:
            focus_temp = float(self.temp_spin.get())
            focus_lat = int(self.latency_spin.get())
        except ValueError:
            return

        # Clear active graphic frame context
        self.ax.clear()
        self.ax.set_facecolor("#1b1e26")
        
        # Define sweep array baseline across standard refrigeration limits (-5C to +35C)
        temp_sweep = [x * 0.5 for x in range(-10, 71)]

        # Plot structural lines for each individual inventory node concurrently
for nid, data in self.db.inventory_nodes.items():
orders_y = []
for t in temp_sweep:
# If checking the active user modified node, use live input adjustments
if nid == focus_nid:
P, _ = self.db.calculate_predictive_target(nid, custom_temp=t, custom_latency=focus_lat)
else:
P, _ = self.db.calculate_predictive_target(nid, custom_temp=t)
orders_y.append(P)
# Draw line vector using the node's specific tracking color signature
self.ax.plot(temp_sweep, orders_y, color=data["color_hex"], linewidth=1.5, linestyle="--", label=f"{nid} Profile")
# Plot coordinate anchor rings for every active asset state
if nid == focus_nid:
act_P, _ = self.db.calculate_predictive_target(nid, custom_temp=focus_temp, custom_latency=focus_lat)
self.ax.plot(focus_temp, act_P, marker="o", markersize=9, color="#98c379", markeredgecolor="#ffffff", label="Modified Working Node")
else:
act_P, _ = self.db.calculate_predictive_target(nid)
self.ax.plot(data["fridge_temp_c"], act_P, marker="s", markersize=6, color=data["color_hex"])
# Feature 2 Overlay: Apply Translucent Shading for Critical Spoilage Zones (> 6.0C)
self.ax.axvspan(6.0, 35.0, color="#e06c75", alpha=0.15, label="Cold-Chain Violation Zone (>6.0°C)")
# Layout parameters, font configs, and legends
self.ax.set_title("Multi-Department Stock Response Matrix & Critical Boundary Overlays", color="#ffffff", fontname="Courier", fontsize=10, weight="bold")
self.ax.set_xlabel("Refrigeration Temperature Telemetry (°C)", color="#abb2bf", fontname="Courier", fontsize=9)
self.ax.set_ylabel("Cubic Replenishment Order Output (P)", color="#abb2bf", fontname="Courier", fontsize=9)
self.ax.set_xlim(-5.0, 32.0)
self.ax.tick_params(colors="#abb2bf", labelsize=8)
self.ax.grid(True, color="#2c313c", linestyle=":", linewidth=0.5)
self.ax.legend(facecolor="#171a21", edgecolor="#2c313c", labelcolor="#ffffff", loc="upper left", fontsize=8)
# Flush frame buffer update straight to terminal panel window
self.fig.tight_layout()
self.canvas.draw()
def save_node_telemetry(self):
nid = self.node_selector.get()
self.db.inventory_nodes[nid]["fridge_temp_c"] = round(float(self.temp_spin.get()), 2)
self.db.inventory_nodes[nid]["shipping_latency_days"] = int(self.latency_spin.get())
self.db.inventory_nodes[nid]["cause_effect_log"] = self.cause_text.get("1.0", tk.END).strip()
self.refresh_display_grid()
self.update_multi_graph()
def refresh_display_grid(self):
for item in self.tree.get_children(): self.tree.delete(item)
for nid, data in self.db.inventory_nodes.items():
P, D_eff = self.db.calculate_predictive_target(nid)
self.tree.insert("", tk.END, values=(nid, data["name"], f"{data['fridge_temp_c']}°C", f"{data['shipping_latency_days']}d", D_eff, P))
def toggle_loop(self):
if not self.is_looping:
self.is_looping = True
self.toggle_btn.config(text="■ HALT INDUSTRIAL POLLING MATRIX")
self.status_lbl.config(text="Status: BACKGROUND DAEMON ACTIVE", foreground="#98c379")
self.execute_scheduled_pass()
else:
self.is_looping = False
self.toggle_btn.config(text="▶ START 60s REPLENISHMENT LOOP")
self.status_lbl.config(text="Status: MANUAL OVERRIDE", foreground="#e06c75")
def execute_scheduled_pass(self):
if not self.is_looping: return
self.db.export_telemetry_to_json()
self.root.after(60000, self.execute_scheduled_pass)
if name == "main":
root = tk.Tk()
app = MultiLineGraphingConsole(root)
root.mainloop()
