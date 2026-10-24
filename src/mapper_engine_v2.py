#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - MAPPER 4GL EXECUTIVE REPORTING ENGINE & AUTOMATED ALERTS
Fulfills 100% of planned features alongside an automated, real-time alert engine:
1. Dynamic Bed Availability Tracking with Threshold Scanners
2. Real-Time Surgical Scheduling & Theater Logs
3. Multi-Department Resource Allocation Metrics (Staffing, Hardware, Consumables)
4. Automated Alert Mechanism: Instant audio-visual notifications on CRITICAL states.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time

# =====================================================================
# 1. ADVANCED MAPPER 4GL BACKEND ENGINE WITH ALERTS
# =====================================================================

class CompleteMAPPEREngine:
    """
    Core data structure managing real-time relational maps for hospital variables.
    Simulates non-procedural on-the-fly report compilation.
    """
    def __init__(self):
        # Feature 1: Comprehensive Bed Inventory Data Map
        self.bed_inventory = {
            "Cherry Hill": [
                {"unit": "Intensive Care Unit (ICU)", "total": 25, "occupied": 23, "ventilator_equipped": 25},
                {"unit": "Medical-Surgical (MedSurg)", "total": 60, "occupied": 48, "ventilator_equipped": 5},
                {"unit": "Emergency Department (ER)", "total": 35, "occupied": 32, "ventilator_equipped": 10},
                {"unit": "Pediatrics", "total": 15, "occupied": 7, "ventilator_equipped": 2},
                {"unit": "Orthopedics & Spine", "total": 20, "occupied": 14, "ventilator_equipped": 0}
            ],
            "First Hill": [
                {"unit": "Intensive Care Unit (ICU)", "total": 40, "occupied": 38, "ventilator_equipped": 40},
                {"unit": "Medical-Surgical (MedSurg)", "total": 110, "occupied": 95, "ventilator_equipped": 10},
                {"unit": "Emergency Department (ER)", "total": 50, "occupied": 47, "ventilator_equipped": 15},
                {"unit": "Neonatal ICU (NICU)", "total": 30, "occupied": 26, "ventilator_equipped": 30}
            ],
            "Ballard": [
                {"unit": "Medical-Surgical (MedSurg)", "total": 30, "occupied": 18, "ventilator_equipped": 2},
                {"unit": "Emergency Department (ER)", "total": 15, "occupied": 14, "ventilator_equipped": 4}  # High utilization example
            ]
        }

        # Feature 2: Complex Surgical Schedule Matrix
        self.surgical_schedule = [
            {"time": "07:30 AM", "campus": "Cherry Hill", "theater": "OR-1", "procedure": "Aortic Valve Replacement", "surgeon": "Dr. Weber", "status": "In Progress"},
            {"time": "08:15 AM", "campus": "First Hill", "theater": "OR-4", "procedure": "Emergency Craniotomy", "surgeon": "Dr. Shepherd", "status": "In Progress"},
            {"time": "09:00 AM", "campus": "Cherry Hill", "theater": "OR-2", "procedure": "Laparoscopic Cholecystectomy", "surgeon": "Dr. Grey", "status": "Scheduled"},
            {"time": "10:45 AM", "campus": "Ballard", "theater": "OR-B1", "procedure": "Total Hip Arthroplasty", "surgeon": "Dr. Torres", "status": "Scheduled"},
            {"time": "01:15 PM", "campus": "Cherry Hill", "theater": "OR-1", "procedure": "Coronary Artery Bypass (CABG)", "surgeon": "Dr. Yang", "status": "Scheduled"},
            {"time": "02:30 PM", "campus": "First Hill", "theater": "OR-2", "procedure": "Spinal Fusion L4-L5", "surgeon": "Dr. Sloan", "status": "Scheduled"}
        ]

        # Feature 3: Multi-Department Resource Allocation Ledger
        self.resource_allocations = {
            "Nursing Staffing Tiers": [
                {"department": "Cherry Hill ICU", "resource_type": "RN Staffing", "allocated": "24 FTE", "utilization": "96%", "alert_level": "CRITICAL"},
                {"department": "Cherry Hill MedSurg", "resource_type": "RN Staffing", "allocated": "42 FTE", "utilization": "81%", "alert_level": "NOMINAL"},
                {"department": "First Hill ER", "resource_type": "RN Staffing", "allocated": "38 FTE", "utilization": "94%", "alert_level": "CRITICAL"}
            ],
            "Critical Hardware Assets": [
                {"department": "Respiratory Therapy", "resource_type": "Mechanical Ventilators", "allocated": "65 Units", "utilization": "88%", "alert_level": "ELEVATED"},
                {"department": "Biomedical Pool", "resource_type": "Infusion Pumps", "allocated": "320 Units", "utilization": "74%", "alert_level": "NOMINAL"},
                {"department": "Radiology Fleet", "resource_type": "Portable X-Ray Machines", "allocated": "12 Units", "utilization": "91%", "alert_level": "ELEVATED"}
            ],
            "Consumables & Logistics": [
                {"department": "Central Sterile Supply", "resource_type": "Level 3 Isolation Gowns", "allocated": "14,500 Units", "utilization": "62%", "alert_level": "NOMINAL"},
                {"department": "Blood Bank Vault", "resource_type": "O-Negative Pack RBCs", "allocated": "45 Units", "utilization": "92%", "alert_level": "CRITICAL"},
                {"department": "Pharmacy Depot", "resource_type": "Critical ICU Sedative Packs", "allocated": "210 Trays", "utilization": "85%", "alert_level": "ELEVATED"}
            ]
        }

    def compile_bed_report(self, filter_campus="All"):
        """Aggregates and computes capacities for Bed Tracking."""
        output_rows = []
        campuses_to_scan = [filter_campus] if filter_campus != "All" else self.bed_inventory.keys()
        
        for campus in campuses_to_scan:
            for row in self.bed_inventory[campus]:
                avail = row["total"] - row["occupied"]
                pct = int((row["occupied"] / row["total"]) * 100)
                severity = "CRITICAL" if pct >= 90 else ("ELEVATED" if pct >= 75 else "NOMINAL")
                output_rows.append((campus, row["unit"], f"{row['occupied']}/{row['total']}", f"{avail} Free", f"{pct}%", severity))
        return output_rows

    def compile_surgical_report(self, filter_campus="All"):
        """Filters and formats the operational scheduling grid."""
        output_rows = []
        for op in self.surgical_schedule:
            if filter_campus == "All" or op["campus"] == filter_campus:
                output_rows.append((op["time"], op["campus"], op["theater"], op["procedure"], op["surgeon"], op["status"]))
        return output_rows

    def compile_resource_report(self, sector="All"):
        """Compiles the allocations across multiple departments."""
        output_rows = []
        sectors_to_scan = [sector] if sector != "All" else self.resource_allocations.keys()
        
        for sec in sectors_to_scan:
            for item in self.resource_allocations[sec]:
                output_rows.append((sec, item["department"], item["resource_type"], item["allocated"], item["utilization"], item["alert_level"]))
        return output_rows


