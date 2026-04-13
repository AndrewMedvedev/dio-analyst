import contextlib
import json
import logging
import re
import time
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from ...settings import CHROMA_PATH

INDEX_NAME = "main-index"

logger = logging.getLogger(__name__)

hf_model = SentenceTransformer("deepvk/USER-bge-m3")
client = chromadb.PersistentClient(CHROMA_PATH)
splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=50, length_function=len)


# async def indexing(text: str, metadata: dict[str, Any] | None = None) -> list[str]:
#     """Индексация и добавление документа в семантический индекс.

#     :param text: Текст документа.
#     :param metadata: Мета-информация документа.
#     :returns: Идентификаторы чанков в индексе.
#     """

#     if not text.strip():
#         logger.warning("Attempted to index empty text!")
#         return []
#     start_time = time.monotonic()
#     logger.info("Starting index document text, length %s characters", len(text))
#     collection = client.get_collection(INDEX_NAME)
#     chunks = splitter.split_text(text)
#     logger.info(len(chunks))
#     logger.info([len(i) for i in chunks])
#     ids = [str(uuid4()) for _ in range(len(chunks))]
#     # embeddings = await get_embeddings(chunks)
#     embeddings = hf_model.encode_document(chunks, normalize_embeddings=False)
#     collection.add(
#         ids=ids,
#         documents=chunks,
#         embeddings=embeddings.tolist(),  # type: ignore  # noqa: PGH003
#         metadatas=[metadata.copy() for _ in range(len(chunks))],  # type: ignore  # noqa: PGH003
#     )
#     logger.info("Finished indexing text, time %s seconds", round(time.monotonic() - start_time, 2))
#     return ids


def batch_chunks(items: list[Any], batch_size: int = 5) -> Iterable[list[Any]]:
    """
    Асинхронный генератор батчей фиксированного размера.

    :param items: список элементов для батчинга
    :param batch_size: размер одного батча (по умолчанию 5)
    :param delay_between_batches: задержка между батчами в секундах (полезно при rate limit)
    """
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        yield batch


async def indexing(
    text: str, metadata: dict[str, Any] | None = None, batch_size: int = 5
) -> list[str]:
    """
    Индексация и добавление документа в семантический индекс с батчингом чанков.

    :param text: Текст документа.
    :param metadata: Мета-информация документа.
    :param batch_size: Количество чанков в одном батче при добавлении в векторную БД.
    :returns: Идентификаторы всех чанков в индексе.
    """
    if not text or not text.strip():
        logger.warning("Attempted to index empty text!")
        return []

    start_time = time.monotonic()
    logger.info("Starting index document text, length %s characters", len(text))

    collection = client.get_or_create_collection(INDEX_NAME)

    # Разбиваем текст на чанки
    chunks = splitter.split_text(text)

    if not chunks:
        logger.warning("No chunks generated from text")
        return []

    logger.info("Generated %s chunks with lengths: %s", len(chunks), [len(i) for i in chunks])

    # Генерируем уникальные ID для всех чанков
    ids = [str(uuid4()) for _ in chunks]

    # Получаем эмбеддинги (можно оставить синхронно, если hf_model быстрый,
    # или сделать асинхронным при необходимости)
    embeddings = hf_model.encode_document(chunks, normalize_embeddings=False)
    embeddings_list = embeddings.tolist()  # type: ignore  # noqa: PGH003

    # Подготавливаем метаданные
    metadatas = [metadata.copy() if metadata else {} for _ in chunks]

    # Батчинг добавления в коллекцию
    added_ids: list[str] = []

    for batch_idx, batch_slice in enumerate(
        batch_chunks(list(range(len(chunks))), batch_size=batch_size)
    ):
        batch_ids = [ids[i] for i in batch_slice]
        batch_docs = [chunks[i] for i in batch_slice]
        batch_embs = [embeddings_list[i] for i in batch_slice]
        batch_metas = [metadatas[i] for i in batch_slice]

        logger.info("Adding batch %s with %s chunks to collection", batch_idx + 1, len(batch_ids))

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            embeddings=batch_embs,
            metadatas=batch_metas,
        )

        added_ids.extend(batch_ids)

    logger.info(
        "Finished indexing text (%s chunks), time: %s seconds",
        len(chunks),
        round(time.monotonic() - start_time, 2),
    )

    return added_ids


