def main():
    while True:
        try:
            num = int(input("Enter the number of processes (3-10): "))
            if 3 <= num <= 10:
                break
            else:
                print(">> Please enter a number between 3 and 10.\n")
        except ValueError:
            print(">> Invalid input. Please enter an integer value.\n")

    processes = []

    for i in range(num):
        print(f"Process {i}")
        arrival = int(input("Enter the arrival time: "))
        burst = int(input("Enter the burst time: "))
        priority = int(input("Enter the priority: "))  # Priority isn't used in SJN
        processes.append(["P" + str(i), arrival, burst])
        print()

    execution_log = non_preemptive_sjn(processes)
    gantt_chart(execution_log)
    calculations(processes, execution_log)


def non_preemptive_sjn(processes):
    processes.sort(key=lambda x: x[1])  # Sort by arrival time

    current_time = 0
    execution_log = []
    completed = []

    while len(completed) < len(processes):
        # Get processes that have arrived and are not completed
        ready_queue = [p for p in processes if p[1] <= current_time and p not in completed]

        if ready_queue:
            # Select process with shortest burst time (if tie, FCFS)
            ready_queue.sort(key=lambda x: x[2])
            process = ready_queue[0]

            # Execute the process
            process_name, arrival_time, burst_time = process
            start_time = current_time
            end_time = current_time + burst_time
            execution_log.append([process_name, start_time, end_time])

            # Update time and mark process as completed
            current_time = end_time
            completed.append(process)
        else:
            # If no process is ready, move to the next arrival time
            current_time += 1

    return execution_log


def gantt_chart(execution_log):
    print("\nGantt Chart:")

    border = "+-" + "------+" * len(execution_log)
    print(border)

    for entry in execution_log:
        process_name, _, _ = entry
        print(f"|  {process_name}  ", end="")
    print("|")

    print(border)

    current_time = execution_log[0][1]  # Start time of the first process
    print(f"{current_time:<3}", end="")

    for entry in execution_log:
        _, _, end_time = entry
        print(f"{end_time:<6}", end="")
    print()


def calculations(processes, execution_log):
    num_processes = len(processes)
    completion_times = [0] * num_processes
    turnaround_times = [0] * num_processes
    waiting_times = [0] * num_processes

    # Determine completion times based on execution log
    for log in execution_log:
        process_name, _, end_time = log
        process_index = int(process_name[1:])
        completion_times[process_index] = end_time

    total_tat = 0
    total_wt = 0

    print("\nProcess\tArrival\tBurst\tCompletion\tTAT\tWT")
    for i, process in enumerate(processes):
        name, arrival, burst = process
        tat = completion_times[i] - arrival  # Turnaround Time
        wt = tat - burst  # Waiting Time

        turnaround_times[i] = tat
        waiting_times[i] = wt
        total_tat += tat
        total_wt += wt

        print(f"{name}\t{arrival}\t{burst}\t{completion_times[i]}\t\t{tat}\t{wt}")

    avg_tat = total_tat / num_processes
    avg_wt = total_wt / num_processes

    print(f"\nAverage Turnaround Time: {avg_tat:.2f}")
    print(f"Average Waiting Time: {avg_wt:.2f}")

main()
