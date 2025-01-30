import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = f"P{pid}"
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("800x600")
        
        # Variables
        self.algorithm = tk.StringVar(value="SJN")
        self.time_quantum = tk.StringVar(value="2")
        self.processes: List[Process] = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Algorithm Selection Frame
        algo_frame = ttk.LabelFrame(self.root, text="Algorithm Selection", padding=10)
        algo_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Radiobutton(algo_frame, text="Shortest Job Next (SJN)", 
                       variable=self.algorithm, value="SJN").pack(side="left", padx=5)
        ttk.Radiobutton(algo_frame, text="Round Robin (RR)", 
                       variable=self.algorithm, value="RR").pack(side="left", padx=5)
        ttk.Radiobutton(algo_frame, text="Non-preemptive Priority", 
                       variable=self.algorithm, value="NP").pack(side="left", padx=5)
        ttk.Radiobutton(algo_frame, text="Preemptive Priority", 
                       variable=self.algorithm, value="PP").pack(side="left", padx=5)
        
        # Time Quantum Frame (for RR)
        self.tq_frame = ttk.LabelFrame(self.root, text="Time Quantum", padding=10)
        ttk.Label(self.tq_frame, text="Time Quantum:").pack(side="left", padx=5)
        ttk.Entry(self.tq_frame, textvariable=self.time_quantum, width=10).pack(side="left", padx=5)
        
        # Process Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Process Input", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Process Table
        self.tree = ttk.Treeview(input_frame, columns=("PID", "Arrival", "Burst", "Priority"), 
                                show="headings", height=5)
        self.tree.heading("PID", text="Process ID")
        self.tree.heading("Arrival", text="Arrival Time")
        self.tree.heading("Burst", text="Burst Time")
        self.tree.heading("Priority", text="Priority")
        self.tree.pack(fill="x", pady=5)
        
        # Input Fields
        input_fields = ttk.Frame(input_frame)
        input_fields.pack(fill="x", pady=5)
        
        self.arrival_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        
        ttk.Label(input_fields, text="Arrival Time:").pack(side="left", padx=5)
        ttk.Entry(input_fields, textvariable=self.arrival_var, width=10).pack(side="left", padx=5)
        ttk.Label(input_fields, text="Burst Time:").pack(side="left", padx=5)
        ttk.Entry(input_fields, textvariable=self.burst_var, width=10).pack(side="left", padx=5)
        ttk.Label(input_fields, text="Priority:").pack(side="left", padx=5)
        ttk.Entry(input_fields, textvariable=self.priority_var, width=10).pack(side="left", padx=5)
        
        ttk.Button(input_fields, text="Add Process", command=self.add_process).pack(side="left", padx=5)
        ttk.Button(input_fields, text="Remove Selected", command=self.remove_process).pack(side="left", padx=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Results Table
        self.results_tree = ttk.Treeview(results_frame, 
                                       columns=("PID", "Arrival", "Burst", "Priority", 
                                              "Completion", "Turnaround", "Waiting"),
                                       show="headings", height=5)
        self.results_tree.heading("PID", text="Process ID")
        self.results_tree.heading("Arrival", text="Arrival Time")
        self.results_tree.heading("Burst", text="Burst Time")
        self.results_tree.heading("Priority", text="Priority")
        self.results_tree.heading("Completion", text="Completion Time")
        self.results_tree.heading("Turnaround", text="Turnaround Time")
        self.results_tree.heading("Waiting", text="Waiting Time")
        self.results_tree.pack(fill="both", expand=True, pady=5)
        
        # Gantt Chart Canvas
        self.canvas = tk.Canvas(results_frame, height=100, bg="white")
        self.canvas.pack(fill="x", pady=5)
        
        # Average Metrics
        self.metrics_label = ttk.Label(results_frame, text="")
        self.metrics_label.pack(pady=5)
        
        # Run Button
        ttk.Button(self.root, text="Run Simulation", 
                  command=self.run_simulation).pack(pady=10)
        
        # Update Time Quantum visibility based on algorithm
        self.algorithm.trace("w", self.update_time_quantum_visibility)
        self.update_time_quantum_visibility()
        
    def update_time_quantum_visibility(self, *args):
        if self.algorithm.get() == "RR":
            self.tq_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.tq_frame.pack_forget()
    
    def add_process(self):
        try:
            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get()) if self.priority_var.get() else None
            
            if arrival < 0 or burst <= 0 or (priority is not None and priority <= 0):
                raise ValueError("Invalid input values")
            
            pid = len(self.processes)
            process = Process(pid, arrival, burst, priority)
            self.processes.append(process)
            
            self.tree.insert("", "end", values=(process.pid, arrival, burst, 
                                               priority if priority is not None else "N/A"))
            
            # Clear input fields
            self.arrival_var.set("")
            self.burst_var.set("")
            self.priority_var.set("")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def remove_process(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            self.processes.pop(index)
            self.tree.delete(selected_item)
    
    def draw_gantt_chart(self, execution_log):
        self.canvas.delete("all")
        
        if not execution_log:
            return
        
        # Calculate dimensions
        chart_width = self.canvas.winfo_width() - 20
        chart_height = 60
        start_x = 10
        start_y = 20
        
        total_time = execution_log[-1][2]  # End time of last process
        time_unit_width = chart_width / total_time
        
        # Draw processes
        colors = ["#FFB6C1", "#98FB98", "#87CEFA", "#DDA0DD", "#F0E68C", 
                 "#E6E6FA", "#20B2AA", "#FFA07A", "#66CDAA", "#BA55D3"]
        
        for i, (pid, start_time, end_time) in enumerate(execution_log):
            x1 = start_x + (start_time * time_unit_width)
            x2 = start_x + (end_time * time_unit_width)
            
            # Draw process block
            color = colors[int(pid[1]) % len(colors)]
            self.canvas.create_rectangle(x1, start_y, x2, start_y + chart_height, 
                                      fill=color, outline="black")
            
            # Draw process label
            label_x = (x1 + x2) / 2
            self.canvas.create_text(label_x, start_y + chart_height/2, text=pid)
            
            # Draw time label
            self.canvas.create_text(x1, start_y + chart_height + 10, 
                                  text=str(start_time), anchor="w")
        
        # Draw final time label
        self.canvas.create_text(start_x + chart_width, start_y + chart_height + 10,
                              text=str(total_time), anchor="e")
    
    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add some processes first")
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Create copy of processes for simulation
        processes = copy.deepcopy(self.processes)
        
        # Run selected algorithm
        algorithm = self.algorithm.get()
        if algorithm == "SJN":
            execution_log = sjn_scheduling(processes)
        elif algorithm == "RR":
            try:
                time_quantum = int(self.time_quantum.get())
                if time_quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid time quantum")
                return
            execution_log = round_robin_scheduling(processes, time_quantum)
        elif algorithm == "NP":
            execution_log = priority_scheduling(processes, preemptive=False)
        else:  # PP
            execution_log = priority_scheduling(processes, preemptive=True)
        
        # Update results table
        for process in processes:
            self.results_tree.insert("", "end", values=(
                process.pid, process.arrival_time, process.burst_time,
                process.priority if process.priority is not None else "N/A",
                process.completion_time, process.turnaround_time, process.waiting_time
            ))
        
        # Draw Gantt chart
        self.draw_gantt_chart(execution_log)
        
        # Calculate and display metrics
        total_tat = sum(p.turnaround_time for p in processes)
        total_wt = sum(p.waiting_time for p in processes)
        avg_tat = total_tat / len(processes)
        avg_wt = total_wt / len(processes)
        
        self.metrics_label.config(text=f"Average Turnaround Time: {avg_tat:.2f} | "
                                     f"Average Waiting Time: {avg_wt:.2f}")

def main():
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()