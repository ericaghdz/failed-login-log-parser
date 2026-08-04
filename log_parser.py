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


if __name__ == "__main__":
    results = count_failed_logins("auth.log")
    print_sorted_summary(results)
