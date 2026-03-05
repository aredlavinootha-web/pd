"""
Plagiarism Scoring Engine
Provides balanced, multi-method scoring with proper weight distribution.
Ported from scoringEngine.js.
"""

import code_normalizer


WEIGHTS = {
    "semantic_embeddings": 0.25,
    "copydetect": 0.50,
    "treesitter": 0.25,
    "difflib": 0,
}


def _calculate_confidence(score: float, method_count: int) -> str:
    if score >= 0.90 and method_count >= 3:
        return "very_high"
    if score >= 0.85 and method_count >= 2:
        return "high"
    if score >= 0.75:
        return "high"
    if score >= 0.65:
        return "medium"
    if score >= 0.50:
        return "low"
    return "very_low"


def calculate_weighted_score(
    local_result: dict | None,
    external_result: dict | None,
    options: dict | None = None,
) -> dict:
    options = options or {}
    scores = {"semantic_embeddings": 0.0, "copydetect": 0.0, "treesitter": 0.0, "difflib": 0.0}
    available = {"semantic_embeddings": False, "copydetect": False, "treesitter": False, "difflib": False}

    if local_result is not None:
        max_sim = local_result.get("max_similarity")
        if max_sim is not None:
            scores["semantic_embeddings"] = max(0.0, min(1.0, max_sim))
            available["semantic_embeddings"] = True
        elif local_result.get("has_matches") is False:
            scores["semantic_embeddings"] = 0.0
            available["semantic_embeddings"] = True

    if external_result and external_result.get("comparisons"):
        for comp in external_result["comparisons"]:
            if not comp.get("available") or not comp.get("results"):
                continue
            max_sim = max((r.get("similarity", 0) for r in comp["results"]), default=0)
            tool = comp.get("tool", "")
            if tool == "copydetect":
                scores["copydetect"] = max(0.0, min(1.0, max_sim))
                available["copydetect"] = True
            elif tool.startswith("treesitter"):
                scores["treesitter"] = max(0.0, min(1.0, max_sim))
                available["treesitter"] = True
            elif tool == "difflib":
                scores["difflib"] = max(0.0, min(1.0, max_sim))
                available["difflib"] = True

    total_weight = 0.0
    weighted_sum = 0.0
    for method, weight in WEIGHTS.items():
        if available[method]:
            weighted_sum += scores[method] * weight
            total_weight += weight

    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    structural_penalty = 1.0
    if options.get("current_code") and options.get("compared_code") and options.get("language"):
        penalty_result = code_normalizer.calculate_structural_penalty(
            options["current_code"], options["compared_code"], options["language"]
        )
        structural_penalty = penalty_result["penalty_factor"]
        penalty_details = penalty_result
        overall_score *= structural_penalty

    method_count = sum(1 for v in available.values() if v)

    breakdown = {}
    for method in WEIGHTS:
        breakdown[method] = {
            "score": scores[method],
            "weight": WEIGHTS[method],
            "contribution": scores[method] * WEIGHTS[method] if available[method] else 0,
            "available": available[method],
        }

    return {
        "overall_score": max(0.0, min(1.0, overall_score)),
        "structural_penalty": structural_penalty,
        "breakdown": breakdown,
        "method_count": method_count,
        "confidence": _calculate_confidence(overall_score, method_count),
    }


def classify_plagiarism_type(score_data: dict) -> dict:
    breakdown = score_data["breakdown"]
    overall_score = score_data["overall_score"]
    structural_penalty = score_data["structural_penalty"]

    embedding = breakdown["semantic_embeddings"]["score"]
    copy = breakdown["copydetect"]["score"]
    ast = breakdown["treesitter"]["score"]
    diff = breakdown["difflib"]["score"]

    has_structural_difference = structural_penalty < 0.85

    if copy >= 0.95 and ast >= 0.95 and diff >= 0.90:
        return {"type": "exact_copy", "severity": "critical", "explanation": "Nearly identical code detected across all checks"}
    if ast >= 0.90 and copy >= 0.80 and diff < 0.70:
        return {"type": "variable_rename", "severity": "high", "explanation": "Same structure and logic, different variable names"}
    if ast >= 0.80 and embedding >= 0.75 and copy < 0.70:
        return {"type": "structural_similarity", "severity": "medium", "explanation": "Similar algorithmic approach and structure"}
    if has_structural_difference and embedding >= 0.70:
        return {"type": "different_implementation", "severity": "low", "explanation": "Similar logic but different code organization (function decomposition, structure)"}
    if embedding >= 0.85 and ast < 0.60 and copy < 0.60:
        return {"type": "template_code", "severity": "low", "explanation": "High semantic similarity but different implementation (likely template/starter code)"}
    if embedding >= 0.70 and ast < 0.65 and (copy < 0.60 or diff < 0.60):
        return {"type": "logic_transformation", "severity": "medium", "explanation": "Same logic with different control flow (e.g., recursive vs iterative)"}
    if overall_score < 0.50:
        return {"type": "different_implementation", "severity": "none", "explanation": "Different implementations with minimal similarity"}

    return {"type": "moderate_similarity", "severity": "medium", "explanation": "Some similarity detected across multiple checks"}


def generate_plagiarism_report(
    local_result: dict | None,
    external_result: dict | None,
    threshold: float = 0.75,
    options: dict | None = None,
) -> dict:
    score_data = calculate_weighted_score(local_result, external_result, options)
    classification = classify_plagiarism_type(score_data)
    overall_score = score_data["overall_score"]
    is_plagiarism = overall_score >= threshold

    detection_methods: list[str] = []
    reasoning: list[str] = []

    bd = score_data["breakdown"]
    if bd["semantic_embeddings"]["available"]:
        detection_methods.append("semantic_embeddings")
        reasoning.append(f"Semantic similarity: {bd['semantic_embeddings']['score'] * 100:.1f}%")
    if bd["copydetect"]["available"]:
        detection_methods.append("copydetect")
        reasoning.append(f"Copy detection: {bd['copydetect']['score'] * 100:.1f}%")
    if bd["treesitter"]["available"]:
        detection_methods.append("treesitter_ast")
        reasoning.append(f"AST similarity: {bd['treesitter']['score'] * 100:.1f}%")
    if bd["difflib"]["available"]:
        detection_methods.append("difflib")
        reasoning.append(f"Text similarity: {bd['difflib']['score'] * 100:.1f}%")

    if is_plagiarism:
        display_msg = f"Plagiarism detected with {overall_score * 100:.1f}% similarity ({classification['type']})"
    elif overall_score > 0.01:
        display_msg = f"Low similarity: {overall_score * 100:.1f}% ({classification['type']}) - Below {threshold * 100:.0f}% threshold"
    else:
        display_msg = "No significant similarity detected"

    return {
        "plagiarism_detected": is_plagiarism,
        "overall_score": overall_score,
        "overall_percentage": f"{overall_score * 100:.1f}%",
        "plagiarism_type": classification["type"],
        "severity": classification["severity"],
        "confidence": score_data["confidence"],
        "method_count": score_data["method_count"],
        "score_breakdown": score_data["breakdown"],
        "detection_methods": detection_methods,
        "reasoning": reasoning,
        "threshold": threshold,
        "is_above_threshold": is_plagiarism,
        "explanation": classification["explanation"],
        "structural_penalty": score_data["structural_penalty"],
        "structural_penalty_applied": score_data["structural_penalty"] < 1.0,
        "display_message": display_msg,
    }