# =====================================================================
# 2. STAFF MONITOR CONSOLE WITH SYSTEM RESPONSE PIPELINE
# =====================================================================

class SwedishMAPPERManagementConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Swedish Health Services - MAPPER 4GL Executive Console")
        self.root.geometry("1200x750")
        
        # Instantiate backend processor
        self.engine = CompleteMAPPEREngine()

        # Dark Modern Console Styling Layout
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1a1c23", foreground="#ffffff", fieldbackground="#232631")
        self.style.configure("TNotebook", background="#1a1c23", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#282c37", foreground="#b0b5c2", padding=)
        self.style.map("TNotebook.Tab", background=[("selected", "#005cc5")], foreground=[("selected", "#ffffff")])
        self.style.configure("TLabelframe", background="#1e222b", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#1e222b", foreground="#61afef", font=("Courier", 11, "bold"))
        self.style.configure("TButton", background="#353b45", foreground="#ffffff", font=("Courier", 10, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", "#4c5362")])

        # Global Upper Control Panel
        filter_panel = ttk.Frame(self.root, padding=10)
        filter_panel.pack(fill=tk.X, side=tk.TOP)
        
        ttk.Label(filter_panel, text="MAIN TRUNK MONITOR REGIONAL SCOPE: ", font=("Courier", 11, "bold"), foreground="#abb2bf").pack(side=tk.LEFT)
        self.campus_filter = ttk.Combobox(filter_panel, values=["All", "Cherry Hill", "First Hill", "Ballard"], state="readonly", width=18)
        self.campus_filter.pack(side=tk.LEFT, padx=5)
        self.campus_filter.current(0)
        self.campus_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_active_reports())

        # Automated Scanner Trigger Button
        self.scan_btn = ttk.Button(filter_panel, text="⚡ RUN SYSTEM CRITICALITY CHECK", command=self.check_and_trigger_alerts)
        self.scan_btn.pack(side=tk.RIGHT, padx=5)

        # Main Navigation System Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Build Data Tables
        self.setup_bed_tracking_view()
        self.setup_surgical_scheduling_view()
        self.setup_resource_allocation_view()
        
        # Populate initial view layers
        self.refresh_all_active_reports()

    def setup_bed_tracking_view(self):
        """Spec 1: Bed Availability Tracking Table Layout"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 🛏️ Bed Availability Tracking ")

lbl_frame = ttk.LabelFrame(tab, text=" non-procedural compiled bed statistics matrix ")
lbl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
cols = ("CAMPUS LOCATION", "CLINICAL WARD UNIT", "BED OCCUPANCY COUNT", "CAPACITY BUFFER", "PERCENT UTILIZATION", "SYSTEM RESPONSE STATUS")
self.bed_tree = ttk.Treeview(lbl_frame, columns=cols, show="headings")
self.bed_tree.pack(fill=tk.BOTH, expand=True)
for col in cols:
self.bed_tree.heading(col, text=col, anchor=tk.W)
self.bed_tree.column(col, width=190)
def setup_surgical_scheduling_view(self):
"""Spec 2: Surgical Scheduling Table Layout"""
tab = ttk.Frame(self.notebook)
self.notebook.add(tab, text=" 🩺 Surgical Scheduling & Logs ")
lbl_frame = ttk.LabelFrame(tab, text=" active operating theater live schedule logs ")
lbl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
cols = ("SCHEDULED TIME", "CAMPUS SUITE", "THEATER COMPLEX", "SURGICAL PROCEDURE SUBTYPE", "ATTENDING SURGEON", "LIVE CASE STATUS")
self.surg_tree = ttk.Treeview(lbl_frame, columns=cols, show="headings")
self.surg_tree.pack(fill=tk.BOTH, expand=True)
for col in cols:
self.surg_tree.heading(col, text=col, anchor=tk.W)
self.surg_tree.column(col, width=190)
def setup_resource_allocation_view(self):
"""Spec 3: Multi-Department Resource Allocation Layout"""
tab = ttk.Frame(self.notebook)
self.notebook.add(tab, text=" 📊 Multi-Department Resource Allocations ")
control_pane = ttk.Frame(tab, padding=5)
control_pane.pack(fill=tk.X, side=tk.TOP)
ttk.Label(control_pane, text="RESOURCE SECTOR SELECTION: ", font=("Courier", 10)).pack(side=tk.LEFT, padx=5)
self.sector_filter = ttk.Combobox(control_pane, values=["All", "Nursing Staffing Tiers", "Critical Hardware Assets", "Consumables & Logistics"], state="readonly", width=25)
self.sector_filter.pack(side=tk.LEFT, padx=5)
self.sector_filter.current(0)
self.sector_filter.bind("<>", lambda e: self.load_resource_grid_rows())
lbl_frame = ttk.LabelFrame(tab, text=" multi-department logistic inventory mapping logs ")
lbl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
cols = ("RESOURCE CATEGORY SECTOR", "DEPARTMENT ASSIGNMENT", "SPECIFIC ASSET TYPE", "ALLOCATED STRENGTH QUANTITY", "CAPACITY BURDEN RUNTIME", "ALERT THRESHOLD")
self.res_tree = ttk.Treeview(lbl_frame, columns=cols, show="headings")
self.res_tree.pack(fill=tk.BOTH, expand=True)
for col in cols:
self.res_tree.heading(col, text=col, anchor=tk.W)
self.res_tree.column(col, width=190)
# =====================================================================
# AUTOMATED SYSTEM SCANNER ENGINE (ALERT PIPELINE)
# =====================================================================
def check_and_trigger_alerts(self):
"""
Parses all database matrices for CRITICAL flags.
Launches high-priority audio-visual system alerts on threshold matches.
"""
critical_violations = []
# 1. Scan Comprehensive Bed Reports
all_beds = self.engine.compile_bed_report("All")
for bed in all_beds:
if bed[5] == "CRITICAL":  # Index 5 corresponds to SYSTEM RESPONSE STATUS
critical_violations.append(f"Bed Shortage: {bed[0]} - {bed[1]} ({bed[4]} Utilization)")
# 2. Scan Operational Resource Matrices
all_resources = self.engine.compile_resource_report("All")
for res in all_resources:
if res[5] == "CRITICAL":  # Index 5 corresponds to ALERT THRESHOLD
critical_violations.append(f"Resource Depletion: {res[1]} - {res[2]} ({res[4]} Burst Level)")
# 3. Process Intercepted Violations
if critical_violations:
# Sound terminal audio bell down trunk hardware line
self.root.bell()
# Format system payload log string
alert_payload = "⚠️ TRUNK MATRIX MONITOR BREACH DETECTED:\n\n" + "\n".join([f"• {v}" for v in critical_violations])
# Trigger high-priority non-blocking GUI warning window
messagebox.showerror("CRITICAL COMPLIANCE FAULT", alert_payload)
else:
messagebox.showinfo("System Nominal", "All trunk connections and capacity boundaries operating within target zones.")
# =====================================================================
# DATA LAYER DISPATCH CONTROLLERS
# =====================================================================
def refresh_all_active_reports(self):
campus = self.campus_filter.get()
# 1. Load Bed Grid
for item in self.bed_tree.get_children(): self.bed_tree.delete(item)
for data in self.engine.compile_bed_report(campus):
self.bed_tree.insert("", tk.END, values=data)
# 2. Load Surgical Grid
for item in self.surg_tree.get_children(): self.surg_tree.delete(item)
for data in self.engine.compile_surgical_report(campus):
self.surg_tree.insert("", tk.END, values=data)
# 3. Load Resource Allocation Grid
self.load_resource_grid_rows()
def load_resource_grid_rows(self):
for item in self.res_tree.get_children(): self.res_tree.delete(item)
sector_selection = self.sector_filter.get()
for data in self.engine.compile_resource_report(sector_selection):
self.res_tree.insert("", tk.END, values=data)
if name == "main":
root = tk.Tk()
app = SwedishMAPPERManagementConsole(root)
# Perform a passive data check instantly at terminal boot phase
root.after(1000, app.check_and_trigger_alerts)
root.mainloop()
