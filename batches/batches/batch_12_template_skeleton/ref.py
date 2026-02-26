"""
Reference - Original code for Batch 12: Template/Skeleton (NOT cheating)
Minimal logic, heavy boilerplate.
"""


import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="out.txt")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.input) as f:
        data = f.read()
    result = data.upper()
    with open(args.output, "w") as f:
        f.write(result)


if __name__ == "__main__":
    main()
