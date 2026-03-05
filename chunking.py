"""
Code Chunking Module
Splits code into semantic chunks (functions, blocks) for fine-grained similarity detection.
Ported from chunking.js.
"""

import re

LANGUAGE_ALIASES = {
    "js": "javascript",
    "ts": "javascript",
    "typescript": "javascript",
    "py": "python",
    "c++": "cpp",
    "cc": "cpp",
}


def _resolve_language(lang: str) -> str:
    return LANGUAGE_ALIASES.get(lang.lower(), lang) if lang else "javascript"


def extract_javascript_functions(code: str) -> list[dict]:
    chunks: list[dict] = []
    lines = code.split("\n")

    patterns = [
        re.compile(r"^\s*function\s+(\w+)\s*\("),
        re.compile(r"^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"),
        re.compile(r"^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(\w+)\s*=>"),
        re.compile(r"^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?function\s*\("),
        re.compile(r"^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{"),
        re.compile(r"^\s*export\s+(?:async\s+)?function\s+(\w+)\s*\("),
        re.compile(r"^\s*export\s+const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"),
    ]

    current_chunk = None
    brace_depth = 0
    chunk_index = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()

        if current_chunk is None and (trimmed == "" or trimmed.startswith("//")):
            continue

        if current_chunk is None:
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    current_chunk = {
                        "index": chunk_index,
                        "start_line": i,
                        "name": match.group(1) or "anonymous",
                        "type": "function",
                        "_lines": [line],
                    }
                    chunk_index += 1
                    brace_depth = line.count("{") - line.count("}")
                    break
        else:
            current_chunk["_lines"].append(line)
            brace_depth += line.count("{") - line.count("}")

            if brace_depth <= 0:
                current_chunk["text"] = "\n".join(current_chunk.pop("_lines"))
                current_chunk["end_line"] = i
                chunks.append(current_chunk)
                current_chunk = None
                brace_depth = 0

    if current_chunk:
        current_chunk["text"] = "\n".join(current_chunk.pop("_lines"))
        current_chunk["end_line"] = len(lines) - 1
        chunks.append(current_chunk)

    return chunks


def extract_python_functions(code: str) -> list[dict]:
    chunks: list[dict] = []
    lines = code.split("\n")
    current_chunk = None
    chunk_index = 0

    def flush_chunk(up_to_line: int):
        nonlocal current_chunk
        if current_chunk is None:
            return
        current_chunk["text"] = "\n".join(current_chunk.pop("_lines")).rstrip()
        current_chunk["end_line"] = up_to_line
        chunks.append(current_chunk)
        current_chunk = None

    for i, line in enumerate(lines):
        trimmed = line.strip()
        indent = len(line) - len(line.lstrip()) if trimmed else None

        top_level_match = None
        if indent == 0:
            top_level_match = re.match(r"^(def|class)\s+(\w+)", trimmed)

        if top_level_match:
            flush_chunk(i - 1)
            current_chunk = {
                "index": chunk_index,
                "start_line": i,
                "name": top_level_match.group(2),
                "type": "class" if top_level_match.group(1) == "class" else "function",
                "_lines": [line],
            }
            chunk_index += 1
        elif current_chunk is not None:
            if indent == 0 and trimmed and not trimmed.startswith("#"):
                flush_chunk(i - 1)
            else:
                current_chunk["_lines"].append(line)

    flush_chunk(len(lines) - 1)
    return chunks


def extract_brace_based_functions(code: str, patterns: list[re.Pattern]) -> list[dict]:
    chunks: list[dict] = []
    lines = code.split("\n")
    current_chunk = None
    brace_depth = 0
    chunk_index = 0

    def _is_comment(trimmed: str) -> bool:
        return trimmed.startswith("//") or trimmed.startswith("/*") or trimmed.startswith("*")

    for i, line in enumerate(lines):
        trimmed = line.strip()

        if current_chunk is None:
            if trimmed == "" or _is_comment(trimmed):
                continue
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    current_chunk = {
                        "index": chunk_index,
                        "start_line": i,
                        "name": match.group(1) or "anonymous",
                        "type": "function",
                        "_lines": [line],
                    }
                    chunk_index += 1
                    brace_depth = line.count("{") - line.count("}")
                    break
        else:
            current_chunk["_lines"].append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                current_chunk["text"] = "\n".join(current_chunk.pop("_lines"))
                current_chunk["end_line"] = i
                chunks.append(current_chunk)
                current_chunk = None
                brace_depth = 0

    if current_chunk:
        current_chunk["text"] = "\n".join(current_chunk.pop("_lines"))
        current_chunk["end_line"] = len(lines) - 1
        chunks.append(current_chunk)

    return chunks


