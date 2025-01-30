import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import compiled_processes

# Import the scheduling functions from your original code
def sjn_scheduling(processes):
    current_time = 0
    completed = []
    execution_log = []
    processes_copy = processes.copy()
    
    while len(completed) < len(processes):
        ready_queue = [p for p in processes_copy if p.arrival_time <= current_time and p not in completed]
        
        if ready_queue:
            next_process = min(ready_queue, key=lambda x: x.burst_time)
            start_time = current_time
            current_time += next_process.burst_time
            next_process.completion_time = current_time
            next_process.turnaround_time = next_process.completion_time - next_process.arrival_time
            next_process.waiting_time = next_process.turnaround_time - next_process.burst_time
            execution_log.append([next_process.pid, start_time, current_time])
            completed.append(next_process)
        else:
            current_time += 1
    
    return execution_log

def round_robin_scheduling(processes, time_quantum):
    current_time = 0
    execution_log = []
    processes.sort(key=lambda p: p.arrival_time)  # Sort by arrival time
    ready_queue = []
    remaining_processes = processes.copy()

    while remaining_processes or ready_queue:
        if ready_queue:  # Check if the ready queue is not empty
            current_process = ready_queue.pop(0)  # Get first process (FIFO)
            
            # Execute process for time quantum
            execution_time = min(time_quantum, current_process.remaining_time)
            current_time += execution_time
            current_process.remaining_time -= execution_time

            # Log execution
            execution_log.append([current_process.pid, current_time - execution_time, current_time])

            # Add newly arrived processes to the ready queue
            i = 0
            while i < len(remaining_processes):
                if remaining_processes[i].arrival_time <= current_time:
                    ready_queue.append(remaining_processes[i])
                    remaining_processes.pop(i)
                else:
                    i += 1

            # Requeue the process if it still has remaining time
            if current_process.remaining_time > 0:
                ready_queue.append(current_process)
            else:
                current_process.completion_time = current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
        else:
            # If ready queue is empty, move to the next arrival time
            current_time = remaining_processes[0].arrival_time
            ready_queue.append(remaining_processes.pop(0))

    return execution_log

