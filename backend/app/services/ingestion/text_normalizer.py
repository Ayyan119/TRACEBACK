import re
import unicodedata


class TextNormalizer:
    """Sanitizes and normalizes extracted text before semantic chunking without destroying document structure."""

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        # 1. Unicode Normalization (NFC)
        normalized = unicodedata.normalize("NFC", text)

        # 2. Strip null bytes and non-printable control characters (except tab/newline)
        normalized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", normalized)

        # 3. Standardize newline formats (\r\n -> \n, \r -> \n)
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 4. Clean trailing whitespace per line
        lines = [line.rstrip() for line in normalized.split("\n")]
        normalized = "\n".join(lines)

        # 5. Collapse 3+ consecutive newlines into double newlines (preserve paragraphs)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)

        # 6. Collapse excessive spaces (3+ spaces into 2 spaces, preserving indentation/formatting)
        normalized = re.sub(r"[ \t]{4,}", "   ", normalized)

        return normalized.strip()


text_normalizer = TextNormalizer()
