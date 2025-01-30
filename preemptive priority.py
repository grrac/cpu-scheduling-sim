class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0


def preemptive_priority_scheduling(processes):
    time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []

    while completed != n:
        current_process = None
        for process in processes:
            if process.arrival_time <= time and process.remaining_time > 0:
                if (current_process is None or 
                    process.priority < current_process.priority or 
                    (process.priority == current_process.priority and process.arrival_time < current_process.arrival_time)):
                    current_process = process

        if current_process:
            current_process.remaining_time -= 1
            time += 1
            gantt_chart.append(f"P{current_process.pid}")

            if current_process.remaining_time == 0:
                completed += 1
                current_process.completion_time = time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
        else:
            if any(p.remaining_time > 0 and p.arrival_time > time for p in processes):
                time = min(p.arrival_time for p in processes if p.remaining_time > 0 and p.arrival_time > time)
            else:
                time += 1

   
    print("PID\tArrival Time\tBurst Time\tPriority\tCompletion Time\tTurnaround Time\tWaiting Time")
    total_turnaround_time = 0
    total_waiting_time = 0
    for process in processes:
        print(f"{process.pid}\t{process.arrival_time}\t{process.burst_time}\t{process.priority}\t{process.completion_time}\t{process.turnaround_time}\t{process.waiting_time}")
        total_turnaround_time += process.turnaround_time
        total_waiting_time += process.waiting_time
    
   
    avg_turnaround_time = total_turnaround_time / n
    avg_waiting_time = total_waiting_time / n
    
    print(f"\nTotal Turnaround Time: {total_turnaround_time}")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")
    print(f"Total Waiting Time: {total_waiting_time}")
    print(f"Average Waiting Time: {avg_waiting_time:.2f}")

    
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
    print("\nPreemptive Priority Scheduling Result:")
    preemptive_priority_scheduling(process_list)

if __name__ == "__main__":
    main()
