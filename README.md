# Plagiarism Detector

Deployable plagiarism detection service with a basic web UI. Compares main student code against other students' submissions using multiple detection tools.

## Request Format

```json
{
  "main_student": {
    "id": "student_001",
    "code": "def find_max(arr):\n    return max(arr) if arr else None"
  },
  "other_students": [
    {"id": "student_002", "code": "def find_max(arr):\n    return max(arr) if arr else None"},
    {"id": "student_003", "code": "def get_maximum(nums):\n    m = nums[0]\n    for n in nums:\n        if n > m: m = n\n    return m"}
  ],
  "language": "python",
  "tools": ["copydetect", "difflib", "treesitter_python", "treesitter_cpp"]
}
```

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `main_student` | object | Yes | `{ "id": str, "code": str }` - Main student ID and code content |
| `other_students` | array | Yes | List of `{ "id": str, "code": str }` - Other students to compare against |
| `language` | string | No | `"python"` or `"cpp"` (default: `"python"`) |
| `tools` | array | No | Tools to run. Omit for all. Options: `copydetect`, `difflib`, `treesitter_python`, `treesitter_cpp` |

## Response Format

```json
{
  "main_student_id": "student_001",
  "comparisons": [
    {
      "tool": "copydetect",
      "available": true,
      "main_student_id": "student_001",
      "results": [
        {
          "other_student_id": "student_002",
          "similarity": 0.95,
          "similarity_main": 0.92,
          "similarity_other": 0.98,
          "token_overlap": 42
        }
      ]
    },
    {
      "tool": "difflib",
      "available": true,
      "results": [
        {
          "other_student_id": "student_002",
          "similarity": 0.85,
          "ratio": 0.85,
          "quick_ratio": 0.85,
          "ratio_normalized": 0.82
        }
      ]
    }
  ]
}
```

## Detection Tools

| Tool | Description |
|------|-------------|
| **copydetect** | Winnowing algorithm (MOSS-style), token-based fingerprinting. Best for structural similarity. |
| **difflib** | SequenceMatcher (Ratcliff-Obershelp). Character-level similarity. |
| **treesitter_python** | AST structure comparison for Python code. |
| **treesitter_cpp** | AST structure comparison for C++ code. |

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 for the UI, or POST to `http://localhost:5000/api/detect` for API access.
