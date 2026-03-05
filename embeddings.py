"""
OpenAI Embeddings Module
Generates vector embeddings for code using OpenAI's API.
Includes retry logic, validation, and code normalization.
Ported from embeddings.js.
"""

import os
import time
import math
import logging

from openai import OpenAI

import code_normalizer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_RETRIES = 3
RETRY_DELAY_MS = 1.0

_default_client: OpenAI | None = None


def _get_openai_client(custom_api_key: str | None = None) -> OpenAI:
    global _default_client
    if custom_api_key:
        return OpenAI(api_key=custom_api_key)
    if _default_client is None:
        server_key = os.environ.get("OPENAI_API_KEY")
        if not server_key:
            raise ValueError(
                "OpenAI API key is required. Either:\n"
                "1. Set OPENAI_API_KEY in your .env file, OR\n"
                "2. Provide a custom API key via the x-openai-api-key header"
            )
        _default_client = OpenAI(api_key=server_key)
    return _default_client


def _is_valid_embedding(embedding: list[float] | None) -> bool:
    if not embedding or not isinstance(embedding, list):
        return False
    if len(embedding) != EMBEDDING_DIMENSIONS:
        return False
    if all(v == 0 for v in embedding):
        return False
    if any(not math.isfinite(v) for v in embedding):
        return False
    magnitude = math.sqrt(sum(v * v for v in embedding))
    if magnitude < 0.0001:
        return False
    return True


def generate_embedding(text: str, custom_api_key: str | None = None) -> list[float]:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            normalized_text = text.strip()
            if not normalized_text:
                raise ValueError("Cannot generate embedding for empty text")

            logger.info(f"Generating embedding (attempt {attempt}/{MAX_RETRIES}, {len(normalized_text)} chars)")
            client = _get_openai_client(custom_api_key)

            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=normalized_text,
                encoding_format="float",
            )

            if not response or not response.data or len(response.data) == 0:
                raise ValueError("Invalid response from OpenAI API")

            embedding = response.data[0].embedding

            if not _is_valid_embedding(embedding):
                raise ValueError("Generated embedding failed validation")

            logger.info(f"Successfully generated valid embedding (attempt {attempt})")
            return embedding

        except Exception as e:
            last_error = e
            logger.error(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY_MS * attempt
                time.sleep(delay)

    raise RuntimeError(
        f"Failed to generate valid embedding after {MAX_RETRIES} attempts: {last_error}"
    )


def generate_embeddings_batch(
    texts: list[str], custom_api_key: str | None = None
) -> list[list[float]]:
    if not texts:
        return []

    valid_texts = [t.strip() for t in texts if t and t.strip()]
    if not valid_texts:
        return []

    logger.info(f"Generating {len(valid_texts)} embeddings in batch")
    client = _get_openai_client(custom_api_key)

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=valid_texts,
        encoding_format="float",
    )

    if not response or not response.data:
        raise ValueError("Invalid batch response from OpenAI API")

    raw_embeddings = [item.embedding for item in response.data]

    validated: list[list[float]] = []
    for i, emb in enumerate(raw_embeddings):
        if not _is_valid_embedding(emb):
            logger.warning(f"Embedding {i} failed validation, regenerating...")
            single = generate_embedding(valid_texts[i], custom_api_key)
            validated.append(single)
        else:
            validated.append(emb)

    logger.info(f"Successfully generated {len(validated)} valid embeddings")
    return validated


def generate_code_embedding(
    code: str,
    language: str = "javascript",
    custom_api_key: str | None = None,
    use_normalization: bool = True,
) -> list[float]:
    if use_normalization:
        normalized = code_normalizer.normalize_code(code, language)
        contextualized = f"{language}:\n{normalized}"
    else:
        contextualized = f"{language}:\n{code}"

    return generate_embedding(contextualized, custom_api_key)


def generate_chunk_embeddings(
    chunks: list[dict],
    language: str = "javascript",
    custom_api_key: str | None = None,
    use_normalization: bool = True,
) -> list[dict]:
    if not chunks:
        return []

    if use_normalization:
        texts = [
            f"{language}:\n{code_normalizer.normalize_code(c['text'], language)}"
            for c in chunks
        ]
    else:
        texts = [f"{language}:\n{c['text']}" for c in chunks]

    batch_embeddings = generate_embeddings_batch(texts, custom_api_key)

    return [
        {"index": c["index"], "text": c["text"], "embedding": batch_embeddings[i]}
        for i, c in enumerate(chunks)
    ]


def cosine_similarity(embedding1: list[float], embedding2: list[float]) -> float:
    if not _is_valid_embedding(embedding1) or not _is_valid_embedding(embedding2):
        raise ValueError("Cannot calculate similarity with invalid embedding vectors")
    if len(embedding1) != len(embedding2):
        raise ValueError("Embeddings must have the same dimensions")

    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    norm1 = math.sqrt(sum(a * a for a in embedding1))
    norm2 = math.sqrt(sum(b * b for b in embedding2))

    if norm1 == 0 or norm2 == 0:
        raise ValueError("Cannot calculate similarity with zero-magnitude vectors")

    similarity = dot_product / (norm1 * norm2)
    return max(0.0, min(1.0, similarity))
