"""
Run copydetect on all batch directories (Python, C, C++, C#, Java, JavaScript)
and output a table with cases, expected, and actual similarity per language.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from plagiarism_detect_copydetect import compare_code_copydetect

# (batch_dir, language, batch_name_pattern)
BATCH_CONFIGS = [
    (os.path.join(os.path.dirname(__file__), "batches", "batches"), "python", "batch_{:02d}_{}"),
    (os.path.join(os.path.dirname(__file__), "batches_c"), "c", "batch_{:02d}_{}"),
    (os.path.join(os.path.dirname(__file__), "batches_cpp"), "cpp", "batch_{:02d}_{}"),
    (os.path.join(os.path.dirname(__file__), "batches_csharp"), "csharp", "batch_{:02d}_{}"),
    (os.path.join(os.path.dirname(__file__), "batches_java"), "java", "batch_{:02d}_{}"),
    (os.path.join(os.path.dirname(__file__), "batches_javascript"), "javascript", "batch_{:02d}_{}"),
]

# 14 cases: (num, suffix)
CASES = [
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

CASE_NAMES = {
    "01_exact_copy": "Exact Copy",
    "02_variable_renaming": "Variable Renaming",
    "03_whitespace_formatting": "Whitespace or Formatting",
    "04_comment_addition": "Comment Addition or Removal",
    "04_comment_addition_removal": "Comment Addition or Removal",
    "05_function_extraction": "Function Extraction",
    "06_loop_type_change": "Loop Type Changes (for ↔ while)",
    "07_recursive_iterative": "Recursive vs Iterative",
    "08_minor_logic_modification": "Minor Logic Modification",
    "09_dead_code_insertion": "Dead Code Insertion",
    "10_code_reordering": "Code Reordering",
    "11_partial_copy": "Partial Copy",
    "12_template_skeleton": "Template or Skeleton Use",
    "13_different_implementation_same_algorithm": "Different Impl, Same Algorithm",
    "14_completely_different_logic": "Completely Different Logic",
}


def load_batch(batch_dir, batch_name):
    """Load ref and compare from a batch setup_batch.py."""
    setup_path = os.path.join(batch_dir, batch_name, "setup_batch.py")
    if not os.path.exists(setup_path):
        return None
    try:
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location("setup_batch", setup_path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.setup_batch()
    except Exception:
        return None


def run_copydetect(ref_code, compare_code, language):
    """Run copydetect and return similarity as percentage string or error."""
    try:
        result = compare_code_copydetect(
            "ref", ref_code,
            [{"id": "compare", "code": compare_code}],
            language=language,
        )
    except Exception as e:
        return f"ERR:{str(e)[:15]}"

    if not result.get("available"):
        return result.get("error", "N/A")[:20]

    res_list = result.get("results", [])
    if not res_list:
        return "N/A"
    sim = res_list[0].get("similarity")
    if sim is None:
        return "N/A"
    err = res_list[0].get("error")
    if err:
        return err[:20]
    return f"{sim * 100:.1f}%"


def run_all():
    """Run copydetect for all cases and all languages. Return rows and columns."""
    lang_names = ["Python", "C", "C++", "C#", "Java", "JavaScript"]
    rows = []

    for case_num, case_suffix in CASES:
        batch_name = f"batch_{case_num:02d}_{case_suffix}"
        case_key = f"{case_num:02d}_{case_suffix}"
        case_display = CASE_NAMES.get(case_key, case_key.replace("_", " ").title())

        # Use Python batch for expected (or first available)
        expected_str = "N/A"
        actuals = []

        for batch_dir, language, _ in BATCH_CONFIGS:
            data = load_batch(batch_dir, batch_name)
            if data is None:
                actuals.append("—")
                continue

            if expected_str == "N/A":
                exp_range = data.get("expected_similarity_range", (0, 0))
                expected_str = f"{exp_range[0]}-{exp_range[1]}%"

            ref_code = data.get("ref", "")
            compare_code = data.get("compare", "")
            actual = run_copydetect(ref_code, compare_code, language)
            actuals.append(actual)

        rows.append({
            "case": case_display,
            "expected": expected_str,
            "actuals": actuals,
        })

    return rows, lang_names


def print_table(rows, lang_names):
    """Print table with cases, expected, and actual per language."""
    col_w = 10
    fmt_parts = ["{:<38}", "{:>12}"]
    for _ in lang_names:
        fmt_parts.append(f"{{:>{col_w}}}")
    fmt = " ".join(fmt_parts)

    header = ["Case", "Expected"] + lang_names
    print()
    print("=" * (38 + 12 + len(lang_names) * (col_w + 1)))
    print("CopyDetect — Expected vs Actual Similarity (by Language)")
    print("=" * (38 + 12 + len(lang_names) * (col_w + 1)))
    print()
    print(fmt.format(*header))
    print("-" * (38 + 12 + len(lang_names) * (col_w + 1)))

    for r in rows:
        vals = [r["case"][:37], r["expected"]] + [a[:col_w] for a in r["actuals"]]
        print(fmt.format(*vals))

    print("-" * (38 + 12 + len(lang_names) * (col_w + 1)))
    print()


if __name__ == "__main__":
    rows, lang_names = run_all()
    print_table(rows, lang_names)
