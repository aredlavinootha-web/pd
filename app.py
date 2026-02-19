"""
Plagiarism Detector - Deployable Flask application with basic UI.
"""

from flask import Flask, request, render_template_string, jsonify

from plagiarism_detect_copydetect import compare_code_copydetect
from plagiarism_detect_difflib import compare_code_difflib
from plagiarism_detect_treesitter_python import compare_code_treesitter_python
from plagiarism_detect_treesitter_cpp import compare_code_treesitter_cpp

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """Allow access from any origin - no restrictions."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/detect", methods=["OPTIONS"])
def cors_preflight():
    return "", 204


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
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        main_student = data.get("main_student")
        if not main_student:
            return jsonify({"error": "Missing 'main_student' with 'id' and 'code'"}), 400

        main_id = main_student.get("id", "")
        main_code = main_student.get("code", "")
        other_students = data.get("other_students", [])
        language = data.get("language", "python")
        tools = data.get("tools", ["copydetect", "difflib", "treesitter_python", "treesitter_cpp"])

        if not isinstance(other_students, list):
            return jsonify({"error": "'other_students' must be a list of {id, code}"}), 400

        comparisons = []
        tool_map = {
            "copydetect": lambda: compare_code_copydetect(main_id, main_code, other_students, language),
            "difflib": lambda: compare_code_difflib(main_id, main_code, other_students),
            "treesitter_python": lambda: compare_code_treesitter_python(main_id, main_code, other_students),
            "treesitter_cpp": lambda: compare_code_treesitter_cpp(main_id, main_code, other_students),
        }

        for tool in tools:
            if tool in tool_map:
                comparisons.append(tool_map[tool]())

        # Build per-student summary (avg similarity across tools)
        other_ids = [o.get("id", "unknown") for o in other_students]
        summary = []
        for oid in other_ids:
            scores = []
            for comp in comparisons:
                if comp.get("available") and comp.get("results"):
                    for r in comp["results"]:
                        if r.get("other_student_id") == oid and r.get("similarity") is not None:
                            scores.append(r["similarity"])
                            break
            avg = round(sum(scores) / len(scores), 4) if scores else 0.0
            summary.append({"other_student_id": oid, "avg_similarity": avg, "tool_count": len(scores)})

        return jsonify({
            "main_student_id": main_id,
            "summary": summary,
            "comparisons": comparisons,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
