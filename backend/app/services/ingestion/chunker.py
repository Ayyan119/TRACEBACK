import logging
from dataclasses import dataclass
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    chunk_index: int
    text: str
    word_count: int
    char_count: int


class Chunker:
    """Structure-aware RecursiveCharacterTextSplitter with configurable size and overlap priority."""

    def __init__(
        self,
        default_chunk_size: Optional[int] = None,
        default_overlap: Optional[int] = None,
    ):
        self.default_chunk_size = default_chunk_size or getattr(settings, "CHUNK_SIZE", 3000)
        self.default_overlap = default_overlap or getattr(settings, "CHUNK_OVERLAP", 300)

    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[TextChunk]:
        """Splits normalized text into semantically cohesive chunks using LangChain RecursiveCharacterTextSplitter."""
        if not text or not text.strip():
            return []

        c_size = chunk_size or self.default_chunk_size
        c_overlap = chunk_overlap or self.default_overlap

        # Priority separator list: Section -> Paragraph -> Line -> Sentence -> Semicolon -> Comma -> Word -> Char
        separators = [
            "\n# ",
            "\n## ",
            "\n### ",
            "\n1. ",
            "\n2. ",
            "\n\n",
            "\n",
            ". ",
            "; ",
            ", ",
            " ",
            "",
        ]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=c_size,
            chunk_overlap=c_overlap,
            separators=separators,
            keep_separator=True,
        )

        raw_splits = splitter.split_text(text)
        chunks: List[TextChunk] = []

        for idx, split_str in enumerate(raw_splits):
            clean_str = split_str.strip()
            if not clean_str:
                continue
            words = clean_str.split()
            chunks.append(
                TextChunk(
                    chunk_index=idx,
                    text=clean_str,
                    word_count=len(words),
                    char_count=len(clean_str),
                )
            )

        return chunks


chunker = Chunker()
