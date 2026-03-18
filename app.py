"""
Plagiarism Detector - Deployable Flask application with basic UI.
Combines tool-based detection (copydetect, tree-sitter, difflib) with
semantic embedding search (OpenAI + Pinecone) and a scoring engine.
"""

import json
import time
import logging
import uuid
from datetime import datetime
import concurrent.futures

from flask import Flask, request, render_template_string, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from dotenv import load_dotenv

try:
    import numpy as _np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


class _SafeJSONProvider(DefaultJSONProvider):
    """Handle numpy types that the default encoder cannot serialize."""

    def default(self, o):
        if _HAS_NUMPY:
            if isinstance(o, _np.integer):
                return int(o)
            if isinstance(o, _np.floating):
                return float(o)
            if isinstance(o, _np.bool_):
                return bool(o)
            if isinstance(o, _np.ndarray):
                return o.tolist()
        return super().default(o)


load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from plagiarism_detect_copydetect import compare_code_copydetect, compare_all_pairs_copydetect
from plagiarism_detect_difflib import compare_code_difflib
from plagiarism_detect_treesitter_python import compare_code_treesitter_python
from plagiarism_detect_treesitter_cpp import compare_code_treesitter_cpp
from plagiarism_detect_treesitter_java import compare_code_treesitter_java
from plagiarism_detect_treesitter_c import compare_code_treesitter_c
from plagiarism_detect_treesitter_csharp import compare_code_treesitter_csharp
from plagiarism_detect_treesitter_javascript import compare_code_treesitter_javascript

import embeddings
import chunking
import vector_db
import scoring_engine
import code_normalizer

app = Flask(__name__)
app.json_provider_class = _SafeJSONProvider
app.json = _SafeJSONProvider(app)
CORS(app, resources={r"/*": {"origins": "*"}})

pinecone_ok = False
try:
    pinecone_ok = vector_db.initialize_index()
except Exception as _init_err:
    logger.warning(f"Pinecone init failed (non-fatal): {_init_err}")
logger.info(f"Pinecone at startup: {'OK' if pinecone_ok else 'NOT CONFIGURED'}")


def _summarize_other_students_code(other_students: list) -> dict:
    """Lengths only — safe for large payloads (e.g. 2500+ char code)."""
    if not other_students:
        return {"count": 0}
    lens = [len(str(o.get("code", "") or "")) for o in other_students]
    return {
        "count": len(other_students),
        "code_len_min": min(lens),
        "code_len_max": max(lens),
        "code_len_sum": sum(lens),
    }


# Request schema:
# {
#   "main_student": { "id": str, "code": str },
#   "other_students": [ { "id": str, "code": str }, ... ],
#   "language": "python" | "cpp" (optional, default "python"),
#   "tools": ["copydetect", "difflib", "treesitter_python", "treesitter_cpp"] (optional, all if omitted)
# }