JAVA_METHOD_PATTERNS = [
    re.compile(
        r"^\s*(?:(?:public|private|protected|static|final|abstract|synchronized)\s+)*[\w<>\[\]\s,?]+\s+(\w+)\s*\("
    ),
]

C_CPP_METHOD_PATTERNS = [
    re.compile(r"^\s*(?:[\w:*&<>\[\]\s]+\s+)+(\w+)\s*\([^)]*\)\s*\{?"),
]


def filter_trivial_chunks(
    chunks: list[dict], min_lines: int = 3, min_chars: int = 50
) -> list[dict]:
    filtered = []
    for chunk in chunks:
        text = chunk.get("text", "")
        line_count = len(text.split("\n"))
        char_count = len(text.strip())
        if line_count < min_lines or char_count < min_chars:
            continue
        code_no_ws = re.sub(r"\s+", "", text)
        if re.match(r"^(const|let|var)\w+=\(\)=>\{\}$", code_no_ws):
            continue
        filtered.append(chunk)
    return filtered


def extract_code_chunks(code: str, language: str = "javascript") -> list[dict]:
    if not code or not code.strip():
        return []

    lang = _resolve_language(language)
    chunks: list[dict] = []

    if lang == "javascript":
        chunks = extract_javascript_functions(code)
    elif lang == "python":
        chunks = extract_python_functions(code)
        if not chunks:
            chunks = [{"index": 0, "text": code, "type": "whole", "name": "main"}]
    elif lang == "java":
        chunks = extract_brace_based_functions(code, JAVA_METHOD_PATTERNS)
        if not chunks:
            chunks = [{"index": 0, "text": code, "type": "whole", "name": "main"}]
    elif lang in ("cpp", "c"):
        chunks = extract_brace_based_functions(code, C_CPP_METHOD_PATTERNS)
        if not chunks:
            chunks = [{"index": 0, "text": code, "type": "whole", "name": "main"}]
    else:
        chunks = [{"index": 0, "text": code, "type": "whole", "name": "main"}]

    filtered = filter_trivial_chunks(chunks)
    for i, chunk in enumerate(filtered):
        chunk["index"] = i
    return filtered


def sliding_window_chunks(
    code: str, lines_per_chunk: int = 20, overlap_lines: int = 5
) -> list[dict]:
    lines = code.split("\n")
    chunks: list[dict] = []
    chunk_index = 0
    step = lines_per_chunk - overlap_lines

    for i in range(0, len(lines), step):
        chunk_lines = lines[i : i + lines_per_chunk]
        if chunk_lines:
            chunks.append({
                "index": chunk_index,
                "text": "\n".join(chunk_lines),
                "type": "window",
                "start_line": i,
                "end_line": min(i + lines_per_chunk - 1, len(lines) - 1),
            })
            chunk_index += 1

    return chunks


def get_chunk_stats(chunks: list[dict]) -> dict:
    if not chunks:
        return {"count": 0, "totalChars": 0, "avgChars": 0, "avgLines": 0}

    total_chars = sum(len(c.get("text", "")) for c in chunks)
    total_lines = sum(len(c.get("text", "").split("\n")) for c in chunks)
    types: dict[str, int] = {}
    for c in chunks:
        t = c.get("type", "unknown")
        types[t] = types.get(t, 0) + 1

    return {
        "count": len(chunks),
        "totalChars": total_chars,
        "avgChars": round(total_chars / len(chunks)),
        "avgLines": round(total_lines / len(chunks)),
        "types": types,
    }
