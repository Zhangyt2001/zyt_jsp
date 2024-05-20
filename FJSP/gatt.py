import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as patches

# Job schedule data example (Job ID, Machine ID, Start Time, Duration)
schedule = [
    ('Job1_1', 'Machine1', 14, 10),
    ('Job1_2', 'Machine2', 26, 5),
    ('Job1_3', 'Machine3', 43, 8),
    ('Job2_1', 'Machine2', 18, 5),
    ('Job2_2', 'Machine1', 24, 3),
    ('Job2_3', 'Machine3', 28, 15),
    ('Job3_1', 'Machine3', 0, 8),
    ('Job3_2', 'Machine2', 8, 10),
    ('Job3_3', 'Machine1', 26, 8)
]

# Constraints (Job ID, [Min Wait Time, Max Wait Time])
time_windows = {

    'Job1': [(0, 1), (1, 12)],  # Between operations of Job1
    'Job2': [(0, 2), (1, 10)],  # Between operations of Job2
    'Job3': [(0, 4), (0, 10)]   # Between operations of Job3
}

# Color mapping
# colors = {
#     'Job1_1': 'skyblue',
#     'Job1_2': 'skyblue',
#     'Job1_3': 'skyblue',
#     'Job2_1': 'lightgreen',
#     'Job2_2': 'lightgreen',
#     'Job2_3': 'lightgreen',
#     'Job3_1': 'lightcoral',
#     'Job3_2': 'lightcoral',
#     'Job3_3': 'lightcoral'
# }
colors = {
    'Job1': 'skyblue',
    'Job2': 'lightgreen',
    'Job3': 'lightcoral'
}
fig, gnt = plt.subplots()

# Set chart title and axis labels
gnt.set_title('Workshop Scheduling Gantt Chart')
gnt.set_xlabel('Time')
gnt.set_ylabel('Machines')

# Set Y-axis
machines = list(set([job[1] for job in schedule]))
machines.sort()
gnt.set_yticks(range(len(machines)))
gnt.set_yticklabels(machines)

# Set X-axis range
max_time = max([job[2] + job[3] for job in schedule])
gnt.set_xlim(0, max_time+10)

# Function to check time window constraints
def check_constraints(schedule, time_windows):
    violations = []
    for job_id in time_windows.keys():
        job_operations = [job for job in schedule if job[0].startswith(job_id)]
        job_operations.sort(key=lambda x: x[2])  # Sort by start time
        for i in range(len(job_operations) - 1):
            end_time = job_operations[i][2] + job_operations[i][3]
            next_start_time = job_operations[i+1][2]
            min_wait, max_wait = time_windows[job_id][i]
            if next_start_time < end_time + min_wait:
                violations.append((job_operations[i], job_operations[i+1], 'Min'))
            elif next_start_time > end_time + max_wait:
                violations.append((job_operations[i], job_operations[i+1], 'Max'))
    return violations


# Check for constraint violations
violations = check_constraints(schedule, time_windows)


# Check for machine overlap
def check_machine_overlap(schedule):
    machine_schedule = {}
    for job_id, machine_id, start_time, duration in schedule:
        if machine_id not in machine_schedule:
            machine_schedule[machine_id] = []
        for scheduled_job_id, scheduled_start_time, scheduled_duration in machine_schedule[machine_id]:
            if (start_time < scheduled_start_time + scheduled_duration and
                    start_time + duration > scheduled_start_time):
                print(f"Machine {machine_id} is busy at time {start_time} with jobs {job_id} and {scheduled_job_id}")
        machine_schedule[machine_id].append((job_id, start_time, duration))

# Call function to check machine overlap
check_machine_overlap(schedule)


# Check for machine overlap
def check_machine_overlap(schedule):
    machine_schedule = {}
    machine_overlap = []
    for job_id, machine_id, start_time, duration in schedule:
        if machine_id not in machine_schedule:
            machine_schedule[machine_id] = []
        for scheduled_job_id, scheduled_start_time, scheduled_duration in machine_schedule[machine_id]:
            if (start_time < scheduled_start_time + scheduled_duration and
                    start_time + duration > scheduled_start_time):
                print(f"Machine {machine_id} is busy at time {start_time} with jobs {job_id} and {scheduled_job_id}")
                machine_overlap.append((start_time, machine_id))
        machine_schedule[machine_id].append((job_id, start_time, duration))
    return machine_overlap

# Call function to check machine overlap
machine_overlap = check_machine_overlap(schedule)

# Add machine overlap to the Gantt chart
for overlap_time, machine_id in machine_overlap:
    machine_idx = machines.index(machine_id)
    gnt.broken_barh([(overlap_time, 1)], (machine_idx - 0.4, 0.8), facecolors='red', alpha=0.3)
    gnt.text(overlap_time + 0.5, machine_idx, 'Overlap', ha='center', va='center', color='red')


# Add jobs to the Gantt chart
for job in schedule:
    job_id, machine_id, start_time, duration = job
    job_prefix = job_id.split('_')[0]  # Extract job prefix
    machine_idx = machines.index(machine_id)
    gnt.broken_barh([(start_time, duration)], (machine_idx - 0.4, 0.8), facecolors=(colors[job_prefix]))

# Add shaded areas and labels for violations
for violation in violations:
    job1, job2, violation_type = violation
    job1_id, _, job1_start, job1_duration = job1
    job2_id, _, job2_start, _ = job2
    job1_end = job1_start + job1_duration
    machine_idx = machines.index(job1[1])
    job1_job_number = int(job1_id.split('_')[1])  # Extract job number from job ID
    job1_prefix = job1_id.split('_')[0]  # Extract job prefix
    job2_prefix = job2_id.split('_')[0]  # Extract job prefix
    job1_time_window = time_windows[job1_prefix][job1_job_number - 1]  # Get time window for job1
    print(f"Debug - job1_id: {job1_id}, job1_prefix: {job1_prefix}, job1_job_number: {job1_job_number}, job1_time_window: {job1_time_window}")
    if violation_type == 'Min':
        min_wait, _ = job1_time_window
        rect = patches.Rectangle((job1_end, machine_idx - 0.4), min_wait, 0.8, linewidth=1, edgecolor='r',
                                 facecolor='pink', alpha=0.3)
        gnt.add_patch(rect)
        gnt.text(job1_end + min_wait / 2, machine_idx, 'Min Violation', ha='center', va='center', color='red')
    elif violation_type == 'Max':
        _, max_wait = job1_time_window
        rect = patches.Rectangle((job1_end, machine_idx - 0.4), max_wait, 0.8, linewidth=1, edgecolor='r',
                                 facecolor='lightcoral', alpha=0.3)
        gnt.add_patch(rect)
        gnt.text(job1_end + max_wait / 2, machine_idx, 'Max Violation', ha='center', va='center', color='red')

# Create legend
patches_list = [mpatches.Patch(color=colors[job_id], label=job_id) for job_id in colors]
patches_list.append(mpatches.Patch(color='red', label='Constraint Violation'))
plt.legend(handles=patches_list)

# Save chart to file
plt.savefig('4')

# Show chart
plt.show()
