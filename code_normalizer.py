"""
Code Normalizer Module
Normalizes code to reduce impact of variable names and cosmetic differences.
Helps embeddings focus on logic and structure rather than naming.
Ported from codeNormalizer.js.
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

KEYWORDS = {
    "python": {
        "def", "class", "if", "else", "elif", "for", "while", "return",
        "import", "from", "True", "False", "None", "print", "len", "range",
        "str", "int", "float", "list", "dict", "set",
    },
    "javascript": {
        "function", "const", "let", "var", "if", "else", "for", "while",
        "return", "import", "export", "class", "true", "false", "null",
        "undefined", "console", "log",
    },
    "java": {
        "public", "private", "protected", "class", "interface", "void",
        "static", "final", "return", "if", "else", "for", "while", "true",
        "false", "null", "System", "out", "println", "new", "this", "super",
        "extends", "implements", "try", "catch", "throw", "throws",
    },
    "cpp": {
        "class", "public", "private", "return", "if", "else", "for", "while",
        "true", "false", "nullptr", "std", "cout", "cin", "include", "using",
        "namespace", "struct", "template", "typename",
    },
}

VARIABLE_PATTERNS = {
    "python": [
        r"def\s+([a-z_][a-z0-9_]*)\s*\(",
        r"for\s+([a-z_][a-z0-9_]*)\s+in\b",
        r"\b([a-z_][a-z0-9_]*)\s*=(?!=)",
        r"\(([a-z_][a-z0-9_]*)\s*[,\)]",
    ],
    "javascript": [
        r"\b(?:const|let|var)\s+([a-z_$][a-z0-9_$]*)",
        r"function\s+([a-z_$][a-z0-9_$]*)\s*\(",
        r"\(([a-z_$][a-z0-9_$]*)\s*(?:,|\))",
    ],
    "java": [
        r"\b(?:public|private|protected|static|final)\s+[\w<>\[\]\s,?]+\s+([a-z_][a-z0-9_]*)\s*\(",
        r"\b(?:int|long|short|byte|char|String|boolean|double|float)\s+([a-z_][a-z0-9_]*)",
        r"\b(?:List|Map|Set|ArrayList|HashMap|HashSet)\s*<[^>]*>\s+([a-z_][a-z0-9_]*)",
        r"\b([a-z_][a-z0-9_]*)\s*=(?!=)",
        r"\(([a-z_][a-z0-9_]*)\s*[,\)]",
    ],
    "cpp": [
        r"\b(?:int|long|short|char|unsigned|size_t|string|bool|double|float|auto|void)\s+([a-z_][a-z0-9_]*)",
        r"\b(?:vector|map|set|unordered_map)\s*<[^>]*>\s+([a-z_][a-z0-9_]*)",
        r"\b([a-z_][a-z0-9_]*)\s*=(?!=)",
        r"\(([a-z_][a-z0-9_]*)\s*[,\)]",
    ],
}


def resolve_language(lang: str) -> str:
    if not lang:
        return "javascript"
    return LANGUAGE_ALIASES.get(lang.lower(), lang.lower())


def _is_common_keyword(name: str, language: str) -> bool:
    lang_keywords = KEYWORDS.get(language, KEYWORDS["javascript"])
    return name in lang_keywords


def normalize_variable_names(code: str, language: str) -> str:
    try:
        normalized = code
        variable_map: dict[str, str] = {}
        var_counter = 0

        lang = resolve_language(language)
        lang_patterns = VARIABLE_PATTERNS.get(lang, VARIABLE_PATTERNS["javascript"])

        for pattern in lang_patterns:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                var_name = match.group(1)
                if not _is_common_keyword(var_name, lang) and var_name not in variable_map:
                    variable_map[var_name] = f"var{var_counter}"
                    var_counter += 1

        sorted_vars = sorted(variable_map.keys(), key=len, reverse=True)
        for original_name in sorted_vars:
            generic_name = variable_map[original_name]
            normalized = re.sub(rf"\b{re.escape(original_name)}\b", generic_name, normalized)

        return normalized
    except Exception:
        return code


def _remove_comments(code: str, language: str) -> str:
    try:
        result = code
        if language == "python":
            result = re.sub(r"#[^\n]*", "", result)
            result = re.sub(r'"""[\s\S]*?"""', "", result)
            result = re.sub(r"'''[\s\S]*?'''", "", result)
        else:
            result = re.sub(r"//[^\n]*", "", result)
            result = re.sub(r"/\*[\s\S]*?\*/", "", result)
        return result
    except Exception:
        return code


def normalize_code(code: str, language: str = "javascript") -> str:
    try:
        lang = resolve_language(language)
        normalized = code.strip()
        normalized = normalized.replace("\r\n", "\n")
        normalized = normalized.replace("\t", "  ")
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = _remove_comments(normalized, lang)
        normalized = re.sub(r'"[^"]*"', '"STRING"', normalized)
        normalized = re.sub(r"'[^']*'", "'STRING'", normalized)
        normalized = normalize_variable_names(normalized, lang)
        return normalized
    except Exception:
        return code


def create_semantic_signature(code: str, language: str) -> str:
    try:
        signature = []
        if_count = len(re.findall(r"\bif\b", code))
        for_count = len(re.findall(r"\bfor\b", code))
        while_count = len(re.findall(r"\bwhile\b", code))
        return_count = len(re.findall(r"\breturn\b", code))
        signature.append(f"control:if={if_count},for={for_count},while={while_count},return={return_count}")

        if language == "python":
            def_count = len(re.findall(r"\bdef\s+\w+\s*\(", code))
            signature.append(f"functions:{def_count}")
        else:
            func_count = len(re.findall(r"function\s+\w+\s*\(|=>\s*\{", code))
            signature.append(f"functions:{func_count}")

        lines = [l for l in code.split("\n") if l.strip()]
        signature.append(f"lines:{len(lines)}")
        return " ".join(signature)
    except Exception:
        return ""


def prepare_dual_code(code: str, language: str = "javascript") -> dict:
    return {
        "original": code,
        "normalized": normalize_code(code, language),
        "semantic_signature": create_semantic_signature(code, language),
    }


def analyze_structure(code: str, language: str = "javascript") -> dict:
    lines = [l for l in code.split("\n") if l.strip()]
    stats = {
        "lines": len(lines),
        "conditionals": len(re.findall(r"\b(if|elif|else|switch|case)\b", code)),
        "loops": len(re.findall(r"\b(for|while|do)\b", code)),
        "returns": len(re.findall(r"\breturn\b", code)),
        "functions": 0,
        "classes": 0,
    }

    lang = resolve_language(language)
    if lang == "python":
        stats["functions"] = len(re.findall(r"\bdef\s+\w+\s*\(", code))
        stats["classes"] = len(re.findall(r"\bclass\s+\w+", code))
    elif lang == "java":
        stats["functions"] = len(
            re.findall(
                r"\b(?:public|private|protected|static|final|abstract|synchronized)\s+[\w<>\[\]\s,?]+\s+\w+\s*\(",
                code,
            )
        )
        stats["classes"] = len(re.findall(r"\bclass\s+\w+", code))
    elif lang in ("cpp", "c"):
        stats["functions"] = len(
            re.findall(r"(?:^|\n)\s*(?:[\w:*&<>\[\]\s]+\s+)+\w+\s*\([^)]*\)\s*\{", code)
        )
        stats["classes"] = len(re.findall(r"\bclass\s+\w+", code))
    else:
        stats["functions"] = len(
            re.findall(
                r"\bfunction\s+\w+\s*\(|\w+\s*:\s*function\s*\(|\w+\s*=\s*function\s*\(|=>\s*\{",
                code,
            )
        )
        stats["classes"] = len(re.findall(r"\bclass\s+\w+", code))

    return stats


def calculate_structural_penalty(
    code1: str, code2: str, language: str = "javascript"
) -> dict:
    struct1 = analyze_structure(code1, language)
    struct2 = analyze_structure(code2, language)
    func_diff = abs(struct1["functions"] - struct2["functions"])

    if func_diff >= 3:
        penalty_factor = 0.3
    elif func_diff == 2:
        penalty_factor = 0.5
    elif func_diff == 1:
        penalty_factor = 0.75
    else:
        penalty_factor = 1.0

    return {
        "penalty_factor": penalty_factor,
        "func_diff": func_diff,
        "struct1": struct1,
        "struct2": struct2,
    }
