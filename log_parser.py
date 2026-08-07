"""
Failed Login Log Parser
Scans an auth log file for failed SSH login attempts and tallies
attempts by source IP address.
"""

import re


def count_failed_logins(filename):
    """
    Reads a log file and counts failed login attempts per IP address.

    Args:
        filename (str): Path to the log file to parse.

    Returns:
        dict: Mapping of IP address (str) -> number of failed attempts (int).
    """
    counts = {}

    with open(filename) as file:
        for line in file:
            if "Failed password" in line:
                match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                ip = match.group()

                if ip in counts:
                    counts[ip] = counts[ip] + 1
                else:
                    counts[ip] = 1

    return counts


def print_sorted_summary(counts):
    """
    Prints failed login counts sorted from highest to lowest.

    Args:
        counts (dict): Mapping of IP address (str) -> failed attempt count (int),
                        as returned by count_failed_logins().
    """
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    print("Failed login attempts by IP (highest first):")
    for ip, count in sorted_counts:
        print(f"  {ip}: {count}")


class LoginAttempt:
    """Represents a single login attempt parsed from a log line."""

    def __init__(self, ip, username, success):
        self.ip = ip
        self.username = username
        self.success = success

    def summary(self):
        """Prints a human-readable summary of this login attempt."""
        if self.success:
            print(f"{self.username} logged in successfully from {self.ip}")
        else:
            print(f"Failed login for {self.username} from {self.ip}")


def parse_failed_logins(filename):
    """
    Reads a log file and builds a LoginAttempt object for each failed login.

    Args:
        filename (str): Path to the log file to parse.

    Returns:
        list[LoginAttempt]: One LoginAttempt per failed login line.
    """
    attempts = []

    with open(filename) as file:
        for line in file:
            if "Failed password" in line:
                words = line.split()
                username = words[6]

                match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                ip = match.group()

                attempt = LoginAttempt(ip, username, False)
                attempts.append(attempt)

    return attempts


if __name__ == "__main__":
    # Dictionary-based approach: quick tally sorted by count
    counts = count_failed_logins("auth.log")
    print_sorted_summary(counts)

    print()

    # Object-oriented approach: each attempt as its own LoginAttempt object
    attempts = parse_failed_logins("auth.log")
    for attempt in attempts:
        attempt.summary()