def clean_text(text: str) -> str:
    """Очистка текста от экранированных символов и Unicode"""
    if not isinstance(text, str):
        return str(text)

    # Метод 1: Декодирование Unicode escape последовательностей
    with contextlib.suppress(UnicodeDecodeError):
        text = text.encode("utf-8").decode("unicode_escape")

    # Метод 2: Обработка JSON строк
    try:
        # Убираем лишние кавычки в начале и конце если есть
        if text.startswith('"') and text.endswith('"'):
            text = json.loads(text)
        else:
            text = json.loads(f'"{text}"')
    except (json.JSONDecodeError, TypeError):
        pass

    # Метод 3: Ручная замена Unicode последовательностей
    def replace_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)

    return re.sub(r"\\u([0-9a-fA-F]{4})", replace_unicode, text)


async def retrieve(
    query: str,
    metadata_filter: dict[str, Any] | None = None,
    search_string: str | None = None,
    n_results: int = 10,
) -> list[str]:
    """Извлечение документов с очисткой текста"""

    collection = client.get_collection(INDEX_NAME)
    logger.info("Retrieving for query: '%s...'", query[:50])

    # embedding = await get_embeddings([query])
    embedding = hf_model.encode_query(query, normalize_embeddings=False)
    params = {"query_embeddings": [embedding.tolist()], "n_results": n_results}  # type: ignore  # noqa: PGH003

    if metadata_filter:
        if len(metadata_filter) == 0:
            pass  # пустой фильтр не передаём
        elif len(metadata_filter) == 1:
            params["where"] = metadata_filter
        else:
            # Несколько полей → оборачиваем в $and
            params["where"] = {"$and": [{k: v} for k, v in metadata_filter.items()]}
    if search_string:
        params["where_document"] = {"$contains": search_string}

    result = collection.query(**params, include=["documents", "metadatas", "distances"])

    cleaned_results = []
    for document, metadata, distance in zip(
        result["documents"][0],  # type: ignore  # noqa: PGH003
        result["metadatas"][0],  # type: ignore  # noqa: PGH003
        result["distances"][0],  # type: ignore  # noqa: PGH003
        strict=False,  # type: ignore  # noqa: PGH003
    ):
        # Очищаем документ
        cleaned_doc = clean_text(document)

        # Очищаем метаданные если нужно
        cleaned_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                cleaned_metadata[key] = clean_text(value)
            else:
                cleaned_metadata[key] = value

        cleaned_results.append(
            f"**Relevance score:** {round(distance, 2)}\n"
            f"**Source:** {cleaned_metadata.get('source', '')}\n"
            f"**Category:** {cleaned_metadata.get('category', '')}\n"
            "**Document:**\n"
            f"{cleaned_doc}"
        )

    return cleaned_results


def delete_old_data(max_age_hours: int = 3) -> None:
    """Удаляет из ChromaDB документы старше max_age_hours."""
    cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)

    # Важно: переводим в Unix timestamp (число секунд)
    cutoff_timestamp = int(cutoff.timestamp())

    collection = client.get_collection(INDEX_NAME)

    # Теперь фильтр будет работать, потому что значение — число
    old_docs = collection.get(where={"timestamp": {"$lt": cutoff_timestamp}})

    if old_docs.get("ids"):
        collection.delete(ids=old_docs["ids"])
        deleted_count = len(old_docs["ids"])
        logger.info(
            "Из RAG удалено %s старых документов (старше %s часов)", deleted_count, max_age_hours
        )

    else:
        logger.info("Нет старых документов для удаления (старше %s часов)", max_age_hours)
