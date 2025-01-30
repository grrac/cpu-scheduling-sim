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

def print_table(processes):
    # Define what data to show for each column
    def get_value(process, column):
        return {
            "Process": process.pid,
            "Arrival Time": process.arrival_time,
            "Burst Time": process.burst_time,
            "Priority": process.priority if process.priority is not None else "N/A",
            "Completion Time": process.completion_time,
            "Turnaround Time": process.turnaround_time,
            "Waiting Time": process.waiting_time
        }[column]

    # Determine which columns to show
    header = ["Process", "Arrival Time", "Burst Time"]
    if any(p.priority is not None for p in processes):
        header.append("Priority")
    if any(p.completion_time != 0 for p in processes):
        header.extend(["Completion Time", "Turnaround Time", "Waiting Time"])
    
    # Calculate column widths
    widths = []
    for column in header:
        column_values = [len(str(get_value(p, column))) for p in processes]
        widths.append(max(len(column), max(column_values)))
    
    # Print header
    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(separator)
    print("|" + "|".join(f" {h.center(w)} " for h, w in zip(header, widths)) + "|")
    print(separator)
    
    # Print processes
    for p in processes:
        row = [str(get_value(p, column)) for column in header]
        print("|" + "|".join(f" {val.center(w)} " for val, w in zip(row, widths)) + "|")
    print(separator)

def print_gantt_chart(execution_log):
    print("\nGantt Chart:")
    
    # Print the top border
    border = "+" + "+".join("-" * 6 for _ in execution_log) + "+"
    print(border)
    
    # Print process names
    for entry in execution_log:
        print(f"|  {entry[0]}  ", end="")
    print("|")
    
    # Print bottom border
    print(border)
    
    # Print time markers
    print(f"{execution_log[0][1]:<3}", end="")
    for entry in execution_log:
        print(f"{entry[2]:<6}", end="")
    print()

def calculate_metrics(processes):
    total_tat = sum(p.turnaround_time for p in processes)
    total_wt = sum(p.waiting_time for p in processes)
    avg_tat = total_tat / len(processes)
    avg_wt = total_wt / len(processes)
    
    print(f"\nTotal Turnaround Time: {total_tat}")
    print(f"Average Turnaround Time: {avg_tat:.2f}")
    print(f"Total Waiting Time: {total_wt}")
    print(f"Average Waiting Time: {avg_wt:.2f}")

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
    
    while completed < len(processes):
        highest_priority_process = None
        for process in processes:
            if (process.arrival_time <= current_time and 
                (process.remaining_time if preemptive else process.completion_time == 0)):
                if highest_priority_process is None or process.priority < highest_priority_process.priority:
                    highest_priority_process = process
        
        if highest_priority_process:
            if preemptive:
                execution_log.append([highest_priority_process.pid, current_time, current_time + 1])
                highest_priority_process.remaining_time -= 1
                current_time += 1
                
                if highest_priority_process.remaining_time == 0:
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
    
    return execution_log

def get_user_input(algorithm):
    while True:
        try:
            n = int(input("\nEnter the number of processes (3-10): "))
            if 3 <= n <= 10:
                break
            print("Number of processes must be between 3 and 10.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
    
    processes = []
    for i in range(n):
        print(f"\nProcess {i}:")
        while True:
            try:
                arrival_time = int(input("Arrival Time: "))
                burst_time = int(input("Burst Time: "))
                if arrival_time < 0 or burst_time <= 0:
                    print("Arrival Time must be >= 0 and Burst Time must be > 0")
                    continue
                
                priority = None
                if algorithm != "SJN":
                    priority = int(input("Priority: "))
                    if priority <= 0:
                        print("Priority must be > 0")
                        continue
                
                processes.append(Process(i, arrival_time, burst_time, priority))
                break
            except ValueError:
                print("Invalid input. Please enter integers only.")
    
    if algorithm == "RR":
        while True:
            try:
                time_quantum = int(input("\nEnter Time Quantum: "))
                if time_quantum > 0:
                    return processes, time_quantum
                print("Time Quantum must be > 0")
            except ValueError:
                print("Invalid input. Please enter an integer.")
    
    return processes, None

def main():
    print("CPU Scheduling Algorithms:")
    print("1. Shortest Job Next (SJN)")
    print("2. Round Robin (RR)")
    print("3. Non-preemptive Priority")
    print("4. Preemptive Priority")
    print("5. Exit")
    
    while True:
        try:
            choice = int(input("\nSelect an algorithm (1-5): "))
            if 1 <= choice <= 5:
                break
            print("Invalid choice. Please select 1-5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1-5.")
    
    if choice == 5:
        print("Exiting program.")
        return
    
    algorithm = {1: "SJN", 2: "RR", 3: "NP", 4: "PP"}[choice]
    processes, time_quantum = get_user_input(algorithm)
    
    print("\nInitial Process Details:")
    print_table(processes)
    
    if algorithm == "SJN":
        execution_log = sjn_scheduling(processes)
    elif algorithm == "RR":
        execution_log = round_robin_scheduling(processes, time_quantum)
    elif algorithm == "NP":
        execution_log = priority_scheduling(processes, preemptive=False)
    else:  # PP
        execution_log = priority_scheduling(processes, preemptive=True)
    
    print("\nFinal Process Details:")
    print_table(processes)
    print_gantt_chart(execution_log)
    calculate_metrics(processes)

if __name__ == "__main__":
    main()