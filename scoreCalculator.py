import json
import sys
import argparse

def main(report_list):
    # Initialize counters for different severity levels
    warning_count = 0
    info_count = 0
    error_count = 0

    # Read JSON input from stdin and process each JSON object

    for report in report_list:
        violations = report.get("violations", [])
            # Iterate through violations and count severity levels
        for violation in violations:
                
            severity = violation.get("severity", "").upper()
            if severity == "WARNING":
                warning_count += 1
            elif severity == "INFO":
                    info_count += 1
            elif severity == "ERROR":
                    error_count += 1
                    break
   

    # Print the counts
    print(f"WARNING count: {warning_count}")
    print(f"INFO count: {info_count}")
    print(f"ERROR count: {error_count}")

if __name__ == "__main__":
    main()
