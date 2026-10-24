#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - MODERNIZED REAL-TIME ICU PROCESS CONTROL & HELP SYSTEM
Integrates continuous physiological acquisition, non-linear cubic stress modeling,
and high-priority clinical decision support hardware interrupts.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import random

# =====================================================================
# 1. CORE REAL-TIME ACQUISITION & PHYSIOLOGICAL PREDICTION ENGINE
# =====================================================================

class ModernizedHELPSystem:
    """
    Modernized MEDLAB/HELP system executing continuous multi-parameter telemetry analysis
    and rule-based clinical decision support scoring.
    """
    def __init__(self):
        # Current Active Monitoring Parameters + Future Expandable Slots
        self.patient_matrix = {
            "BED-01 (ICU)": {
                "patient_name": "Patient Alpha (Post-Op Cardiac)",
                "heart_rate_bpm": 74.0,
                "mean_arterial_pressure_mmhg": 85.0,
                "core_temp_c": 37.2,
                "chest_tube_drainage_ml_hr": 15.0,
                "fluid_hydration_bal_ml": +120,
                # Future-proof placeholder slots for new biometric machines/sensors
                "future_sensor_alpha_raw": 0.0,
                "future_sensor_beta_raw": 0.0,
                "base_vitals_friction_D": 35.0
            },
            "BED-02 (ICU)": {
                "patient_name": "Patient Beta (Trauma Triage)",
                "heart_rate_bpm": 118.0,              # Tachycardia event
                "mean_arterial_pressure_mmhg": 58.0,   # Hypotension event
                "core_temp_c": 38.9,                  # Pyrexia event
                "chest_tube_drainage_ml_hr": 180.0,   # Hemorrhage event
                "fluid_hydration_bal_ml": -450,
                "future_sensor_alpha_raw": 0.0,
                "future_sensor_beta_raw": 0.0,
                "base_vitals_friction_D": 82.0        # High physiological restriction
            }
        }

    def compute_systemic_strain(self, bed_id):
        """
        Executes the cubic progression algorithm to transform multiple raw vitals variables
        into a singular continuous Systemic Strain Output (P_s).
        """
        pt = self.patient_matrix[bed_id]
        D_base = pt["base_vitals_friction_D"]

        # Clinical Decision Support Rule Adjustments (HELP Engine)
        modifier = 1.0
        # Rule 1: Shock Index Assessment (HR / SBP)
        if pt["heart_rate_bpm"] > 100.0 and pt["mean_arterial_pressure_mmhg"] < 70.0:
            modifier *= 1.5  # Escalate baseline restriction calculation due to hypovolemic trends
            
        # Rule 2: Chest Tube Excess Output Track
        if pt["chest_tube_drainage_ml_hr"] > 100.0:
            modifier *= 1.3  # Scale for active internal blood loss profiles

        D_effective = min(D_base * modifier, 100.0)

        # Run core continuous polynomial calculation loop
        try:
            P_s = (50 * (D_effective**3) + 5065 * (D_effective**2) + 168324 * D_effective + 843000) / 600
            return round(P_s), round(D_effective, 2)
        except Exception:
            return 0, D_base


# =====================================================================
# 2. RUNTIME WORKSTATION AND SYSTEM INTERRUPT MANAGER
# =====================================================================

class ModernICUConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Swedish Health Services - Modernized Process Control ICU Central")
        self.root.geometry("1300x750")

        self.engine = ModernizedHELPSystem()
        self.active_monitoring = False

        # Apply Console Custom Layout Styles
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

        # Left Grid: Core Controls and Telemetry Override Typer
        ctrl_frame = ttk.LabelFrame(left_pane, text=" process control core ")
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.toggle_btn = ttk.Button(ctrl_frame, text="▶ ENGAGE LIVE REAL-TIME TELEMETRY SCAN", command=self.toggle_telemetry_stream)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=10)

        self.status_lbl = ttk.Label(ctrl_frame, text="Status: CHERRY HILL ARCHITECTURE IDLE", foreground="#e06c75", font=("Courier", 9, "bold"))
        self.status_lbl.pack(pady=2)

        override_frame = ttk.LabelFrame(left_pane, text=" bedside telemetry modifiers ")
        override_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(override_frame, text="Select Target Patient Bed Node:", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.bed_selector = ttk.Combobox(override_frame, values=list(self.engine.patient_matrix.keys()), state="readonly")
        self.bed_selector.pack(fill=tk.X, padx=5, pady=2)
        self.bed_selector.current(0)
        self.bed_selector.bind("<<ComboboxSelected>>", lambda e: self.load_bed_vitals_to_ui())

        # Vitals Signal Entry Boxes
        ttk.Label(override_frame, text="Heart Rate Signal (BPM):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.hr_spin = tk.Spinbox(override_frame, from_=30, to=220, increment=1, bg="#161920", fg="#abb2bf", buttonbackground="#21252b", command=self.commit_ui_changes_to_matrix)
        self.hr_spin.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(override_frame, text="Mean Arterial Pressure (mmHg):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.map_spin = tk.Spinbox(override_frame, from_=30, to=180, increment=1, bg="#161920", fg="#abb2bf", buttonbackground="#21252b", command=self.commit_ui_changes_to_matrix)
        self.map_spin.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(override_frame, text="Chest Tube Drainage Stream (mL/hr):", font=("Courier", 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.drain_spin = tk.Spinbox(override_frame, from_=0, to=1000, increment=5, bg="#161920", fg="#abb2bf", buttonbackground="#21252b", command=self.commit_ui_changes_to_matrix)
        self.drain_spin.pack(fill=tk.X, padx=5, pady=2)

        # Future-Proof Custom Machine Interface Slots
        ttk.Label(override_frame, text="Future Modular Machine Integration Slot A (Raw V):", font=("Courier", 9), foreground="#5c6370").pack(anchor=tk.W, padx=5, pady=2)
        self.future_a_spin = tk.Spinbox(override_frame, from_=0, to=5, increment=0.01, bg="#161920", fg="#5c6370", state="disabled")
        self.future_a_spin.pack(fill=tk.X, padx=5, pady=2)

        update_btn = ttk.Button(override_frame, text="💾 FORCE TRANSMIT BIOMETRIC PAYLOAD", command=self.force_manual_payload_transmission)
        update_btn.pack(fill=tk.X, padx=5, pady=10)

        # Right Grid: Live Tracking Grid and Interrupt Console
        ledger_frame = ttk.LabelFrame(right_pane, text=" centralized processes telemetry monitor ")
        ledger_frame.pack(fill=tk.X, height=280, pady=5)

        cols = ("BED ID", "PATIENT ID IDENTIFIER", "HEART RATE", "MAP PRESS", "DRAINAGE", "INDEX D_p", "STRESS P_s")
        self.tree = ttk.Treeview(ledger_frame, columns=cols, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=120)

        interrupt_frame = ttk.LabelFrame(right_pane, text=" direct hardware interrupt log array ")
        interrupt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console = tk.Text(interrupt_frame, bg="#05070a", fg="#98c379", font=("Courier", 10))
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Hydrate active configurations
        self.load_bed_vitals_to_ui()
        self.refresh_central_display_grid()

    # =====================================================================
    # HARDWARE INTERRUPT AND CLINICAL CONTROL SYSTEM INTERACTION
    # =====================================================================

    def push_interrupt_alert(self, level, payload_text):
        """Simulates forcing a vector hardware interrupt to override baseline processor time."""
        ts = time.strftime("%H:%M:%S")
        formatted = f"[{ts}] >>> SYSTEM VECTOR INTERRUPT {level} <<< {payload_text}\n"
        self.console.insert(tk.END, formatted)
        self.console.see(tk.END)

    def load_bed_vitals_to_ui(self):
        bed_id = self.bed_selector.get()
        pt = self.engine.patient_matrix[bed_id]
        
        self.hr_spin.delete(0, "end"); self.hr_spin.insert(0, str(int(pt["heart_rate_bpm"])))
        self.map_spin.delete(0, "end"); self.map_spin.insert(0, str(int(pt["mean_arterial_pressure_mmhg"])))
        self.drain_spin.delete(0, "end"); self.drain_spin.insert(0, str(int(pt["chest_tube_drainage_ml_hr"])))

    def commit_ui_changes_to_matrix(self):
        """Passively synchronizes working UI modifications to memory."""
        bid = self.bed_selector.get()
        try:
            self.engine.patient_matrix[bid]["heart_rate_bpm"] = float(self.hr_spin.get())
            self.engine.patient_matrix[bid]["mean_arterial_pressure_mmhg"] = float(self.map_spin.get())
self.engine.patient_matrix[bid]["chest_tube_drainage_ml_hr"] = float(self.drain_spin.get())
except ValueError:
return
def force_manual_payload_transmission(self):
self.commit_ui_changes_to_matrix()
self.refresh_central_display_grid()
self.execute_hardware_interrupt_scan()
def refresh_central_display_grid(self):
for item in self.tree.get_children(): self.tree.delete(item)
for bid, data in self.engine.patient_matrix.items():
P_s, D_eff = self.engine.compute_systemic_strain(bid)
self.tree.insert("", tk.END, values=(
bid, data["patient_name"], f"{int(data['heart_rate_bpm'])} bpm",
f"{int(data['mean_arterial_pressure_mmhg'])} mmHg", f"{int(data['chest_tube_drainage_ml_hr'])} mL/hr",
D_eff, P_s
))
def execute_hardware_interrupt_scan(self):
"""
Parses all patient data blocks against continuous polynomial limits.
If constraints cross critical boundaries, it trips immediate vector interrupts.
"""
for bid, data in self.engine.patient_matrix.items():
P_s, D_eff = self.engine.compute_systemic_strain(bid)
# Clinical Decision Support Threshold Breach Trigger
if P_s > 1500:
self.root.bell()
alert_text = f"CRITICAL PHYSIOLOGICAL STRESS FAULT at {bid} ({data['patient_name']}). Output P_s: {P_s}. Forcing telemetry override line routing to intensive care desk."
self.push_interrupt_alert("0x02 (PRIORITY_CRITICAL_VITAL)", alert_text)
elif data["chest_tube_drainage_ml_hr"] > 150.0:
self.root.bell()
alert_text = f"HEMORRHAGIC FLOW EXCEPTION at {bid}. Output Volume: {data['chest_tube_drainage_ml_hr']} mL/hr. Initializing immediate blood bank core routing request."
self.push_interrupt_alert("0x05 (HEMODYNAMIC_DRAIN_SURGE)", alert_text)
# =====================================================================
# LIVE POLLING AUTOMATION LOOPS
# =====================================================================
def toggle_telemetry_stream(self):
if not self.active_monitoring:
self.active_monitoring = True
self.toggle_btn.config(text="■ HALT INDUSTRIAL POLLING MATRIX")
self.status_lbl.config(text="Status: REAL-TIME ACQUISITION CHANNELS ACTIVE", foreground="#98c379")
self.push_interrupt_alert("0x00 (SYS_BOOT)", "Real-time automated diagnostic scans engaged across Swedish clinical architecture lines.")
self.run_automated_polling_pass()
else:
self.active_monitoring = False
self.toggle_btn.config(text="▶ ENGAGE LIVE REAL-TIME TELEMETRY SCAN")
self.status_lbl.config(text="Status: CHERRY HILL ARCHITECTURE IDLE", foreground="#e06c75")
self.push_interrupt_alert("0x01 (SYS_SHUTDOWN)", "Continuous physiological scanner unlatched from trunk connections.")
def run_automated_polling_pass(self):
if not self.active_monitoring: return
# Simulate subtle physiological signal oscillations over time
for bid in self.engine.patient_matrix:
# Add small random fluctuation to simulate life telemetry stream inputs
self.engine.patient_matrix[bid]["heart_rate_bpm"] += random.choice([-1.0, 0.0, 1.0])
self.engine.patient_matrix[bid]["heart_rate_bpm"] = max(40.0, min(self.engine.patient_matrix[bid]["heart_rate_bpm"], 200.0))
self.refresh_central_display_grid()
self.execute_hardware_interrupt_scan()
# Continuous scheduling iteration latch set to cycle real-time evaluations
self.root.after(2000, self.run_automated_polling_pass)
if name == "main":
root = tk.Tk()
app = ModernICUConsole(root)
root.mainloop()
