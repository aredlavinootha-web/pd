"""
Vector Database Module - Pinecone
Handles vector storage and similarity search using Pinecone cloud vector DB.
Ported from vectorDb.js.
"""

import os
import logging
from datetime import datetime

from pinecone import Pinecone

logger = logging.getLogger(__name__)

INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "plagiarism-detector")
EMBEDDING_DIMENSIONS = 1536
COSINE_SIMILARITY_BASELINE = 0.70

_pinecone_client: Pinecone | None = None
_index = None


def _calibrate_score(raw_score: float) -> float:
    """Remap [BASELINE, 1.0] -> [0, 1] to eliminate embedding floor noise."""
    return max(0.0, (raw_score - COSINE_SIMILARITY_BASELINE) / (1 - COSINE_SIMILARITY_BASELINE))


def _get_pinecone_client() -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        api_key = os.environ.get("PINECONE_API_KEY", "")
        if not api_key or api_key == "your_pinecone_api_key_here":
            raise RuntimeError(
                "Pinecone API key is not configured. Set PINECONE_API_KEY in your .env file. "
                "Get your free API key from https://www.pinecone.io/"
            )
        _pinecone_client = Pinecone(api_key=api_key)
        logger.info("Pinecone client initialized")
    return _pinecone_client


def initialize_index() -> bool:
    global _index
    try:
        client = _get_pinecone_client()
        _index = client.Index(INDEX_NAME)
        logger.info(f"Connected to Pinecone index: {INDEX_NAME}")
        return True
    except Exception as e:
        logger.error(f"Pinecone init error: {e}")
        logger.warning("Server will start but vector operations will fail until API key is configured")
        return False


def save_submission(data: dict) -> str:
    global _index
    if _index is None:
        raise RuntimeError("Pinecone index not initialized. Please configure PINECONE_API_KEY.")

    submission_id = data["submission_id"]
    student_id = data["student_id"]
    question_id = data["question_id"]
    exam_id = data.get("exam_id")
    code = data["code"]
    embedding = data["embedding"]
    chunks = data.get("chunks", [])

    normalized_exam_id = str(exam_id).strip() if exam_id and str(exam_id).strip() else ""

    base_metadata = {
        "type": "submission",
        "submissionId": submission_id,
        "studentId": student_id,
        "questionId": question_id,
        "code": code[:1000],
        "codeLength": len(code),
        "timestamp": int(datetime.now().timestamp() * 1000),
    }
    if normalized_exam_id:
        base_metadata["examId"] = normalized_exam_id

    vectors = [
        {
            "id": f"sub_{submission_id}",
            "values": embedding,
            "metadata": {**base_metadata},
        }
    ]

    chunk_base = {
        "type": "chunk",
        "submissionId": submission_id,
        "studentId": student_id,
        "questionId": question_id,
    }
    if normalized_exam_id:
        chunk_base["examId"] = normalized_exam_id

    for idx, chunk in enumerate(chunks):
        vectors.append({
            "id": f"sub_{submission_id}_chunk_{idx}",
            "values": chunk["embedding"],
            "metadata": {
                **chunk_base,
                "chunkIndex": idx,
                "chunkText": chunk["text"][:1000],
                "timestamp": int(datetime.now().timestamp() * 1000),
            },
        })

    _index.upsert(vectors=vectors)
    logger.info(f"Saved submission {submission_id} with {len(chunks)} chunks")
    return submission_id


