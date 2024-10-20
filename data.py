import re
import psutil
import subprocess

def get_command_string(pid):
    """Get the full command string for a given PID using `top`."""
    result = None
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'comm='],
            stdout=subprocess.PIPE, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return "<unknown>"
    if result is not None:
        return result.stdout.strip().split('/')[-1]
    return "<unknown>"

def memory_percentage(rss):
    """Convert RSS value in KB to percentage of total memory."""
    total_memory = psutil.virtual_memory().total
    rss_bytes = int(rss) * 1024  # Convert KB to bytes
    return (rss_bytes / total_memory) * 100

def get_top_cpu_processes():
    """Executes `top -l 1` and returns the 10 most CPU-intensive processes as a list of dictionaries."""
    result = None
    try:
        # Run the ps command and capture output
        result = subprocess.run(
            ['ps', '-axo', 'pid,%cpu,rss'],
            stdout=subprocess.PIPE, text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing top: {e}")
        return []

    # Parse the ps output, skipping the header row
    lines = result.stdout.strip().split('\n')[1:]

    if len(lines) == 0:
        return []

    # Store processes as a list of dictionaries
    processes = []
    for line in lines:
        pid, cpu, mem = re.split(r'\s+', line.strip(), 2)
        processes.append({
            'pid': int(pid),
            'cpu': float(cpu),
            'mem': memory_percentage(mem)
        })

    # Sort the processes first by CPU%, then by MEM%
    processes.sort(key=lambda x: (-x['cpu'], -x['mem']))

    top_processes = processes[:10]  # Get the top 10

    # Supplement each process with the full command string
    for process in top_processes:
        process['command'] = get_command_string(process['pid'])

    return top_processes
