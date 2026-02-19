"""
Comparison - Partial Copy (CHEATING)
Only core logic copied: filter and write. Different I/O, different structure.
"""


def process_data():
    data = fetch_from_db()
    filtered = [x for x in data if len(str(x).strip()) > 5]
    save_results(filtered)
    return len(filtered)


def fetch_from_db():
    with open("input.txt", "r") as f:
        return f.readlines()


def save_results(items):
    with open("output.txt", "w") as f:
        f.write("\n".join(str(i).strip() for i in items))


if __name__ == "__main__":
    process_data()
