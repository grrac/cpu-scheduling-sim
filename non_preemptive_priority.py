class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0


def non_preemptive_priority_scheduling(processes):
    time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []

    while completed != n:
        # Select the process with the highest priority that is ready to execute
        current_process = None
        for process in processes:
            if process.arrival_time <= time and process.completion_time == 0:
                if (current_process is None or 
                    process.priority < current_process.priority or 
                    (process.priority == current_process.priority and process.arrival_time < current_process.arrival_time)):
                    current_process = process

        if current_process:
            # Execute the process to completion
            gantt_chart.extend([f"P{current_process.pid}"] * current_process.burst_time)
            time += current_process.burst_time
            current_process.completion_time = time
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            completed += 1
        else:
            # No process is ready to execute; increment time
            time += 1

    # Output results with centered table
    header = [
        "PID", "Arrival Time", "Burst Time", "Priority", 
        "Completion Time", "Turnaround Time", "Waiting Time"
    ]
    widths = [5, 14, 12, 10, 18, 18, 14]

    # Print the table header
    print("\n" + "".join(title.center(width) for title, width in zip(header, widths)))
    print("=" * sum(widths))

    total_turnaround_time = 0
    total_waiting_time = 0
    for process in processes:
        row = [
            str(process.pid), str(process.arrival_time), str(process.burst_time),
            str(process.priority), str(process.completion_time),
            str(process.turnaround_time), str(process.waiting_time)
        ]
        print("".join(value.center(width) for value, width in zip(row, widths)))
        total_turnaround_time += process.turnaround_time
        total_waiting_time += process.waiting_time
    
    avg_turnaround_time = total_turnaround_time / n
    avg_waiting_time = total_waiting_time / n

    print("\nTotal Turnaround Time: {}".format(total_turnaround_time))
    print("Average Turnaround Time: {:.2f}".format(avg_turnaround_time))
    print("Total Waiting Time: {}".format(total_waiting_time))
    print("Average Waiting Time: {:.2f}".format(avg_waiting_time))

    print("\nGantt Chart:")
    print(" -> ".join(gantt_chart))


def get_user_input():
    process_list = []
    while True:
        try:
            n = int(input("Enter the number of processes (between 3 and 10): "))
            if n < 3 or n > 10:
                print("The number of processes must be between 3 and 10. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

    for i in range(n):
        while True:
            try:
                print(f"\nEnter details for Process {i + 1}:")
                arrival_time = int(input("Arrival Time: "))
                burst_time = int(input("Burst Time: "))
                priority = int(input("Priority: "))
                if arrival_time < 0 or burst_time <= 0 or priority <= 0:
                    print("Arrival Time must be >= 0, Burst Time and Priority must be > 0. Please try again.")
                    continue
                process_list.append(Process(i + 1, arrival_time, burst_time, priority))
                break
            except ValueError:
                print("Invalid input. Please enter integers only.")
    return process_list


def main():
    process_list = get_user_input()
    print("\nNon-Preemptive Priority Scheduling Result:")
    non_preemptive_priority_scheduling(process_list)


if __name__ == "__main__":
    main()
