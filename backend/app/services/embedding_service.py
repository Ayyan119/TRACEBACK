import logging
import math
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Real Embedding Service using BAAI/bge-small-en-v1.5 via FastEmbed / SentenceTransformers."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self._embedding_dim = 384  # Default BAAI/bge-small-en-v1.5 dimension

    def _load_model(self):
        if self._model is not None:
            return self._model

        # Attempt 1: FastEmbed (Lightweight ONNX)
        try:
            from fastembed import TextEmbedding
            logger.info(f"Loading FastEmbed model '{self.model_name}'...")
            self._model = ("fastembed", TextEmbedding(model_name=self.model_name))
            # Determine dimension programmatically
            sample_vec = list(next(self._model[1].embed(["test"])))
            self._embedding_dim = len(sample_vec)
            logger.info(f"FastEmbed model initialized. Vector dimension: {self._embedding_dim}")
            return self._model
        except Exception as e1:
            logger.warning(f"FastEmbed initialization skipped/failed: {e1}")

        # Attempt 2: SentenceTransformers (PyTorch)
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformers model '{self.model_name}'...")
            st_model = SentenceTransformer(self.model_name)
            self._model = ("sentence_transformers", st_model)
            sample_vec = st_model.encode("test").tolist()
            self._embedding_dim = len(sample_vec)
            logger.info(f"SentenceTransformers model initialized. Vector dimension: {self._embedding_dim}")
            return self._model
        except Exception as e2:
            logger.warning(f"SentenceTransformers initialization skipped/failed: {e2}")

        raise RuntimeError(
            f"Failed to initialize embedding model '{self.model_name}' using FastEmbed or SentenceTransformers. "
            f"Production mode requires a real embedding model."
        )

    @property
    def embedding_dim(self) -> int:
        """Returns exact programmatically verified embedding vector size."""
        if self._model is None:
            self._load_model()
        return self._embedding_dim

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single string into a vector embedding."""
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        res = self.embed_documents([text])
        return res[0] if res else [0.0] * self.embedding_dim

    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embeds a list of string chunks into dense vector embeddings using batching."""
        if not texts:
            return []

        model_type, model_obj = self._load_model()

        if model_type == "fastembed":
            embeddings = list(model_obj.embed(texts, batch_size=batch_size))
            return [list(vec) for vec in embeddings]

        if model_type == "sentence_transformers":
            embeddings = model_obj.encode(texts, batch_size=batch_size, show_progress_bar=False)
            return [vec.tolist() for vec in embeddings]

        raise RuntimeError("No embedding model initialized.")


embedding_service = EmbeddingService()
