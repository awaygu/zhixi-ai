"""FAISS + SQLite vector store for knowledge base chunks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import aiosqlite
import numpy as np

from database import DB_PATH

logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = Path(__file__).parent.parent / "kb_index.faiss"
FAISS_IDMAP_PATH = Path(__file__).parent.parent / "kb_id_map.json"


class FAISSVectorStore:
    def __init__(self, dim: int = 1536):
        self.dim = dim
        self.index = None
        self.id_map: list[str] = []
        self._loaded = False
        self._vectors: list = []

    def _ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True
        try:
            import faiss

            if FAISS_INDEX_PATH.exists() and FAISS_IDMAP_PATH.exists():
                self.index = faiss.read_index(str(FAISS_INDEX_PATH))
                self.id_map = json.loads(FAISS_IDMAP_PATH.read_text("utf-8"))
                logger.info(
                    "Loaded FAISS index: %d vectors", self.index.ntotal
                )
            else:
                self.index = faiss.IndexFlatIP(self.dim)
                self.id_map = []
                logger.info("Created empty FAISS index (dim=%d)", self.dim)
        except ImportError:
            logger.warning("faiss not installed, using brute-force search")
            self.index = None
            self._vectors = []
            self.id_map = []

    def save(self):
        if self.index is not None:
            import faiss

            faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        FAISS_IDMAP_PATH.write_text(
            json.dumps(self.id_map, ensure_ascii=False), encoding="utf-8"
        )

    def add(self, chunk_ids: list[str], vectors: list[list[float]]):
        self._ensure_loaded()
        vecs = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        vecs = vecs / norms

        if self.index is not None:
            self.index.add(vecs)
        else:
            self._vectors.extend(vecs)

        self.id_map.extend(chunk_ids)
        self.save()

    def search(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[tuple[str, float]]:
        self._ensure_loaded()
        q = np.array([query_vector], dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        if self.index is not None and self.index.ntotal > 0:
            actual_k = min(top_k, self.index.ntotal)
            scores, ids = self.index.search(q, actual_k)
            results = []
            for score, idx in zip(scores[0], ids[0]):
                if idx < len(self.id_map):
                    results.append((self.id_map[idx], float(score)))
            return results
        else:
            all_vecs = np.array(self._vectors, dtype=np.float32) if hasattr(self, '_vectors') else np.array([], dtype=np.float32)
            if len(all_vecs) == 0:
                return []
            scores = np.dot(all_vecs, q[0])
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [(self.id_map[i], float(scores[i])) for i in top_indices]

    def remove_by_doc(self, chunk_ids: set[str]):
        self._ensure_loaded()
        keep_indices = [
            i for i, cid in enumerate(self.id_map) if cid not in chunk_ids
        ]
        if not keep_indices:
            self._rebuild_empty()
            return

        if self.index is not None:
            import faiss

            keep_vecs = self.index.reconstruct_n(0, self.index.ntotal)
            keep_vecs = np.array(
                [keep_vecs[i] for i in keep_indices], dtype=np.float32
            )
            self.id_map = [self.id_map[i] for i in keep_indices]
            self.index = faiss.IndexFlatIP(self.dim)
            if len(keep_vecs) > 0:
                self.index.add(keep_vecs)
        else:
            self._vectors = [self._vectors[i] for i in keep_indices]
            self.id_map = [self.id_map[i] for i in keep_indices]
        self.save()

    def _rebuild_empty(self):
        if self.index is not None:
            import faiss

            self.index = faiss.IndexFlatIP(self.dim)
        else:
            self._vectors = []
        self.id_map = []
        self.save()

    @property
    def total_vectors(self) -> int:
        self._ensure_loaded()
        if self.index is not None:
            return self.index.ntotal
        return len(self.id_map)
