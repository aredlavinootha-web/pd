"""
Reference - Original code for Batch 11: Partial Copy
Full script: reads file, filters lines, writes output.
"""


def main():
    with open("input.txt", "r") as f:
        lines = f.readlines()
    filtered = [line.strip() for line in lines if len(line.strip()) > 5]
    with open("output.txt", "w") as f:
        f.write("\n".join(filtered))
    return len(filtered)


if __name__ == "__main__":
    main()