def find_similar_submissions(
    embedding: list[float],
    question_id: str,
    limit: int = 5,
    min_similarity: float = 0.3,
    exam_id: str | None = None,
) -> list[dict]:
    global _index
    if _index is None:
        raise RuntimeError("Pinecone index not initialized.")

    filter_dict: dict = {
        "type": {"$eq": "submission"},
        "questionId": {"$eq": question_id},
    }
    normalized_exam_id = str(exam_id).strip() if exam_id and str(exam_id).strip() else None
    if normalized_exam_id:
        filter_dict["examId"] = {"$eq": normalized_exam_id}

    response = _index.query(
        vector=embedding,
        top_k=100,
        filter=filter_dict,
        include_metadata=True,
    )

    results = []
    for match in response.get("matches", []):
        if match["score"] < min_similarity:
            continue
        if len(results) >= limit:
            break
        results.append({
            "id": match["metadata"]["submissionId"],
            "student_id": match["metadata"]["studentId"],
            "question_id": match["metadata"]["questionId"],
            "code": match["metadata"].get("code", ""),
            "similarity": _calibrate_score(match["score"]),
            "raw_similarity": match["score"],
        })

    logger.info(f"Found {len(results)} submissions (raw threshold: {min_similarity})")
    return results


def find_similar_chunks(
    embedding: list[float],
    question_id: str,
    limit: int = 10,
    min_similarity: float = 0.75,
    exam_id: str | None = None,
) -> list[dict]:
    global _index
    if _index is None:
        raise RuntimeError("Pinecone index not initialized.")

    filter_dict: dict = {
        "type": {"$eq": "chunk"},
        "questionId": {"$eq": question_id},
    }
    normalized_exam_id = str(exam_id).strip() if exam_id and str(exam_id).strip() else None
    if normalized_exam_id:
        filter_dict["examId"] = {"$eq": normalized_exam_id}

    response = _index.query(
        vector=embedding,
        top_k=100,
        filter=filter_dict,
        include_metadata=True,
    )

    results = []
    for match in response.get("matches", []):
        if match["score"] < min_similarity:
            continue
        if len(results) >= limit:
            break
        results.append({
            "submission_id": match["metadata"]["submissionId"],
            "student_id": match["metadata"]["studentId"],
            "question_id": match["metadata"]["questionId"],
            "chunk_index": match["metadata"].get("chunkIndex"),
            "chunk_text": match["metadata"].get("chunkText", ""),
            "similarity": _calibrate_score(match["score"]),
            "raw_similarity": match["score"],
        })

    logger.info(f"Found {len(results)} similar chunks")
    return results


def get_submissions_by_question(
    question_id: str, exam_id: str | None = None
) -> list[dict]:
    global _index
    if _index is None:
        raise RuntimeError("Pinecone index not initialized.")

    normalized_qid = question_id.strip() if question_id else ""
    if not normalized_qid:
        raise ValueError("Question ID is required")

    filter_dict: dict = {
        "type": {"$eq": "submission"},
        "questionId": {"$eq": normalized_qid},
    }
    normalized_exam_id = str(exam_id).strip() if exam_id and str(exam_id).strip() else None
    if normalized_exam_id:
        filter_dict["examId"] = {"$eq": normalized_exam_id}

    probe_vector = [0.0] * EMBEDDING_DIMENSIONS
    probe_vector[0] = 0.001

    response = _index.query(
        vector=probe_vector,
        top_k=1000,
        filter=filter_dict,
        include_metadata=True,
    )

    return [
        {
            "id": m["metadata"]["submissionId"],
            "student_id": m["metadata"]["studentId"],
            "question_id": m["metadata"]["questionId"],
            "exam_id": m["metadata"].get("examId"),
            "code": m["metadata"].get("code", ""),
            "created_at": datetime.fromtimestamp(m["metadata"].get("timestamp", 0) / 1000).isoformat(),
        }
        for m in response.get("matches", [])
    ]


def get_submission(submission_id: str) -> dict | None:
    global _index
    if _index is None:
        raise RuntimeError("Pinecone index not initialized.")

    try:
        response = _index.fetch(ids=[f"sub_{submission_id}"])
        records = response.get("vectors", {})
        if not records:
            return None

        record = records[f"sub_{submission_id}"]
        meta = record["metadata"]
        return {
            "id": meta["submissionId"],
            "student_id": meta["studentId"],
            "question_id": meta["questionId"],
            "code": meta.get("code", ""),
            "created_at": datetime.fromtimestamp(meta.get("timestamp", 0) / 1000).isoformat(),
        }
    except Exception as e:
        logger.error(f"Pinecone fetch error: {e}")
        return None
