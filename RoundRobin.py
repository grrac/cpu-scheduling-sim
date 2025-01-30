
"""
1. Input details for the processes such as Arrival Time, Burst Time, Priority, Time Quantum (RR), num of processes (3-10).
2. Output Gantt Chart for processes.
3. if there are two or more processes with SAME PRIORITY and same arrival time in the ready poll, privilege go to the process that not being executed before (to give chance to “hungry” process to be fed into CPU). 

4. Calculation of
    i. Turnaround time for each process (Completion time - Arrival time)
    ii. Total and Average Turnaround time for the entire processes
    iii. Waiting time for each process (Turnaround time - Burst time)
    iv. Total and Average Waiting time for the entire processes
"""

def main():
    while True:
        try:
            num = int(input("Enter the number of processes (3-10): "))
            # Validate user input
            if 3 <= num <= 10:
                break  # Exit the loop if input is valid
            else:
                print(">> Please enter a number between 3 and 10.\n")
        except ValueError:
            print(">> Invalid input. Please enter an integer value.\n")
    
    # Initialize empty list to store processes
    processes = [];

    TQ = int(input("Enter the time quantum: "));
    print();
    for i in range(num):
        print("Process",i);
        arrival = int(input("Enter the arrival time: "));
        burst = int(input("Enter the burst time: "));
        priority = int(input("Enter the priority: "));
        processes.append(["P"+str(i),arrival, burst, priority]);
        print();
        print(processes);

    # Move the return statement to the end
    execution_log = roundRobin(processes, TQ);
    ganttChart(execution_log);
    calculations(processes, execution_log);
    return processes;

def table(processes):
    print("+---------+--------------+------------+----------+")
    print("| Process | Arrival Time | Burst Time | Priority |")
    print("+---------+--------------+------------+----------+")
    for i in range(len(processes)):
        print("| {:<7} | {:<12} | {:<10} | {:<8} |".format(
            processes[i][0], processes[i][1], processes[i][2], processes[i][3]))
    print("+---------+--------------+------------+----------+")

# Round Robin Algorithm
def roundRobin(processes, TQ):

    # Create a copy of process list to avoid modifying the OG
    processes_copy = [];
    processes_copy = list(processes);
    processes_copy.sort(key=lambda x: (x[1], x[3]));  # Sort processes by arrival time then priority

    # TEST OUTPUT
    print("Sorted by arrival time:")
    print(processes_copy)

    # ----------------------------------------
    # Initialize variables
    current_time = 0;

    # Ready queue and execution log
    ready_queue = [];
    execution_log = [];

    # Add newly arrived processes to the ready_queue
    for i in range(len(processes_copy)):
        if processes_copy[i][1] <= current_time and processes_copy[i] not in ready_queue:
            ready_queue.append(processes_copy[i]);
            processes_copy.pop(i);
            break;
    
    # TEST OUTPUT
    print("Ready Queue:")
    print(ready_queue)
    print("Processes Remaining:")
    print(processes_copy)

    # ----------------------------------------
    # Start Round Robin
    while ready_queue:
        if ready_queue: # Check if the ready queue is not empty
            process = ready_queue.pop(0); # Get the first process in the ready queue (FIFO)
            process_name, arrival_time, burst_time, priority = process;  # Extract process details

            # Execute the process for the time quantum
            time_executed = min(TQ, burst_time);
            current_time += time_executed;

            # Update process details
            burst_time -= time_executed;
            execution_log.append([process_name, (current_time - time_executed), current_time]);

            # Add newly arrived processes to the ready queue
            i = 0
            while i < len(processes_copy):
                if processes_copy[i][1] <= current_time and processes_copy[i] not in ready_queue:
                    ready_queue.append(processes_copy[i])
                    processes_copy.pop(i)
                else:
                    i += 1

            # Requeue the process if it still has burst time left
            if burst_time > 0:
                ready_queue.append((process_name, arrival_time, burst_time, priority))
        else:
            # If the ready queue is empty, move to the next arrival time
            current_time = processes_copy[0][1]
            ready_queue.append(processes_copy.pop(0))

            # TEST OUTPUT
            print("Ready Queue:")
            print(ready_queue)
            print("Processes Remaining:")
            print(processes_copy)

    # ----------------------------------------
    # Display Execution Log
    print("\nExecution Log:")
    for log in execution_log:
        print(f"Process {log[0]} executed from time {log[1]} to time {log[2]}")

    return(execution_log);


def ganttChart(execution_log):
    print("\nGantt Chart:")
    
    # Print the top border
    border = "+-" + "------+" * (len(execution_log));
    print(border)
    for entry in execution_log:
        process_name, start_time, end_time = entry
        print(f"|  {process_name}  ", end="")
    print(" |")
    
    print(border)
    # Print the time markers
    current_time = execution_log[0][1]  # Start time of the first process
    print(f"{current_time}", end="")
    
    for entry in execution_log:
        _, _, end_time = entry
        print(f"{end_time:7}", end="")  # Adjust spaces for alignment
   
def calculations(processes,execution_log):
    num_processes = len(processes)
    completion_times = [0] * num_processes  # List to store completion times
    turnaround_times = [0] * num_processes  # List to store TAT
    waiting_times = [0] * num_processes     # List to store WT

    # Find the last time each process was executed (completion time)
    for log in execution_log:
        process_name = log[0]
        end_time = log[2]
        process_index = int(process_name[1:])  # Extract process number from "P0", "P1", etc.
        completion_times[process_index] = max(completion_times[process_index], end_time)

    # Calculate TAT and WT for each process
    total_tat = 0
    total_wt = 0
    print("\n")
    print("Process\tArrival\tBurst\tCompletion\tTAT\tWT")
    
    for i in range(num_processes):
        name, arrival, burst, _ = processes[i]
        tat = completion_times[i] - arrival  # Turnaround Time
        wt = tat - burst  # Waiting Time

        turnaround_times[i] = tat
        waiting_times[i] = wt
        total_tat += tat
        total_wt += wt

        print(f"{name}\t{arrival}\t{burst}\t{completion_times[i]}\t\t{tat}\t{wt}")

    # Calculate and display averages
    avg_tat = total_tat / num_processes
    avg_wt = total_wt / num_processes
    print(f"\nAverage Turnaround Time: {avg_tat:.2f}")
    print(f"Average Waiting Time: {avg_wt:.2f}")

main();