def priority_scheduling(processes, preemptive=False):
    current_time = 0
    execution_log = []
    completed = 0
    
    # For tracking continuous process execution
    current_process = None
    start_time = 0
    
    while completed < len(processes):
        highest_priority_process = None
        for process in processes:
            if (process.arrival_time <= current_time and 
                (process.remaining_time if preemptive else process.completion_time == 0)):
                if highest_priority_process is None or process.priority < highest_priority_process.priority:
                    highest_priority_process = process
        
        if highest_priority_process:
            if preemptive:
                # If we have a process switch or first process
                if current_process != highest_priority_process:
                    # Log the previous process if it exists
                    if current_process is not None:
                        execution_log.append([current_process.pid, start_time, current_time])
                    # Start tracking new process
                    current_process = highest_priority_process
                    start_time = current_time
                
                highest_priority_process.remaining_time -= 1
                current_time += 1
                
                if highest_priority_process.remaining_time == 0:
                    # Log the completed process
                    execution_log.append([current_process.pid, start_time, current_time])
                    current_process = None
                    highest_priority_process.completion_time = current_time
                    highest_priority_process.turnaround_time = current_time - highest_priority_process.arrival_time
                    highest_priority_process.waiting_time = highest_priority_process.turnaround_time - highest_priority_process.burst_time
                    completed += 1
            else:
                execution_log.append([highest_priority_process.pid, current_time, 
                                   current_time + highest_priority_process.burst_time])
                current_time += highest_priority_process.burst_time
                highest_priority_process.completion_time = current_time
                highest_priority_process.turnaround_time = current_time - highest_priority_process.arrival_time
                highest_priority_process.waiting_time = highest_priority_process.turnaround_time - highest_priority_process.burst_time
                completed += 1
        else:
            current_time += 1
    
    # Handle the last process if it exists
    if current_process is not None and current_process.remaining_time == 0:
        execution_log.append([current_process.pid, start_time, current_time])
    
    return execution_log

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
        self.root.geometry("820x800")


        # change background color
        self.root.configure(bg="#A69CAC")
        
        # Variables
        self.processes: List[Process] = []
        self.current_pid = 0
        self.selected_algorithm = tk.StringVar(value="")
        self.time_quantum = tk.StringVar(value="3")
        
        self.create_widgets()
        
    def create_widgets(self):

        # Algorithm Selection Frame
        algo_frame = ttk.LabelFrame(self.root, text="Algorithm Selection", padding=10)
        algo_frame.pack(fill="x", padx=10, pady=5)
        
        algorithms = [
            ("Shortest Job Next", "SJN"),
            ("Round Robin", "RR"),
            ("Non-preemptive Priority", "NP"),
            ("Preemptive Priority", "PP")
        ]
        
        for text, value in algorithms:
            ttk.Radiobutton(
                algo_frame, 
                text=text,
                value=value,
                variable=self.selected_algorithm,
                command=self.on_algorithm_change
            ).pack(side="left", padx=5)
        
        style = ttk.Style()
        style.configure("TRadiobutton", font=('Helvetica', 14))
        
        # Time Quantum Frame (initially hidden)
        self.tq_frame = ttk.LabelFrame(self.root, text="Time Quantum", padding=10)
        ttk.Entry(self.tq_frame, textvariable=self.time_quantum, width=10).pack(side="left", padx=5)
        self.tq_frame.pack_forget()
        
        # Process Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Process Input", padding=5)
        input_frame.pack(fill="x", padx=10, pady=5, expand=False)
        
        # Input fields
        self.arrival_time = ttk.Entry(input_frame, width=10)
        self.burst_time = ttk.Entry(input_frame, width=10)
        self.priority = ttk.Entry(input_frame, width=10)
        
        ttk.Label(input_frame, text="Arrival Time:").grid(row=0, column=0, padx=5)
        self.arrival_time.grid(row=0, column=1, padx=5)
        ttk.Label(input_frame, text="Burst Time:").grid(row=0, column=2, padx=5)
        self.burst_time.grid(row=0, column=3, padx=5)
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=4, padx=5)
        self.priority.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="Add", command=self.add_process).grid(row=0, column=6, padx=(10,0))
        ttk.Button(input_frame, text="Remove", command=self.remove_process).grid(row=0, column=7, padx=0)
        ttk.Button(input_frame, text="Clear All", command=self.clear_all).grid(row=0, column=8, padx=0)
        ttk.Button(input_frame, text="Run", command=self.run_simulation).grid(row=0, column=9, padx=(20,10))

        # Process Table
        table_frame = ttk.LabelFrame(self.root, text="Processes", padding=10)
        table_frame.pack(fill="x", expand=True, padx=10, pady=5)

        # Create a frame with fixed height for the treeview
        tree_container = ttk.Frame(table_frame)  # Reduced height
        tree_container.pack(fill="x", expand=False)
        tree_container.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Treeview for processes
        columns = ("PID", "Arrival Time", "Burst Time", "Priority", 
                  "Completion Time", "Turnaround Time", "Waiting Time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Add scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        
        # Gantt Chart Frame
        self.gantt_frame = ttk.LabelFrame(self.root, text="Gantt Chart", padding=10)
        self.gantt_frame.pack(fill="x", padx=10, pady=5)
        # Create a frame to center the canvas
        chart_container = ttk.Frame(self.gantt_frame)
        chart_container.pack(fill="x", expand=True)
        
        self.gantt_canvas = tk.Canvas(chart_container, height=120, bg="white")
        gantt_scrollbar = ttk.Scrollbar(chart_container, orient="horizontal", command=self.gantt_canvas.xview)
        self.gantt_canvas.configure(xscrollcommand=gantt_scrollbar.set)
        self.gantt_canvas.pack(fill="x", expand=True, padx=10)
        gantt_scrollbar.pack(fill="x")

        # Custom font for metrics
        metrics_font = ('Helvetica', 15, 'bold')

        # Metrics Frame
        self.metrics_frame = ttk.LabelFrame(self.root, text="Performance Metrics", padding=10)
        self.metrics_frame.pack(fill="x", padx=10, pady=5)
        
        # Labels for metrics
        self.avg_tat_label = ttk.Label(self.metrics_frame, text="Average Turnaround Time: ", font=metrics_font)
        self.avg_tat_label.pack(anchor="w", padx=5, pady=2)
        
        self.avg_wt_label = ttk.Label(self.metrics_frame, text="Average Waiting Time: ", font=metrics_font)
        self.avg_wt_label.pack(anchor="w", padx=5, pady=2)

    def update_metrics(self, avg_tat, avg_wt):
        self.avg_tat_label.config(text=f"Average Turnaround Time: {avg_tat:.2f}")
        self.avg_wt_label.config(text=f"Average Waiting Time: {avg_wt:.2f}")
        
    def on_algorithm_change(self):
        if self.selected_algorithm.get() == "SJN":
            self.priority.config(state="disabled")
            self.tq_frame.pack_forget()
        elif self.selected_algorithm.get() == "RR":
            self.tq_frame.pack(fill="x", padx=10, pady=5, after=self.root.children["!labelframe"])
            self.priority.config(state="enabled")
        else:
            self.tq_frame.pack_forget()
            self.priority.config(state="normal" if self.selected_algorithm.get() in ["NP", "PP", "RR"] else "disabled")
    
    def add_process(self):
        try:
            arrival = int(self.arrival_time.get())
            burst = int(self.burst_time.get())
            priority = None if self.selected_algorithm.get() == "SJN" else int(self.priority.get())
            
            if arrival < 0 or burst <= 0 or (priority is not None and priority <= 0):
                raise ValueError("Invalid input values")
            
            process = Process(self.current_pid, arrival, burst, priority)
            self.processes.append(process)
            
            self.tree.insert("", "end", values=(
                process.pid, arrival, burst, 
                priority if priority is not None else "N/A",
                0, 0, 0
            ))
            
            self.current_pid += 1
            self.clear_inputs()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def clear_inputs(self):
        self.arrival_time.delete(0, "end")
        self.burst_time.delete(0, "end")
        self.priority.delete(0, "end")

    def remove_process(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            self.processes.pop(index)
            self.tree.delete(selected_item)
    
    def clear_all(self):
        self.processes.clear()
        self.current_pid = 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.gantt_canvas.delete("all")
    
    def update_table(self):
        for item in self.tree.get_children():
            process = next(p for p in self.processes if p.pid == self.tree.item(item)["values"][0])
            self.tree.item(item, values=(
                process.pid, process.arrival_time, process.burst_time,
                process.priority if process.priority is not None else "N/A",
                process.completion_time, process.turnaround_time, process.waiting_time
            ))
    
    def draw_gantt_chart(self, execution_log):
        self.gantt_canvas.delete("all")
        
        if not execution_log:
            return
            
        # Calculate dimensions
        canvas_width = self.gantt_canvas.winfo_width()
        canvas_height = self.gantt_canvas.winfo_height()
        total_time = execution_log[-1][2]  # End time of last process
        
        # Fixed block width calculation
        min_block_width = 50  # Minimum width for each time unit
        required_width = total_time * min_block_width
        scale_factor = min(1, canvas_width / required_width)
        block_width = min_block_width * scale_factor
        
        # Center the chart
        start_x = (canvas_width - (total_time * block_width)) / 2
        block_height = 40
        y_pos = canvas_height - 30
        y_top = y_pos - block_height
        
        # Draw timeline
        timeline_start = start_x
        timeline_end = start_x + (total_time * block_width)
        self.gantt_canvas.create_line(timeline_start, y_pos, timeline_end, y_pos, fill="black")
        
        # Draw process blocks
        for process_id, start_time, end_time in execution_log:
            x1 = start_x + (start_time * block_width)
            x2 = start_x + (end_time * block_width)
            
            # Draw block with border
            self.gantt_canvas.create_rectangle(x1, y_top, x2, y_pos, 
                                            fill="lightblue", outline="black")
            self.gantt_canvas.create_text((x1+x2)/2, (y_top+y_pos)/2, 
                                        text=process_id)
            
            # Draw time markers
            self.gantt_canvas.create_line(x1, y_pos, x1, y_pos+5)
            self.gantt_canvas.create_text(x1, y_pos+15, text=str(start_time))
        
        # Draw final time marker
        self.gantt_canvas.create_line(timeline_end, y_pos, timeline_end, y_pos+5)
        self.gantt_canvas.create_text(timeline_end, y_pos+15, text=str(total_time))
    
    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to simulate!")
            return
        
        # Reset process states
        for process in self.processes:
            process.remaining_time = process.burst_time
            process.completion_time = 0
            process.turnaround_time = 0
            process.waiting_time = 0
        
        algorithm = self.selected_algorithm.get()
        execution_log = []
        
        try:
            if algorithm == "SJN":
                execution_log = sjn_scheduling(self.processes)
            elif algorithm == "RR":
                time_quantum = int(self.time_quantum.get())
                if time_quantum <= 0:
                    raise ValueError("Time quantum must be positive")
                execution_log = round_robin_scheduling(self.processes, time_quantum)
            elif algorithm == "NP":
                execution_log = priority_scheduling(self.processes, preemptive=False)
            else:  # PP
                execution_log = priority_scheduling(self.processes, preemptive=True)
            
            self.update_table()
            self.draw_gantt_chart(execution_log)
            
            # Calculate and show metrics
            total_tat = sum(p.turnaround_time for p in self.processes)
            total_wt = sum(p.waiting_time for p in self.processes)
            avg_tat = total_tat / len(self.processes)
            avg_wt = total_wt / len(self.processes)

            self.update_metrics(avg_tat, avg_wt)
            
            #messagebox.showinfo("Results", 
               # f"Average Turnaround Time: {avg_tat:.2f}\n"
                #f"Average Waiting Time: {avg_wt:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")

def main():
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()