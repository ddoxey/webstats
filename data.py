import re
import psutil
import subprocess
from collections import defaultdict

def get_core_count():
    result = None
    for cmd in [['nproc'], ['sysctl', '-n', 'hw.ncpu']]:
        try:
            result = subprocess.run(cmd,
                                    stdout=subprocess.PIPE,
                                    text=True, check=True)
            break
        except subprocess.CalledProcessError:
            pass
    if result is not None:
        return result.stdout.strip()
    return 1

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

def get_pids(proc_name):
    """Return a list of PIDs for the given program name."""
    result = None
    try:
        result = subprocess.run(
            ['pidof', proc_name],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        return []
    pids = [pid for pid in result.stdout.strip().split()]
    return pids

def memory_percentage(rss):
    """Convert RSS value in KB to percentage of total memory."""
    total_memory = psutil.virtual_memory().total
    rss_bytes = int(rss) * 1024  # Convert KB to bytes
    return (rss_bytes / total_memory) * 100

def get_processes(watch_list):
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

    watch_pids = set()
    proc_name_of = {}

    for proc_name in watch_list:
        pids = get_pids(proc_name)
        for pid in pids:
            watch_pids.add(pid)
            proc_name_of[pid] = proc_name

    # Store processes as a list of dictionaries
    stats_for = defaultdict(lambda: {'cpu': 0.0, 'mem': 0.0})
    for line in lines:
        pid, cpu, mem = re.split(r'\s+', line.strip(), 2)
        if pid in watch_pids:
            proc_name = proc_name_of[pid]
            stats_for[proc_name]['cpu'] += float(cpu)
            stats_for[proc_name]['mem'] += memory_percentage(mem)

    core_count = psutil.cpu_count(logical=True)

    processes = []
    for proc_name in stats_for:
        processes.append({
            'cpu': stats_for[proc_name]['cpu'] / core_count,
            'mem': stats_for[proc_name]['mem'],
            'command': proc_name})

    # Sort the processes first by CPU%, then by MEM%
    processes.sort(key=lambda x: (-x['cpu'], -x['mem']))

    return processes
