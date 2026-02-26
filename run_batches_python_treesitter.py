"""
Run tree-sitter Python detector on all batches (Python) and output expected vs actual table.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from plagiarism_detect_treesitter_python import compare_code_treesitter_python

BATCH_DIR = os.path.join(os.path.dirname(__file__), "batches", "batches")

# Human-readable case names from batch folder names
CASE_NAMES = {
    "01_exact_copy": "Exact Copy",
    "02_variable_renaming": "Variable Renaming",
    "03_whitespace_formatting": "Whitespace or Formatting Changes",
    "04_comment_addition": "Comment Addition or Removal",
    "04_comment_addition_removal": "Comment Addition or Removal",
    "05_function_extraction": "Function Extraction",
    "06_loop_type_change": "Loop Type Changes (for ↔ while)",
    "07_recursive_iterative": "Recursive vs Iterative Implementation",
    "08_minor_logic_modification": "Minor Logic Modification",
    "09_dead_code_insertion": "Dead Code Insertion",
    "10_code_reordering": "Code Reordering",
    "11_partial_copy": "Partial Copy",
    "12_template_skeleton": "Template or Skeleton Use",
    "13_different_implementation_same_algorithm": "Different Implementation, Same Algorithm",
    "14_completely_different_logic": "Completely Different Logic",
}


def run_batches():
    batches = sorted(
        d for d in os.listdir(BATCH_DIR)
        if os.path.isdir(os.path.join(BATCH_DIR, d))
        and d.startswith("batch_")
        and not d.startswith("batch_14_") or d == "batch_14_completely_different_logic"
    )

    # Filter to only the 14 main batches (batch_01 through batch_14)
    main_batches = [
        f"batch_{i:02d}_{name}"
        for i, name in [
            (1, "exact_copy"),
            (2, "variable_renaming"),
            (3, "whitespace_formatting"),
            (4, "comment_addition"),
            (5, "function_extraction"),
            (6, "loop_type_change"),
            (7, "recursive_iterative"),
            (8, "minor_logic_modification"),
            (9, "dead_code_insertion"),
            (10, "code_reordering"),
            (11, "partial_copy"),
            (12, "template_skeleton"),
            (13, "different_implementation_same_algorithm"),
            (14, "completely_different_logic"),
        ]
    ]

    rows = []
    for batch_dir in main_batches:
        batch_path = os.path.join(BATCH_DIR, batch_dir)
        if not os.path.isdir(batch_path):
            continue
        setup_path = os.path.join(batch_path, "setup_batch.py")
        if not os.path.exists(setup_path):
            continue

        try:
            from importlib.util import spec_from_file_location, module_from_spec
            spec = spec_from_file_location("setup_batch", setup_path)
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)
            data = mod.setup_batch()
        except Exception as e:
            rows.append({
                "case": batch_dir.replace("batch_", "").replace("_", " ").title(),
                "expected": "N/A",
                "actual": f"ERR: {e}",
                "in_range": "?",
            })
            continue

        ref_code = data.get("ref", "")
        compare_code = data.get("compare", "")
        exp_range = data.get("expected_similarity_range", (0, 0))
        batch_name = data.get("batch_name", batch_dir)

        case_name = CASE_NAMES.get(batch_name, batch_name.replace("_", " ").title())

        expected_str = f"{exp_range[0]}-{exp_range[1]}%"

        # Run tree-sitter Python
        try:
            result = compare_code_treesitter_python(
                "ref", ref_code,
                [{"id": "compare", "code": compare_code}],
            )
        except Exception as e:
            rows.append({
                "case": case_name,
                "expected": expected_str,
                "actual": f"ERR: {e}",
                "in_range": "?",
            })
            continue

        if not result.get("available"):
            actual_str = result.get("error", "N/A")
            in_range = "?"
        else:
            res_list = result.get("results", [])
            if not res_list:
                actual_str = "N/A"
                in_range = "?"
            else:
                sim = res_list[0].get("similarity")
                if sim is None:
                    actual_str = "N/A"
                    in_range = "?"
                else:
                    actual_pct = sim * 100
                    actual_str = f"{actual_pct:.1f}%"
                    low, high = exp_range[0], exp_range[1]
                    in_range = "✓" if low <= actual_pct <= high else "✗"

        rows.append({
            "case": case_name,
            "expected": expected_str,
            "actual": actual_str,
            "in_range": in_range,
        })

    return rows


def print_table(rows):
    print()
    print("=" * 90)
    print("Tree-Sitter Python — batches (Python): Expected vs Actual Similarity")
    print("=" * 90)
    print()
    fmt = "{:<45} {:>12} {:>12} {:>8}"
    print(fmt.format("Case", "Expected", "Actual", "In Range"))
    print("-" * 90)
    for r in rows:
        print(fmt.format(r["case"][:44], r["expected"], r["actual"], r["in_range"]))
    print("-" * 90)
    print()


if __name__ == "__main__":
    rows = run_batches()
    print_table(rows)
