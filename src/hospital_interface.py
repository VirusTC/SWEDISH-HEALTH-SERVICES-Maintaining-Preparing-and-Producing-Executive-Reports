#!/usr/bin/env python3
"""
SWEDISH HEALTH SERVICES - UNIVAC-IX CORE INTERFACE NODES & STAFF GUI
Implements CODASYL-compliant DMS network nodes, MAPPER 4GL run-time buffers,
and a multi-panel terminal interface for clinical and administrative staff.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
import time

# =====================================================================
# 1. CORE UNIVAC-IX ENGINE NODES (DMS & MAPPER)
# =====================================================================

class DMSNetworkNode:
    """
    Manages CODASYL-compliant hierarchical network database structures.
    Maps unique patient records to sets of admissions, labs, and history.
    """
    def __init__(self):
        # Simulated database store matching hierarchical CODASYL sets
        self.records = {
            "P-1001": {
                "name": "Jane Doe",
                "admission": "Cherry Hill - ICU Bed 04",
                "lab_orders": "CBC, Metabolic Panel, Troponin",
                "pharmacy_history": "Heparin 5000 U, Metoprolol 25mg",
                "radiology_notes": "Chest X-Ray: Clear lung fields."
            },
            "P-1002": {
                "name": "John Smith",
                "admission": "Cherry Hill - MedSurg Room 312",
                "lab_orders": "Urinalysis, Blood Culture",
                "pharmacy_history": "Ceftriaxone 1g IV, Acetaminophen 650mg",
                "radiology_notes": "Abdominal CT: Acute appendicitis indicated."
            }
        }

    def fetch_record(self, patient_id):
        """Emulates a high-speed database read of a record node."""
        time.sleep(0.05) # Simulated mainframe disk drum latency
        return self.records.get(patient_id, None)

    def modify_record(self, patient_id, key, value):
        """Updates specific node schemas within the active set."""
        if patient_id in self.records:
            self.records[patient_id][key] = value
            return True
        return False


class MAPPERReportNode:
    """
    Simulates real-time 4GL data reporting loops.
    Dynamically monitors hospital allocations, surgical queues, and bed availability.
    """
    def __init__(self):
        pass

    def generate_bed_status_report(self):
        """Returns dynamic real-time resource allocations."""
        return [
            {"campus": "Cherry Hill", "unit": "ICU", "total": 20, "occupied": 18, "status": "CRITICAL"},
            {"campus": "Cherry Hill", "unit": "MedSurg", "total": 45, "occupied": 32, "status": "NOMINAL"},
            {"campus": "First Hill", "unit": "ER", "total": 30, "occupied": 29, "status": "CRITICAL"},
            {"campus": "Ballard", "unit": "Ortho", "total": 15, "occupied": 6, "status": "NOMINAL"}
        ]

    def generate_surgical_schedule(self):
        """Compiles real-time surgical theater allocations."""
        return [
            {"time": "08:00 AM", "OR": "OR-1", "procedure": "Cardiothoracic Bypass", "staff": "Dr. Weber"},
            {"time": "10:30 AM", "OR": "OR-3", "procedure": "Laparoscopic Appendectomy", "staff": "Dr. Grey"},
            {"time": "01:15 PM", "OR": "OR-2", "procedure": "Total Knee Arthroplasty", "staff": "Dr. Avery"}
        ]

# =====================================================================
# 2. STAFF STATION GRAPHICAL USER INTERFACE
# =====================================================================

class SwedishStaffStationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Swedish Health Services - Mainframe Terminal (UNIVAC-IX)")
        self.root.geometry("1100x700")
        
        # Initialize Backend Mainframe Engines
        self.dms_node = DMSNetworkNode()
        self.mapper_node = MAPPERReportNode()
        
        # Apply Styling Parameters
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1c1f26", foreground="#ffffff", fieldbackground="#282c34")
        self.style.configure("TNotebook", background="#1c1f26", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#2d3139", foreground="#a0a0a0", padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#007acc")], foreground=[("selected", "#ffffff")])
        self.style.configure("TLabelframe", background="#21252b", foreground="#61afef", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#21252b", foreground="#61afef", font=("Courier", 11, "bold"))
        self.style.configure("TButton", background="#3e4451", foreground="#ffffff", borderwidth=0, font=("Courier", 10))
        self.style.map("TButton", background=[("active", "#4b5263")])

        # Main Layout Container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Build Independent Functional Interfaces
        self.build_dms_patient_chart_tab()
        self.build_mapper_dashboard_tab()
        self.build_sys_telemetry_tab()

    def build_dms_patient_chart_tab(self):
        """Tab 1: CODASYL Database Management Structure (Patient Chart Interface)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" DMS Patient Records ")

        # Left Column: Lookup and Modifiers
        left_pane = ttk.Frame(tab, padding=10)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=350)

        search_frame = ttk.LabelFrame(left_pane, text=" record query ", padding=10)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Patient ID:", font=("Courier", 10)).pack(anchor=tk.W)
        self.patient_id_entry = tk.Entry(search_frame, bg="#282c34", fg="#98c379", insertbackground="white", font=("Courier", 12, "bold"))
        self.patient_id_entry.pack(fill=tk.X, pady=5)
        self.patient_id_entry.insert(0, "P-1001")

        search_btn = ttk.Button(search_frame, text="EXECUTE DMS FETCH", command=self.execute_dms_fetch)
        search_btn.pack(fill=tk.X, pady=5)

        update_frame = ttk.LabelFrame(left_pane, text=" record modifier ", padding=10)
        update_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(update_frame, text="Select Data Field:", font=("Courier", 10)).pack(anchor=tk.W)
        self.field_selector = ttk.Combobox(update_frame, values=["admission", "lab_orders", "pharmacy_history", "radiology_notes"], state="readonly")
        self.field_selector.pack(fill=tk.X, pady=5)
        self.field_selector.current(0)

        ttk.Label(update_frame, text="New Value Data Block:", font=("Courier", 10)).pack(anchor=tk.W)
        self.update_text = tk.Text(update_frame, bg="#282c34", fg="#abb2bf", insertbackground="white", height=8, font=("Courier", 10))
        self.update_text.pack(fill=tk.BOTH, expand=True, pady=5)

        update_btn = ttk.Button(update_frame, text="TRANSMIT UPDATE NODE", command=self.execute_dms_update)
        update_btn.pack(fill=tk.X, pady=5)

        # Right Column: Visual Console Display
        right_pane = ttk.LabelFrame(tab, text=" codasyl structural tree display ", padding=10)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=10)

        self.dms_console = tk.Text(right_pane, bg="#1e1e1e", fg="#61afef", font=("Courier", 11), wrap=tk.WORD)
        self.dms_console.pack(fill=tk.BOTH, expand=True)
        self.print_dms_console("System operational. Input Patient ID and execute fetch cycle.")

    def build_mapper_dashboard_tab(self):
        """Tab 2: Maintaining, Preparing, and Producing Executive Reports (MAPPER)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" MAPPER Executive Reports ")

        control_bar = ttk.Frame(tab, padding=5)
        control_bar.pack(fill=tk.X, side=tk.TOP)

        refresh_bed_btn = ttk.Button(control_bar, text="GENERATE BED ALLOCATIONS REPORT", command=self.load_mapper_beds)
        refresh_bed_btn.pack(side=tk.LEFT, padx=5, pady=5)

        refresh_surg_btn = ttk.Button(control_bar, text="GENERATE SURGICAL QUEUE LOGS", command=self.load_mapper_surgery)
        refresh_surg_btn.pack(side=tk.LEFT, padx=5, pady=5)

        display_frame = ttk.LabelFrame(tab, text=" 4gl output screen representation ", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.mapper_tree = ttk.Treeview(display_frame, columns=("c1", "c2", "c3", "c4", "c5"), show="headings")
        self.mapper_tree.pack(fill=tk.BOTH, expand=True)

    def build_sys_telemetry_tab(self):
        """Tab 3: Univac-IX Fabric Telemetry Monitoring Link"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Univac-IX Telemetry ")

        log_frame = ttk.LabelFrame(tab, text=" core fabric system logs ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sys_log = tk.Text(log_frame, bg="#121417", fg="#98c379", font=("Courier", 10))
        self.sys_log.pack(fill=tk.BOTH, expand=True)
        
        # Populate realistic system boot log entries
        self.sys_log.insert(tk.END, f"[{time.strftime('%X')}] UNIVAC-IX core baseline infrastructure link verified.\n")
        self.sys_log.insert(tk.END, f"[{time.strftime('%X')}] Trunk connection online at Swedish Cherry Hill Campus network switch.\n")
        self.sys_log.insert(tk.END, f"[{time.strftime('%X')}] Parallel multi-thread processing engines mapped natively via host processing grid.\n")
        self.sys_log.insert(tk.END, f"[{time.strftime('%X')}] Running diagnostics: 30-year chronological data block pipeline initialized.\n")
        self.sys_log.config(state=tk.DISABLED)

    # =====================================================================
    # INTERFACE ACTION CAPTURES
    # =====================================================================
    
    def print_dms_console(self, text):
self.dms_console.config(state=tk.NORMAL)
self.dms_console.delete('1.0', tk.END)
self.dms_console.insert(tk.END, text)
self.dms_console.config(state=tk.DISABLED)
def execute_dms_fetch(self):
pid = self.patient_id_entry.get().strip()
record = self.dms_node.fetch_record(pid)
if record:
formatted = (
f"CODASYL NODE RECORD MATCH DETECTED [{pid}]\n"
f"{'='*50}\n"
f"PATIENT SYSTEM NAME : {record['name']}\n"
f"ACTIVE ADMISSION    : {record['admission']}\n"
f"PHARMACEUTICAL LOGS : {record['pharmacy_history']}\n"
f"PENDING LAB ORDERS  : {record['lab_orders']}\n"
f"RADIOLOGY REPORTS   : {record['radiology_notes']}\n"
f"{'='*50}\n"
f"Node handshake status: 200 SUCCESS OK"
)
self.print_dms_console(formatted)
else:
self.print_dms_console(f"ERROR: Node record hash matching ID [{pid}] could not be found within database clusters.")
def execute_dms_update(self):
pid = self.patient_id_entry.get().strip()
field = self.field_selector.get()
new_val = self.update_text.get("1.0", tk.END).strip()
if not new_val:
messagebox.showwarning("Incomplete payload", "Update data payload block cannot pass null criteria values.")
return
success = self.dms_node.modify_record(pid, field, new_val)
if success:
messagebox.showinfo("Mainframe Sync", f"DMS node tree modified successfully for field entry: [{field}].")
self.execute_dms_fetch()
else:
messagebox.showerror("I/O Error", f"Target patient set context mapping [{pid}] failed synchronization constraints.")
def load_mapper_beds(self):
# Clear Treeview nodes
for item in self.mapper_tree.get_children():
self.mapper_tree.delete(item)
self.mapper_tree["columns"] = ("campus", "unit", "total", "occupied", "status")
for col in self.mapper_tree["columns"]:
self.mapper_tree.heading(col, text=col.upper(), anchor=tk.W)
self.mapper_tree.column(col, width=180)
records = self.mapper_node.generate_bed_status_report()
for r in records:
self.mapper_tree.insert("", tk.END, values=(r["campus"], r["unit"], r["total"], r["occupied"], r["status"]))
def load_mapper_surgery(self):
# Clear Treeview nodes
for item in self.mapper_tree.get_children():
self.mapper_tree.delete(item)
self.mapper_tree["columns"] = ("time", "or", "procedure", "staff")
for col in self.mapper_tree["columns"]:
self.mapper_tree.heading(col, text=col.upper(), anchor=tk.W)
self.mapper_tree.column(col, width=220)
records = self.mapper_node.generate_surgical_schedule()
for r in records:
self.mapper_tree.insert("", tk.END, values=(r["time"], r["OR"], r["procedure"], r["staff"]))
if name == "main":
root = tk.Tk()
app = SwedishStaffStationGUI(root)
root.mainloop()
