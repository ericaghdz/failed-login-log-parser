# Failed Login Log Parser

A small Python tool that scans an authentication log for failed SSH login attempts and tallies them by source IP address — a simplified version of the kind of triage a SOC analyst does when scanning auth logs for brute-force activity.

## What it does

Given a log file like:

```
2026-07-14 09:12:01 sshd: Failed password for admin from 192.168.1.50 port 51422
2026-07-14 09:12:03 sshd: Failed password for root from 192.168.1.50 port 51423
2026-07-14 09:13:10 sshd: Accepted password for eric from 10.0.0.5 port 51500
```

The script identifies every line containing a failed login, extracts the source IP, tallies attempts per IP, and prints a ranked summary from most to least active offender:

```
Failed login attempts by IP (highest first):
  45.33.12.9: 3
  192.168.1.50: 2
```

## How it works

1. **Read the file line by line** using `with open(filename) as file`, iterating over each line.
2. **Filter for failed attempts** by checking whether `"Failed password"` appears in the line.
3. **Extract the source IP** using a regular expression (`\d+\.\d+\.\d+\.\d+`) that matches the shape of an IPv4 address, rather than relying on a fixed word position in the line.
4. **Tally by IP** using a dictionary, incrementing a running count each time an IP reappears.
5. **Return the result** from a reusable function, `count_failed_logins(filename)`, so it can be run against any log file, not just the sample data.
6. **Sort and print a ranked summary** with `print_sorted_summary(counts)`, using `sorted()` with a `key` function to order IPs from most to least failed attempts, and f-strings for clean output formatting.

## Why regex instead of a fixed index

The first working version located the IP with `line.split()[8]` — grabbing the 9th whitespace-separated word in the line. That worked for this specific log format, but it was fragile: any log source with a different layout, extra fields, or missing fields would break it or silently grab the wrong value.

Switching to a regex pattern search (`re.search(r"\d+\.\d+\.\d+\.\d+", line)`) makes the parser format-agnostic — it finds the IP wherever it sits in the line, so the same function works across different log sources without modification.

## Usage

```bash
python log_parser.py
```

By default it parses `auth.log` in the same directory. To use it on a different file:

```python
from log_parser import count_failed_logins, print_sorted_summary

results = count_failed_logins("your_log_file.log")
print_sorted_summary(results)
```

## Object-oriented version

Alongside the dictionary-based tally, the project also includes an object-oriented approach using a `LoginAttempt` class:

```python
class LoginAttempt:
    def __init__(self, ip, username, success):
        self.ip = ip
        self.username = username
        self.success = success

    def summary(self):
        if self.success:
            print(f"{self.username} logged in successfully from {self.ip}")
        else:
            print(f"Failed login for {self.username} from {self.ip}")
```

Instead of just tallying counts, `parse_failed_logins(filename)` builds a list of `LoginAttempt` objects — one per failed login — each holding its own `ip`, `username`, and `success` status, plus a `summary()` method that describes itself:

```python
attempts = parse_failed_logins("auth.log")
for attempt in attempts:
    attempt.summary()
```

```
Failed login for admin from 192.168.1.50
Failed login for root from 192.168.1.50
Failed login for admin from 45.33.12.9
Failed login for root from 45.33.12.9
Failed login for test from 45.33.12.9
```

This approach trades the simplicity of the dictionary tally for more detail per attempt (username, not just IP) and room to grow — additional fields like timestamp or port could be added to `LoginAttempt` without changing how the rest of the code works.

## Possible next steps

- Write results out to a CSV or JSON summary file
- Add a command-line argument (`argparse`) to pass in the log filename instead of hardcoding it
- Extend `LoginAttempt` to capture timestamp and port for a fuller picture per attempt
- Add a class method to `LoginAttempt` (or a separate function) that summarizes a whole list of attempts, sorted by IP with the most failures

## Background

Built as a learning project while working through Python fundamentals (variables, conditionals, loops, functions, file I/O, dictionaries, and regular expressions) — this was the first project attempted, revisited once those fundamentals were in place.