# Response schema:
# {
#   "main_student_id": str,
#   "comparisons": [
#     { "tool": str, "available": bool, "results": [...], "error"?: str },
#     ...
#   ]
# }


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plagiarism Detector</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f0f12;
            --bg-secondary: #18181c;
            --bg-card: #1e1e24;
            --border: #2a2a32;
            --text-primary: #e4e4e7;
            --text-muted: #a1a1aa;
            --accent: #6366f1;
            --accent-hover: #818cf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }
        .container { max-width: 960px; margin: 0 auto; padding: 2rem; }
        h1 {
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--accent), #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem; }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .card h2 { font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-primary); }
        label { display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.35rem; }
        input, select, textarea {
            width: 100%;
            padding: 0.6rem 0.85rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }
        textarea { min-height: 120px; resize: vertical; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.65rem 1.25rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: var(--accent-hover); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .tools-check { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 0.5rem; }
        .tools-check label { display: flex; align-items: center; gap: 0.4rem; margin: 0; cursor: pointer; }
        .tools-check input { width: auto; }
        #results { margin-top: 2rem; }
        .tool-result {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        .tool-result h3 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .tool-result h3 .badge {
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-weight: 500;
        }
        .badge-ok { background: rgba(34, 197, 94, 0.2); color: var(--success); }
        .badge-err { background: rgba(239, 68, 68, 0.2); color: var(--error); }
        .result-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        .result-table th, .result-table td {
            padding: 0.6rem 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        .result-table th { color: var(--text-muted); font-weight: 500; }
        .result-table tr:last-child td { border-bottom: none; }
        .similarity { font-family: 'JetBrains Mono', monospace; font-weight: 500; }
        .similarity-high { color: var(--warning); }
        .similarity-very-high { color: var(--error); }
        .error-msg { color: var(--error); font-size: 0.85rem; }
        .api-info {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
        }
        .api-info code { background: var(--bg-secondary); padding: 0.15rem 0.4rem; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Plagiarism Detector</h1>
        <p class="subtitle">Compare main student code against other submissions using multiple detection tools</p>

        <form id="detectForm" class="card">
            <h2>Main Student</h2>
            <div class="row">
                <div>
                    <label for="mainId">Student ID</label>
                    <input type="text" id="mainId" name="main_id" placeholder="e.g. student_001" required>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <label for="mainCode">Code Content</label>
                <textarea id="mainCode" name="main_code" placeholder="Paste main student code here..." required></textarea>
            </div>

            <h2 style="margin-top: 1.5rem;">Other Students</h2>
            <div style="margin-top: 0.5rem;">
                <label for="otherStudents">JSON: List of { "id": "student_002", "code": "..." }</label>
                <textarea id="otherStudents" name="other_students" placeholder='[{"id": "student_002", "code": "def foo(): pass"}, {"id": "student_003", "code": "..."}]'></textarea>
            </div>

            <div class="row" style="margin-top: 1rem;">
                <div>
                    <label>Language</label>
                    <select id="language" name="language">
                        <option value="python">Python</option>
                        <option value="cpp">C++</option>
                    </select>
                </div>
                <div>
                    <label>Detection Tools</label>
                    <div class="tools-check">
                        <label><input type="checkbox" name="tools" value="copydetect" checked> CopyDetect</label>
                        <label><input type="checkbox" name="tools" value="difflib" checked> Difflib</label>
                        <label><input type="checkbox" name="tools" value="treesitter_python" checked> Tree-Sitter (Python)</label>
                        <label><input type="checkbox" name="tools" value="treesitter_cpp" checked> Tree-Sitter (C++)</label>
                    </div>
                </div>
            </div>

            <div style="margin-top: 1.5rem;">
                <button type="submit" class="btn" id="submitBtn">Run Detection</button>
            </div>
        </form>

        <div id="results"></div>

        <div class="api-info">
            <strong>API:</strong> POST /api/detect with JSON body: <code>{"main_student": {"id": "...", "code": "..."}, "other_students": [{"id": "...", "code": "..."}], "language": "python", "tools": ["copydetect", "difflib", "treesitter_python", "treesitter_cpp"]}</code>
        </div>
    </div>

    <script>
        document.getElementById('detectForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.textContent = 'Analyzing...';

            const mainId = document.getElementById('mainId').value.trim();
            const mainCode = document.getElementById('mainCode').value;
            let otherStudents;
            try {
                otherStudents = JSON.parse(document.getElementById('otherStudents').value || '[]');
            } catch (err) {
                alert('Invalid JSON in Other Students field');
                btn.disabled = false;
                btn.textContent = 'Run Detection';
                return;
            }
            const language = document.getElementById('language').value;
            const tools = Array.from(document.querySelectorAll('input[name="tools"]:checked')).map(c => c.value);

            const payload = {
                main_student: { id: mainId, code: mainCode },
                other_students: otherStudents,
                language,
                tools: tools.length ? tools : ['copydetect', 'difflib', 'treesitter_python', 'treesitter_cpp']
            };

            try {
                const res = await fetch('/api/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                renderResults(data);
            } catch (err) {
                document.getElementById('results').innerHTML = '<div class="card error-msg">Request failed: ' + err.message + '</div>';
            }
            btn.disabled = false;
            btn.textContent = 'Run Detection';
        });

        function similarityClass(sim) {
            if (sim >= 0.8) return 'similarity-very-high';
            if (sim >= 0.5) return 'similarity-high';
            return '';
        }

        function renderResults(data) {
            const container = document.getElementById('results');
            if (data.error) {
                container.innerHTML = '<div class="card error-msg">' + data.error + '</div>';
                return;
            }

            let html = '<h2 style="margin-bottom: 1rem;">Results</h2>';
            for (const comp of data.comparisons || []) {
                const avail = comp.available !== false;
                html += '<div class="tool-result">';
                html += '<h3>' + comp.tool + ' <span class="badge ' + (avail ? 'badge-ok' : 'badge-err') + '">' + (avail ? 'OK' : 'Unavailable') + '</span></h3>';
                if (comp.error) html += '<p class="error-msg">' + comp.error + '</p>';
                if (comp.results && comp.results.length) {
                    html += '<table class="result-table"><thead><tr><th>Other Student</th><th>Similarity</th><th>Details</th></tr></thead><tbody>';
                    for (const r of comp.results) {
                        const sim = (r.similarity !== undefined) ? (r.similarity * 100).toFixed(1) + '%' : '-';
                        let details = [];
                        if (r.token_overlap !== undefined) details.push('overlap: ' + r.token_overlap);
                        if (r.similarity_main !== undefined) details.push('main: ' + (r.similarity_main * 100).toFixed(1) + '%');
                        if (r.similarity_other !== undefined) details.push('other: ' + (r.similarity_other * 100).toFixed(1) + '%');
                        if (r.ratio_normalized !== undefined) details.push('norm: ' + (r.ratio_normalized * 100).toFixed(1) + '%');
                        if (r.error) details.push(r.error);
                        html += '<tr><td>' + r.other_student_id + '</td><td class="similarity ' + similarityClass(r.similarity || 0) + '">' + sim + '</td><td>' + (details.join(' | ') || '-') + '</td></tr>';
                    }
                    html += '</tbody></table>';
                } else if (!comp.error) {
                    html += '<p class="text-muted">No comparison results</p>';
                }
                html += '</div>';
            }
            container.innerHTML = html;
        }
    </script>
</body>
</html>
"""



@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)



@app.route("/api/detect", methods=["POST"])
def api_detect():
    req_id = uuid.uuid4().hex[:10]
    t0 = time.perf_counter()
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            logger.info("[API/detect] req_id=%s rejected: invalid JSON", req_id)
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        main_student = data.get("main_student")
        if not main_student:
            logger.info("[API/detect] req_id=%s rejected: missing main_student", req_id)
            return jsonify({"error": "Missing 'main_student' with 'id' and 'code'"}), 400

        main_id = main_student.get("id", "")
        main_code = main_student.get("code", "")
        other_students = data.get("other_students", [])
        language = data.get("language", "python")
        tools = data.get("tools", ["copydetect", "difflib", "treesitter_python", "treesitter_cpp"])
        max_results = data.get("maxResults")

        if not isinstance(other_students, list):
            logger.info("[API/detect] req_id=%s rejected: other_students not a list", req_id)
            return jsonify({"error": "'other_students' must be a list of {id, code}"}), 400

        if max_results is not None and (not isinstance(max_results, int) or max_results < 0):
            logger.info("[API/detect] req_id=%s rejected: bad max_results", req_id)
            return jsonify({"error": "'max_results' must be a non-negative integer"}), 400

        logger.info(
            "[API/detect] START req_id=%s main_id=%s main_code_len=%d others_summary=%s language=%s tools=%s max_results=%s",
            req_id,
            main_id,
            len(main_code or ""),
            _summarize_other_students_code(other_students),
            language,
            tools,
            max_results,
        )

        comparisons = []
        tool_map = {
            "copydetect": lambda: compare_code_copydetect(main_id, main_code, other_students, language),
            "difflib": lambda: compare_code_difflib(main_id, main_code, other_students),
            "treesitter_python": lambda: compare_code_treesitter_python(main_id, main_code, other_students),
            "treesitter_cpp": lambda: compare_code_treesitter_cpp(main_id, main_code, other_students),
            "treesitter_java": lambda: compare_code_treesitter_java(main_id, main_code, other_students),
            "treesitter_c": lambda: compare_code_treesitter_c(main_id, main_code, other_students),
            "treesitter_csharp": lambda: compare_code_treesitter_csharp(main_id, main_code, other_students),
            "treesitter_javascript": lambda: compare_code_treesitter_javascript(main_id, main_code, other_students),
        }

        for tool in tools:
            if tool in tool_map:
                t_tool = time.perf_counter()
                logger.info("[API/detect] req_id=%s tool=%s START", req_id, tool)
                comparisons.append(tool_map[tool]())
                comp = comparisons[-1]
                logger.info(
                    "[API/detect] req_id=%s tool=%s DONE elapsed=%.3fs available=%s result_count=%s err=%s",
                    req_id,
                    tool,
                    time.perf_counter() - t_tool,
                    comp.get("available"),
                    len(comp.get("results") or []),
                    (comp.get("error") or "")[:120] or None,
                )

        # If max_results is set, trim each tool's results to top N by that tool's similarity
        if max_results is not None and max_results > 0:
            for comp in comparisons:
                if comp.get("available") and comp.get("results"):
                    sorted_results = sorted(
                        comp["results"],
                        key=lambda r: r.get("similarity") if r.get("similarity") is not None else -1,
                        reverse=True,
                    )
                    comp["results"] = sorted_results[:max_results]

        response_body = {
            "main_student_id": main_id,
            "comparisons": comparisons,
        }
        logger.info(
            "[API/detect] END req_id=%s total_elapsed=%.3fs main_id=%s per_tool=%s",
            req_id,
            time.perf_counter() - t0,
            main_id,
            [
                (c.get("tool"), len(c.get("results") or []), c.get("available"))
                for c in comparisons
            ],
        )
        return jsonify(response_body)
    except Exception as e:
        logger.info("[API/detect] req_id=%s ERROR: %s", req_id, e)
        return jsonify({"error": str(e)}), 500


# All-pairs: compare every student with every other. Request body:
# { "students": [ { "id": str, "code": str }, ... ], "language": str (optional), "top_n": int (optional) }
# Response: pairs, top_matches_per_student (if top_n set), comparisons_count, students_count.
# Rough time for 1000 students (~50-line codes): ~2–6 minutes (fingerprinting + ~500k comparisons).


@app.route("/api/detect-all-pairs", methods=["POST"])
def api_detect_all_pairs():
    req_id = uuid.uuid4().hex[:10]
    t0 = time.perf_counter()
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            logger.info("[API/detect-all-pairs] req_id=%s invalid JSON", req_id)
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        students = data.get("students", [])
        if not isinstance(students, list):
            return jsonify({"error": "'students' must be a list of {id, code}"}), 400

        if len(students) < 2:
            logger.info("[API/detect-all-pairs] req_id=%s rejected: need >=2 students", req_id)
            return jsonify({"error": "At least 2 students required for all-pairs comparison"}), 400

        language = data.get("language", "python")
        top_n = data.get("top_n")
        if top_n is not None and (not isinstance(top_n, int) or top_n < 0):
            logger.info("[API/detect-all-pairs] req_id=%s rejected: bad top_n", req_id)
            return jsonify({"error": "'top_n' must be a non-negative integer"}), 400

        code_lens = [len(str(s.get("code", "") or "")) for s in students]
        logger.info(
            "[API/detect-all-pairs] START req_id=%s students=%d language=%s top_n=%s code_len_min/max/sum=%d/%d/%d",
            req_id,
            len(students),
            language,
            top_n,
            min(code_lens) if code_lens else 0,
            max(code_lens) if code_lens else 0,
            sum(code_lens),
        )

        result = compare_all_pairs_copydetect(
            students,
            language=language,
            top_n=top_n,
        )

        response_body = {
            "pairs": result.get("pairs", []),
            "comparisons_count": result.get("comparisons_count", 0),
            "students_count": result.get("students_count", 0),
        }
        if result.get("top_matches_per_student") is not None:
            response_body["top_matches_per_student"] = result["top_matches_per_student"]
        if not result.get("available"):
            response_body["error"] = result.get("error", "copydetect unavailable")
        if result.get("error"):
            response_body["error"] = result["error"]

        logger.info(
            "[API/detect-all-pairs] END req_id=%s elapsed=%.3fs comparisons_count=%s students_count=%s available=%s",
            req_id,
            time.perf_counter() - t0,
            response_body.get("comparisons_count"),
            response_body.get("students_count"),
            result.get("available"),
        )
        return jsonify(response_body)
    except Exception as e:
        logger.info("[API/detect-all-pairs] req_id=%s ERROR: %s", req_id, e)
        return jsonify({"error": str(e)}), 500


##############################################################################
# Semantic / Pinecone routes (ported from PlagDetectBackend Node.js)
##############################################################################


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "service": "semantic-plagiarism-detector",
        "model": embeddings.EMBEDDING_MODEL,
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """Submit code, generate embeddings, and store in Pinecone."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

        code = data.get("code", "")
        student_id = (data.get("studentId") or "").strip()
        question_id = (data.get("questionId") or "").strip()
        exam_id_raw = data.get("examId")
        exam_id = str(exam_id_raw).strip() if exam_id_raw and str(exam_id_raw).strip() else None
        language = data.get("language", "javascript")
        use_normalization = data.get("useNormalization", True)
        custom_api_key = request.headers.get("X-OpenAI-API-Key")

        if not code or not student_id or not question_id:
            return jsonify({"success": False, "error": "Missing required fields: code, studentId, questionId"}), 400
        if not code.strip():
            return jsonify({"success": False, "error": "Code cannot be empty"}), 400

        submission_id = f"{student_id}_{question_id}_{int(time.time() * 1000)}"
        logger.info(
            "[API/submit] studentId=%s questionId=%s code_len=%d language=%s normalization=%s",
            student_id,
            question_id,
            len(code),
            language,
            use_normalization,
        )

        whole_code_embedding = embeddings.generate_code_embedding(
            code, language, custom_api_key, use_normalization,
        )

        code_chunks = chunking.extract_code_chunks(code, language)
        chunks_with_embeddings = (
            embeddings.generate_chunk_embeddings(code_chunks, language, custom_api_key, use_normalization)
            if code_chunks else []
        )

        vector_db.save_submission({
            "submission_id": submission_id,
            "student_id": student_id,
            "question_id": question_id,
            "exam_id": exam_id,
            "code": code,
            "language": language,
            "embedding": whole_code_embedding,
            "chunks": chunks_with_embeddings,
        })

        chunk_stats = chunking.get_chunk_stats(code_chunks)
        logger.info(
            "[API/submit] DONE submissionId=%s chunkCount=%s",
            submission_id,
            len(code_chunks),
        )
        return jsonify({
            "success": True,
            "submissionId": submission_id,
            "chunkCount": len(code_chunks),
            "chunkStats": chunk_stats,
            "message": "Submission processed successfully",
        })
    except Exception as e:
        logger.error(f"[Submit Error] {e}")
        msg = str(e)
        if "Pinecone" in msg:
            return jsonify({"success": False, "error": "Vector database not configured. Please set PINECONE_API_KEY in your backend .env file. Get free API key from https://www.pinecone.io/", "errorType": "PINECONE_NOT_CONFIGURED"}), 503
        if "quota" in msg:
            return jsonify({"success": False, "error": 'OpenAI API quota exceeded. Please provide a valid API key with available credits using the "OpenAI API Key" field in the frontend.', "errorType": "QUOTA_EXCEEDED"}), 402
        if "API key" in msg:
            return jsonify({"success": False, "error": 'Invalid or missing OpenAI API key. Please provide a valid API key using the "OpenAI API Key" field in the frontend.', "errorType": "INVALID_API_KEY"}), 401
        return jsonify({"success": False, "error": msg}), 500


@app.route("/api/submit/bulk", methods=["POST"])
def api_submit_bulk():
    """Bulk upload submissions."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

        rows = data.get("submissions", [])
        use_normalization = data.get("useNormalization", True)
        custom_api_key = request.headers.get("X-OpenAI-API-Key")

        if not isinstance(rows, list) or len(rows) == 0:
            return jsonify({
                "success": False,
                "error": "Missing or empty 'submissions' array. Each row must have: exam_id, question_id, student_id, submission",
            }), 400

        logger.info("[API/submit/bulk] START rows=%d useNormalization=%s", len(rows), use_normalization)
        results = {"success": 0, "failed": 0, "errors": []}

        def process_row(index, row_data):
            exam_id_raw = row_data.get("exam_id")
            exam_id = str(exam_id_raw).strip() if exam_id_raw and str(exam_id_raw).strip() else None
            question_id = str(row_data.get("question_id", "")).strip()
            student_id = str(row_data.get("student_id", "")).strip()
            code_text = str(row_data.get("submission", ""))
            lang = str(row_data.get("language", "javascript")).strip() or "javascript"

            if not question_id or not student_id or not code_text or len(code_text.strip()) < 10:
                return {"status": "failed", "error": {"row": index + 1, "error": "Missing or invalid exam_id/question_id/student_id/submission (code min 10 chars)"}}

            try:
                submission_id = f"{student_id}_{question_id}_{int(time.time() * 1000)}_{index}"
                emb = embeddings.generate_code_embedding(code_text, lang, custom_api_key, use_normalization)
                code_chunks = chunking.extract_code_chunks(code_text, lang)
                chunks_emb = (
                    embeddings.generate_chunk_embeddings(code_chunks, lang, custom_api_key, use_normalization)
                    if code_chunks else []
                )
                vector_db.save_submission({
                    "submission_id": submission_id,
                    "student_id": student_id,
                    "question_id": question_id,
                    "exam_id": exam_id,
                    "code": code_text,
                    "language": lang,
                    "embedding": emb,
                    "chunks": chunks_emb,
                })
                return {"status": "success"}
            except Exception as err:
                return {"status": "failed", "error": {"row": index + 1, "error": str(err) or "Processing failed"}}

        # Use ThreadPoolExecutor to generate embeddings and save to Pinecone concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_row = {executor.submit(process_row, i, row): i for i, row in enumerate(rows)}
            for future in concurrent.futures.as_completed(future_to_row):
                res = future.result()
                if res["status"] == "success":
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(res["error"])

        logger.info(
            "[API/submit/bulk] END total=%d success=%d failed=%d",
            len(rows),
            results["success"],
            results["failed"],
        )
        return jsonify({
            "success": True,
            "total": len(rows),
            "successCount": results["success"],
            "failCount": results["failed"],
            "errors": results["errors"][:50],
            "message": f"Processed {len(rows)} rows: {results['success']} succeeded, {results['failed']} failed",
        })
    except Exception as e:
        logger.error(f"[Bulk Submit Error] {e}")
        msg = str(e)
        if "Pinecone" in msg:
            return jsonify({"success": False, "error": "Vector database not configured.", "errorType": "PINECONE_NOT_CONFIGURED"}), 503
        if "quota" in msg:
            return jsonify({"success": False, "error": "OpenAI API quota exceeded.", "errorType": "QUOTA_EXCEEDED"}), 402
        if "API key" in msg:
            return jsonify({"success": False, "error": "Invalid or missing OpenAI API key.", "errorType": "INVALID_API_KEY"}), 401
        return jsonify({"success": False, "error": msg or "Internal server error"}), 500


def _run_tool_comparisons(
    main_id: str,
    main_code: str,
    other_students: list[dict],
    language: str,
    max_results: int | None = None,
    check_id: str | None = None,
) -> list[dict]:
    """Run copydetect and the appropriate tree-sitter tool (no difflib). Used by /check API.
    Tools run in parallel so total time is max(copydetect, treesitter), not sum.
    If max_results is set, trim each tool's results to the top N by that tool's similarity."""
    lang = code_normalizer.resolve_language(language)
    tools = ["copydetect", f"treesitter_{lang}"]
    main_len = len(main_code)
    num_others = len(other_students)
    max_other_len = max((len(o.get("code", "") or "") for o in other_students), default=0)
    cid = f" check_id={check_id}" if check_id else ""
    logger.info(
        "[Check]%s Tool comparison: tools=%s | main_code_len=%d, num_others=%d, max_other_code_len=%d (difflib not used)",
        cid, tools, main_len, num_others, max_other_len,
    )

    tool_map = {
        "copydetect": lambda: compare_code_copydetect(main_id, main_code, other_students, language),
        "treesitter_python": lambda: compare_code_treesitter_python(main_id, main_code, other_students),
        "treesitter_cpp": lambda: compare_code_treesitter_cpp(main_id, main_code, other_students),
        "treesitter_java": lambda: compare_code_treesitter_java(main_id, main_code, other_students),
        "treesitter_c": lambda: compare_code_treesitter_c(main_id, main_code, other_students),
        "treesitter_csharp": lambda: compare_code_treesitter_csharp(main_id, main_code, other_students),
        "treesitter_javascript": lambda: compare_code_treesitter_javascript(main_id, main_code, other_students),
    }

    tool_list = [t for t in tools if t in tool_map]
    if not tool_list:
        return []

    def run_one(tool: str) -> tuple[str, float, dict]:
        t0 = time.perf_counter()
        result = tool_map[tool]()
        elapsed = time.perf_counter() - t0
        return tool, elapsed, result

    results_by_tool: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(run_one, tool): tool for tool in tool_list}
        done, not_done = concurrent.futures.wait(futures, timeout=280, return_when=concurrent.futures.ALL_COMPLETED)
        for f in not_done:
            tool = futures[f]
            f.cancel()
            logger.warning("[Check] Tool %s did not finish within 280s (timeout); returning partial results", tool)
            results_by_tool[tool] = {
                "tool": tool,
                "available": False,
                "error": f"Tool timed out after 280s. Likely cause: many/long submissions. main_code_len={main_len}, num_others={num_others}, max_other_len={max_other_len}.",
                "results": [],
            }
        for f in done:
            try:
                tool, elapsed, result = f.result()
                results_by_tool[tool] = result
                if elapsed > 60:
                    logger.warning(
                        "[Check] Tool %s took %.1fs (slow; may cause timeouts with more/longer code). main_len=%d, num_others=%d",
                        tool, elapsed, main_len, num_others,
                    )
                else:
                    logger.info("[Check] Tool %s finished in %.2fs", tool, elapsed)
            except Exception as e:
                tool = futures[f]
                logger.exception("[Check] Tool %s failed: %s", tool, e)
                results_by_tool[tool] = {
                    "tool": tool,
                    "available": False,
                    "error": str(e),
                    "results": [],
                }

    comparisons = [results_by_tool[t] for t in tool_list if t in results_by_tool]

    # Trim each tool's results to top N by that tool's similarity
    if max_results is not None and max_results > 0:
        for comp in comparisons:
            if comp.get("available") and comp.get("results"):
                sorted_results = sorted(
                    comp["results"],
                    key=lambda r: r.get("similarity") if r.get("similarity") is not None else -1,
                    reverse=True,
                )
                comp["results"] = sorted_results[:max_results]

    return comparisons


def _format_external_result(comparisons: list[dict], past_submissions: list[dict], main_student_id: str = "") -> dict:
    """Format tool comparison results the same way externalPlagiarismService.formatExternalResult did."""
    student_code_map = {}
    for sub in past_submissions:
        sid = sub.get("studentId") or sub.get("student_id") or sub.get("id", "")
        student_code_map[sid] = sub.get("code", "")

    return {
        "available": True,
        "mainStudentId": main_student_id,
        "summary": [],
        "comparisons": [
            {
                "tool": comp.get("tool", ""),
                "available": comp.get("available", False),
                "mainStudentId": comp.get("main_student_id", ""),
                "results": [
                    {
                        "studentId": r.get("other_student_id", ""),
                        "similarity": r.get("similarity", 0),
                        "code": student_code_map.get(r.get("other_student_id", "")) or None,
                        "details": r,
                    }
                    for r in comp.get("results", [])
                ],
            }
            for comp in comparisons
        ],
    }


def _determine_final_decision(
    local_result: dict,
    external_result: dict,
    threshold: float,
    structural_data: dict,
) -> dict:
    """Use scoring engine to produce final plagiarism report (replaces externalPlagiarismService.determineFinalDecision)."""
    options = {}
    if structural_data.get("current_code") and structural_data.get("compared_code"):
        options["current_code"] = structural_data["current_code"]
        options["compared_code"] = structural_data["compared_code"]
        options["language"] = structural_data.get("language", "python")

    report = scoring_engine.generate_plagiarism_report(local_result, external_result, threshold, options)

    tool_results = {}
    for comp in (external_result or {}).get("comparisons", []):
        if not comp.get("available") or not comp.get("results"):
            continue
        max_sim = max((r.get("similarity", 0) for r in comp["results"]), default=0)
        tool_results[comp["tool"]] = {
            "available": True,
            "maxSimilarity": max_sim,
            "matchCount": sum(1 for r in comp["results"] if r.get("similarity", 0) >= threshold),
        }

    return {
        "plagiarismDetected": report["plagiarism_detected"],
        "overallScore": report["overall_score"],
        "overallPercentage": report["overall_percentage"],
        "plagiarismType": report["plagiarism_type"],
        "severity": report["severity"],
        "confidence": report["confidence"],
        "methodCount": report["method_count"],
        "scoreBreakdown": report["score_breakdown"],
        "detectionMethods": report["detection_methods"],
        "reasoning": report["reasoning"],
        "highestSimilarity": report["overall_score"],
        "toolResults": tool_results,
        "totalChecksRun": report["method_count"],
        "threshold": threshold,
        "isAboveThreshold": report["is_above_threshold"],
        "explanation": report["explanation"],
        "displayMessage": report["display_message"],
    }


@app.route("/api/check", methods=["POST"])
def api_check():
    """
    Comprehensive plagiarism check combining:
      1. Local semantic embedding search (Pinecone)
      2. Direct tool-based comparison (copydetect, tree-sitter; difflib skipped for /check)
      3. Scoring engine for final decision

    Request body:
    {
      "code": str,
      "questionId": str,
      "examId": str (optional),
      "language": str (optional, default "javascript"),
      "similarityThreshold": float (optional, default 0.75),
      "maxResults": int (optional, default 5),
      "useNormalization": bool (optional, default true),
      "excludeStudentId": str (optional, exclude this student's submissions),
      "languageFilter": str (optional, only compare against this language),
      "submissionId": str (optional, reuse stored embedding instead of calling OpenAI)
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

        code = data.get("code", "")
        question_id = (data.get("questionId") or "").strip()
        exam_id_raw = data.get("examId")
        exam_id = str(exam_id_raw).strip() if exam_id_raw and str(exam_id_raw).strip() else None
        language = data.get("language", "javascript")
        similarity_threshold = float(data.get("similarityThreshold", 0.75))
        max_results = int(data.get("maxResults") or data.get("max_results") or 5)
        use_normalization = data.get("useNormalization", True)
        exclude_student_id = data.get("excludeStudentId") or None
        language_filter = data.get("languageFilter") or None
        submission_id = data.get("submissionId") or None
        custom_api_key = request.headers.get("X-OpenAI-API-Key")

        normalized_exclude = str(exclude_student_id).strip() if exclude_student_id else None
        normalized_lang_filter = str(language_filter).strip().lower() if language_filter else None

        if not code or not question_id:
            return jsonify({"success": False, "error": "Missing required fields: code, questionId"}), 400
        if not code.strip():
            return jsonify({"success": False, "error": "Code cannot be empty"}), 400

        check_id = uuid.uuid4().hex[:12]
        t_check = time.perf_counter()
        logger.info(
            "[API/check] START check_id=%s questionId=%s examId=%s code_len=%d language=%s "
            "similarityThreshold=%s maxResults=%s useNormalization=%s excludeStudentId=%s languageFilter=%s submissionId=%s",
            check_id,
            question_id,
            exam_id or "none",
            len(code),
            language,
            similarity_threshold,
            max_results,
            use_normalization,
            normalized_exclude or "none",
            normalized_lang_filter or "none",
            submission_id or "none",
        )

        logger.info("[Check] check_id=%s load_submissions question=%s", check_id, question_id)

        # Verify submissions exist (retry once for Pinecone eventual consistency)
        existing_submissions = vector_db.get_submissions_by_question(question_id, exam_id)
        if not existing_submissions:
            logger.info(
                "[Check] check_id=%s no submissions first fetch; retry 2.5s (Pinecone)",
                check_id,
            )
            time.sleep(2.5)
            existing_submissions = vector_db.get_submissions_by_question(question_id, exam_id)
        logger.info(
            "[TIMING] check_id=%s step=load_submissions cumulative=%.3fs n_submissions=%d",
            check_id, time.perf_counter() - t_check, len(existing_submissions),
        )
        if not existing_submissions:
            logger.info("[API/check] END check_id=%s error=NO_SUBMISSIONS elapsed=%.3fs", check_id, time.perf_counter() - t_check)
            return jsonify({
                "success": False,
                "error": f'No submissions found for question "{question_id}". Please submit code for this question first before checking for similarity.',
                "errorType": "NO_SUBMISSIONS",
                "questionId": question_id,
            }), 404

        logger.info(
            "[Check] check_id=%s loaded %d submissions for question %s",
            check_id,
            len(existing_submissions),
            question_id,
        )

        # Pre-calculation filtering
        if normalized_exclude:
            before_count = len(existing_submissions)
            existing_submissions = [
                s for s in existing_submissions
                if (s.get("student_id") or "").strip().lower() != normalized_exclude.lower()
            ]
            logger.info(f'[Check] Excluded student "{normalized_exclude}": {before_count} -> {len(existing_submissions)} submissions')

        if normalized_lang_filter:
            before_count = len(existing_submissions)
            existing_submissions = [
                s for s in existing_submissions
                if not s.get("language") or s["language"].strip().lower() == normalized_lang_filter
            ]
            logger.info(f'[Check] Language filter "{normalized_lang_filter}": {before_count} -> {len(existing_submissions)} submissions')

        if not existing_submissions:
            logger.info(
                "[API/check] END check_id=%s error=NO_SUBMISSIONS_AFTER_FILTER elapsed=%.3fs",
                check_id,
                time.perf_counter() - t_check,
            )
            return jsonify({
                "success": False,
                "error": f"No submissions found after filtering (excludeStudentId: {normalized_exclude or 'none'}, languageFilter: {normalized_lang_filter or 'none'}).",
                "errorType": "NO_SUBMISSIONS_AFTER_FILTER",
                "questionId": question_id,
            }), 404

        # Step 1: Get embedding - reuse from DB if submissionId provided, otherwise generate via OpenAI
        logger.info("[Check] check_id=%s step=embedding", check_id)
        t_emb = time.perf_counter()
        code_embedding = None
        if submission_id:
            code_embedding = vector_db.get_submission_embedding(submission_id)
            if code_embedding:
                logger.info(
                    "[Check] check_id=%s reused embedding submissionId=%s (no OpenAI) fetch_elapsed=%.3fs",
                    check_id,
                    submission_id,
                    time.perf_counter() - t_emb,
                )

        if not code_embedding:
            code_embedding = embeddings.generate_code_embedding(code, language, custom_api_key, use_normalization)
            logger.info(
                "[Check] check_id=%s OpenAI embedding done normalization=%s elapsed=%.3fs",
                check_id,
                "ON" if use_normalization else "OFF",
                time.perf_counter() - t_emb,
            )
        logger.info(
            "[TIMING] check_id=%s step=embedding cumulative=%.3fs",
            check_id, time.perf_counter() - t_check,
        )

        # Step 2: Find similar whole submissions (low threshold, scoring engine filters later)
        search_threshold = min(0.3, similarity_threshold)
        logger.info(
            "[Check] check_id=%s step=vector_search threshold=%.3f",
            check_id,
            search_threshold,
        )
        similar_submissions = vector_db.find_similar_submissions(
            code_embedding, question_id, 50, search_threshold, exam_id,
        )
        top_sim = similar_submissions[0]["similarity"] if similar_submissions else None
        logger.info(
            "[Check] check_id=%s vector_hits=%d top_similarity=%s",
            check_id,
            len(similar_submissions),
            round(top_sim, 4) if top_sim is not None else None,
        )
        logger.info(
            "[TIMING] check_id=%s step=vector_search cumulative=%.3fs",
            check_id, time.perf_counter() - t_check,
        )

        # Apply same pre-filters to vector search results
        if normalized_exclude:
            similar_submissions = [
                s for s in similar_submissions
                if (s.get("student_id") or "").strip().lower() != normalized_exclude.lower()
            ]
            logger.info(f"[Check] After excludeStudentId filter: {len(similar_submissions)} similar submissions")

        if normalized_lang_filter:
            similar_submissions = [
                s for s in similar_submissions
                if not s.get("language") or s["language"].strip().lower() == normalized_lang_filter
            ]
            logger.info(f'[Check] After languageFilter "{normalized_lang_filter}": {len(similar_submissions)} similar submissions')

        # Step 3: Extract and check chunks
        logger.info("[Check] check_id=%s step=chunks", check_id)
        code_chunks = chunking.extract_code_chunks(code, language)
        logger.info("[Check] check_id=%s chunk_count=%d", check_id, len(code_chunks))

        similar_chunks: list[dict] = []
        if code_chunks:
            t_chunks = time.perf_counter()
            query_chunks_emb = embeddings.generate_chunk_embeddings(
                code_chunks, language, custom_api_key, use_normalization,
            )
            logger.info(
                "[Check] check_id=%s chunk_embeddings count=%d elapsed=%.3fs",
                check_id,
                len(query_chunks_emb),
                time.perf_counter() - t_chunks,
            )
            logger.info(
                "[TIMING] check_id=%s step=chunk_embeddings cumulative=%.3fs n_chunks=%d",
                check_id, time.perf_counter() - t_check, len(query_chunks_emb),
            )
            def _search_one_chunk(chunk):
                matches = vector_db.find_similar_chunks(
                    chunk["embedding"], question_id, 10, search_threshold, exam_id,
                )
                for m in matches:
                    m["query_chunk_index"] = chunk["index"]
                    m["query_chunk_text"] = chunk["text"]
                return matches

            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(query_chunks_emb), 5)) as executor:
                chunk_futures = [executor.submit(_search_one_chunk, chunk) for chunk in query_chunks_emb]
                for future in concurrent.futures.as_completed(chunk_futures):
                    try:
                        similar_chunks.extend(future.result())
                    except Exception as e:
                        logger.warning("[Check] check_id=%s chunk search error: %s", check_id, e)
            logger.info(
                "[TIMING] check_id=%s step=chunk_searches cumulative=%.3fs n_chunk_matches=%d",
                check_id, time.perf_counter() - t_check, len(similar_chunks),
            )

            # Apply same filters to chunks
            if normalized_exclude:
                similar_chunks = [
                    c for c in similar_chunks
                    if (c.get("student_id") or "").strip().lower() != normalized_exclude.lower()
                ]
                logger.info(f"[Check] After excludeStudentId filter: {len(similar_chunks)} similar chunks")

            if normalized_lang_filter:
                similar_chunks = [
                    c for c in similar_chunks
                    if not c.get("language") or c["language"].strip().lower() == normalized_lang_filter
                ]
                logger.info(f'[Check] After languageFilter "{normalized_lang_filter}": {len(similar_chunks)} similar chunks')

            similar_chunks.sort(key=lambda c: c.get("similarity", 0), reverse=True)
            logger.info(f"[Check] Found {len(similar_chunks)} similar chunks")

        # Step 4: Build summary
        unique_matched = set(
            [s.get("submission_id", "") for s in similar_submissions]
            + [c.get("submission_id", "") for c in similar_chunks]
        )
        high_sim = [s for s in similar_submissions if s.get("similarity", 0) >= 0.85]
        moderate_sim = [s for s in similar_submissions if 0.75 <= s.get("similarity", 0) < 0.85]
        summary = {
            "totalMatchedSubmissions": len(unique_matched),
            "highSimilarity": len(high_sim),
            "moderateSimilarity": len(moderate_sim),
            "matchedChunks": len(similar_chunks),
            "maxSimilarity": similar_submissions[0]["similarity"] if similar_submissions else 0,
            "threshold": similarity_threshold,
        }

        def _fmt_sub(sub):
            c = sub.get("code", "")
            return {
                "submissionId": sub.get("submission_id", ""),
                "studentId": sub.get("student_id", ""),
                "similarity": round(sub.get("similarity", 0), 3),
                "code": c,
                "codePreview": c[:200] + ("..." if len(c) > 200 else ""),
                "codeLength": len(c),
            }

        def _fmt_chunk(chunk):
            qtext = chunk.get("query_chunk_text") or ""
            mtext = chunk.get("chunk_text") or ""
            return {
                "submissionId": chunk.get("submission_id", ""),
                "studentId": chunk.get("student_id", ""),
                "similarity": round(chunk.get("similarity", 0), 3),
                "queryChunkIndex": chunk.get("query_chunk_index"),
                "queryChunkPreview": qtext[:150] + ("..." if len(qtext) > 150 else ""),
                "matchedChunkText": mtext[:150] + ("..." if len(mtext) > 150 else ""),
                "matchedChunkIndex": chunk.get("chunk_index"),
            }

        # Step 5: Run tool-based comparison DIRECTLY (no HTTP call)
        external_result = None
        final_decision = None

        logger.info(
            "[Check] check_id=%s step=tool_comparisons (copydetect+treesitter) local_vector_hits=%d",
            check_id,
            len(similar_submissions),
        )
        try:
            # Cap tool comparison to the top semantically similar submissions.
            # Running copydetect/treesitter against all stored submissions scales as
            # O(N_all × code_length) — with long code and many submissions this easily
            # exceeds the worker timeout. The vector search already ranked the most
            # relevant candidates; use those. Fall back to existing_submissions when
            # the vector search returned nothing (e.g. first submission for a question).
            MAX_TOOL_SUBMISSIONS = 50
            tool_source = similar_submissions if similar_submissions else existing_submissions
            submissions_for_tools = [
                {
                    "id": sub.get("student_id") or sub.get("id") or sub.get("submission_id", "unknown"),
                    "code": sub.get("code", ""),
                }
                for sub in tool_source[:MAX_TOOL_SUBMISSIONS]
            ]
            tool_code_lens = [len(s.get("code", "") or "") for s in submissions_for_tools]
            logger.info(
                "[Check] check_id=%s tool_inputs submissions=%d (from %d existing, capped at %d) query_code_len=%d stored_code_len_min/max=%s/%s",
                check_id,
                len(submissions_for_tools),
                len(existing_submissions),
                MAX_TOOL_SUBMISSIONS,
                len(code),
                min(tool_code_lens) if tool_code_lens else 0,
                max(tool_code_lens) if tool_code_lens else 0,
            )

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _run_tool_comparisons,
                    "current_check",
                    code,
                    submissions_for_tools,
                    language,
                    max_results,
                    check_id,
                )
                tool_comparisons = future.result(timeout=280)
                
            external_result = _format_external_result(tool_comparisons, existing_submissions, "current_check")
            logger.info(
                "[TIMING] check_id=%s step=tool_comparison cumulative=%.3fs",
                check_id, time.perf_counter() - t_check,
            )

            local_result_for_scoring = {
                "has_matches": len(similar_submissions) > 0,
                "max_similarity": similar_submissions[0]["similarity"] if similar_submissions else 0,
                "match_count": len(similar_submissions),
                "submissions": similar_submissions,
            }
            structural_data = {
                "current_code": code,
                "compared_code": similar_submissions[0]["code"] if similar_submissions else "",
                "language": language,
            }

            final_decision = _determine_final_decision(
                local_result_for_scoring, external_result, similarity_threshold, structural_data,
            )
            logger.info(
                "[Check] check_id=%s scoring plagiarism=%s confidence=%s overall_score=%s",
                check_id,
                final_decision.get("plagiarismDetected"),
                final_decision.get("confidence"),
                final_decision.get("overallScore"),
            )

        except concurrent.futures.TimeoutError:
            logger.error("[Check] External API comparison timed out after 280 seconds (graceful fallback)")
            external_result = {"available": False, "error": "Comparison timed out after 280 seconds. Try testing against fewer submissions or increase timeout.", "matches": []}
            
            local_result_for_scoring = {
                "has_matches": len(similar_submissions) > 0,
                "max_similarity": similar_submissions[0]["similarity"] if similar_submissions else 0,
                "match_count": len(similar_submissions),
                "submissions": similar_submissions,
            }
            structural_data = {
                "current_code": code,
                "compared_code": similar_submissions[0]["code"] if similar_submissions else "",
                "language": language,
            }

            final_decision = _determine_final_decision(
                local_result_for_scoring, {"available": False, "comparisons": []}, similarity_threshold, structural_data,
            )
            final_decision["reasoning"].append("Note: External API verification unavailable due to timeout")
            logger.info("[API/check] check_id=%s tools_timeout fallback_scoring applied", check_id)

        except Exception as tool_err:
            logger.error(f"[Check] External API call failed: {tool_err}")
            external_result = {"available": False, "error": str(tool_err), "matches": []}

            local_result_for_scoring = {
                "has_matches": len(similar_submissions) > 0,
                "max_similarity": similar_submissions[0]["similarity"] if similar_submissions else 0,
                "match_count": len(similar_submissions),
                "submissions": similar_submissions,
            }
            structural_data = {
                "current_code": code,
                "compared_code": similar_submissions[0]["code"] if similar_submissions else "",
                "language": language,
            }

            final_decision = _determine_final_decision(
                local_result_for_scoring, {"available": False, "comparisons": []}, similarity_threshold, structural_data,
            )
            final_decision["reasoning"].append("Note: External API verification unavailable")
            logger.info("[API/check] check_id=%s tools_error fallback: %s", check_id, str(tool_err)[:200])

        # Step 6: Build local / external verdicts
        logger.info(
            "[Check] check_id=%s step=build_response local_flag=%s external_flag=%s",
            check_id,
            (
                len(similar_submissions) > 0
                and similar_submissions[0]["similarity"] >= similarity_threshold
            ),
            external_result.get("available") and final_decision.get("plagiarismDetected", False),
        )
        local_verdict = {
            "method": "Local Vector Similarity (Semantic)",
            "plagiarism_detected": (
                len(similar_submissions) > 0
                and similar_submissions[0]["similarity"] >= similarity_threshold
            ),
            "confidence": (
                "high" if similar_submissions and similar_submissions[0]["similarity"] >= 0.85
                else "medium" if similar_submissions and similar_submissions[0]["similarity"] >= 0.75
                else "low" if similar_submissions
                else "none"
            ),
            "max_similarity": round(similar_submissions[0]["similarity"] * 100) if similar_submissions else 0,
            "matches_found": len(similar_submissions),
            "summary": (
                f"Found {len(similar_submissions)} similar submission(s). Highest similarity: {round(similar_submissions[0]['similarity'] * 100)}%"
                if similar_submissions
                else "No similar submissions found in local database"
            ),
            "details": {
                "threshold_used": round(similarity_threshold * 100),
                "top_matches": [_fmt_sub(s) for s in similar_submissions[:max_results]],
                "similar_chunks": [_fmt_chunk(c) for c in similar_chunks[:10]],
            },
        }

        external_verdict = {
            "method": "External API (AST + Code Structure)",
            "plagiarism_detected": external_result.get("available") and final_decision.get("plagiarismDetected", False),
            "confidence": final_decision.get("confidence", "unknown"),
            "max_similarity": round(final_decision.get("highestSimilarity", 0) * 100),
            "matches_found": len(external_result.get("summary", [])),
            "summary": (
                f"External API detected {len(external_result.get('summary', []))} potential match(es)"
                if external_result.get("available") and external_result.get("summary")
                else "External API found no matches"
                if external_result.get("available")
                else f"External API unavailable: {external_result.get('error', '')}"
                if external_result.get("error")
                else "External API unavailable"
            ),
            "details": external_result or {"available": False},
        }

        overall_assessment = {
            "status": "PLAGIARISM_DETECTED" if local_verdict["plagiarism_detected"] or external_verdict["plagiarism_detected"] else "NO_PLAGIARISM",
            "priority": (
                "HIGH_PRIORITY" if local_verdict["plagiarism_detected"] and external_verdict["plagiarism_detected"]
                else "MEDIUM_PRIORITY" if local_verdict["plagiarism_detected"] or external_verdict["plagiarism_detected"]
                else "LOW_PRIORITY"
            ),
            "recommendation": (
                "Review required - one or more detection methods flagged this submission"
                if local_verdict["plagiarism_detected"] or external_verdict["plagiarism_detected"]
                else "No plagiarism detected by any method"
            ),
            "methods_flagged": (
                (["Local Vector Similarity"] if local_verdict["plagiarism_detected"] else [])
                + (["External API Analysis"] if external_verdict["plagiarism_detected"] else [])
            ),
        }

        total_elapsed = time.perf_counter() - t_check
        logger.info(
            "[API/check] END check_id=%s success overall=%s total_elapsed=%.3fs",
            check_id,
            overall_assessment.get("status"),
            total_elapsed,
        )
        logger.info(
            "[TIMING] check_id=%s COMPLETE total=%.3fs",
            check_id, total_elapsed,
        )
        return jsonify({
            "success": True,
            "detection_results": {"local": local_verdict, "external": external_verdict},
            "overall": overall_assessment,
            "local_result": {
                "summary": summary,
                "similarSubmissions": [_fmt_sub(s) for s in similar_submissions[:max_results]],
                "similarChunks": [_fmt_chunk(c) for c in similar_chunks[:10]],
            },
            "external_result": external_result,
            "final_decision": final_decision,
            "summary": summary,
            "similarSubmissions": [_fmt_sub(s) for s in similar_submissions[:max_results]],
            "similarChunks": [_fmt_chunk(c) for c in similar_chunks[:10]],
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        logger.error(f"[Check Error] {e}")
        msg = str(e)
        if "Pinecone" in msg:
            return jsonify({"success": False, "error": "Vector database not configured. Please set PINECONE_API_KEY in your backend .env file. Get free API key from https://www.pinecone.io/", "errorType": "PINECONE_NOT_CONFIGURED"}), 503
        if "quota" in msg:
            return jsonify({"success": False, "error": 'OpenAI API quota exceeded. Please provide a valid API key with available credits using the "OpenAI API Key" field in the frontend.', "errorType": "QUOTA_EXCEEDED"}), 402
        if "API key" in msg:
            return jsonify({"success": False, "error": 'Invalid or missing OpenAI API key. Please provide a valid API key using the "OpenAI API Key" field in the frontend.', "errorType": "INVALID_API_KEY"}), 401
        return jsonify({"success": False, "error": msg or "Internal server error"}), 500


@app.route("/api/submissions/<question_id>", methods=["GET"])
def api_get_submissions(question_id):
    try:
        qid = question_id.strip()
        exam_id_raw = request.args.get("examId")
        exam_id = str(exam_id_raw).strip() if exam_id_raw and str(exam_id_raw).strip() else None
        submissions = vector_db.get_submissions_by_question(qid, exam_id)
        return jsonify({
            "success": True,
            "questionId": qid,
            "count": len(submissions),
            "submissions": [
                {
                    "id": s["id"],
                    "studentId": s["student_id"],
                    "language": s.get("language") or None,
                    "codeLength": len(s.get("code", "")),
                    "createdAt": s.get("created_at"),
                }
                for s in submissions
            ],
        })
    except Exception as e:
        logger.error(f"[Get Submissions Error] {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reembed/<question_id>", methods=["POST"])
def api_reembed(question_id):
    """Re-generate embeddings for all submissions of a question."""
    try:
        qid = question_id.strip()
        data = request.get_json(force=True, silent=True) or {}
        use_normalization = data.get("useNormalization", True)
        exam_id_raw = data.get("examId")
        exam_id = str(exam_id_raw).strip() if exam_id_raw and str(exam_id_raw).strip() else None
        custom_api_key = request.headers.get("X-OpenAI-API-Key")

        submissions = vector_db.get_submissions_by_question(qid, exam_id)
        if not submissions:
            return jsonify({"success": False, "error": f'No submissions found for question "{qid}"'}), 404

        logger.info(f"[Re-embed] Re-embedding {len(submissions)} submissions for {qid}")
        success_count = 0
        fail_count = 0

        for sub in submissions:
            try:
                lang = "python"
                new_emb = embeddings.generate_code_embedding(sub["code"], lang, custom_api_key, use_normalization)
                chunks = chunking.extract_code_chunks(sub["code"], lang)
                chunks_emb = (
                    embeddings.generate_chunk_embeddings(chunks, lang, custom_api_key, use_normalization)
                    if chunks else []
                )
                existing_exam_id = sub.get("exam_id") or None
                existing_language = sub.get("language") or None
                vector_db.save_submission({
                    "submission_id": sub["id"],
                    "student_id": sub["student_id"],
                    "question_id": sub["question_id"],
                    "exam_id": existing_exam_id,
                    "language": existing_language,
                    "code": sub["code"],
                    "embedding": new_emb,
                    "chunks": chunks_emb,
                })
                success_count += 1
                logger.info(f"[Re-embed] Re-embedded {sub['id']} ({success_count}/{len(submissions)})")
            except Exception as err:
                fail_count += 1
                logger.error(f"[Re-embed] Failed to re-embed {sub['id']}: {err}")

        return jsonify({
            "success": True,
            "questionId": qid,
            "totalSubmissions": len(submissions),
            "successCount": success_count,
            "failCount": fail_count,
            "message": f"Successfully re-embedded {success_count} out of {len(submissions)} submissions",
        })
    except Exception as e:
        logger.error(f"[Re-embed Error] {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/submission/<submission_id>", methods=["GET"])
def api_get_submission(submission_id):
    try:
        submission = vector_db.get_submission(submission_id)
        if not submission:
            return jsonify({"success": False, "error": "Submission not found"}), 404
        return jsonify({"success": True, "submission": submission})
    except Exception as e:
        logger.error(f"[Get Submission Error] {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    logger.info(f"Embedding model: {embeddings.EMBEDDING_MODEL}")
    logger.info(f"Pinecone: {'OK' if pinecone_ok else 'NOT CONFIGURED'}")
    app.run(host="0.0.0.0", port=port, debug=True)
