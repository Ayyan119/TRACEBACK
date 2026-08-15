import re
from typing import List, Dict, Any


class StructureDetector:
    """Detects structural elements (headings, numbered sections, code blocks, lists) in document text."""

    HEADER_PATTERNS = [
        # Markdown headings (# Heading)
        re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+)$"),
        # Numbered section headings (1. Introduction or 2.1 API Gateway)
        re.compile(r"^(?P<num>\d+(?:\.\d+)*)\s+(?P<title>[A-Z][A-Za-z0-9\s_\-\.\:\(\)]+)$"),
        # ALL CAPS headings (ARCHITECTURAL OVERVIEW)
        re.compile(r"^(?P<caps>[A-Z0-9\s_\-\:\.]{4,60})$"),
    ]

    def detect_structure(self, text: str) -> List[Dict[str, Any]]:
        """Parses text blocks into structured elements with section titles."""
        if not text:
            return []

        lines = text.splitlines()
        structured_blocks = []
        current_section = "General"
        buffer = []
        in_code_block = False

        for line in lines:
            line_str = line.rstrip()

            # Code block toggle
            if line_str.startswith("```"):
                in_code_block = not in_code_block
                buffer.append(line_str)
                continue

            if in_code_block:
                buffer.append(line_str)
                continue

            # Check heading patterns
            is_header = False
            for pat in self.HEADER_PATTERNS:
                match = pat.match(line_str)
                if match:
                    # Flush previous buffer
                    if buffer:
                        block_text = "\n".join(buffer).strip()
                        if block_text:
                            structured_blocks.append({"section": current_section, "text": block_text})
                        buffer = []

                    current_section = line_str.strip("#").strip()
                    is_header = True
                    break

            if not is_header:
                buffer.append(line_str)

        if buffer:
            block_text = "\n".join(buffer).strip()
            if block_text:
                structured_blocks.append({"section": current_section, "text": block_text})

        return structured_blocks


structure_detector = StructureDetector()
