"""Document loader: parse PDF, DOCX, TXT files with page tracking."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PageText:
    page: int
    text: str


@dataclass
class Document:
    doc_id: str = field(default_factory=lambda: "")
    filename: str = ""
    text: str = ""
    file_type: str = ""
    file_size: int = 0
    metadata: dict = field(default_factory=dict)
    pages: list[PageText] = field(default_factory=list)


class DocumentLoader:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}

    def load(self, file_path: Path, doc_id: str = "") -> Document:
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        file_size = file_path.stat().st_size

        if ext == ".pdf":
            pages = self._load_pdf(file_path)
            text = "\n\n".join(p.text for p in pages)
        elif ext in (".docx", ".doc"):
            pages = self._load_docx(file_path)
            text = "\n\n".join(p.text for p in pages)
        else:
            pages = self._load_text(file_path)
            text = "\n\n".join(p.text for p in pages)

        return Document(
            doc_id=doc_id,
            filename=file_path.name,
            text=text,
            file_type=ext,
            file_size=file_size,
            pages=pages,
        )

    def _load_pdf(self, path: Path) -> list[PageText]:
        import pdfplumber

        pages: list[PageText] = []
        with pdfplumber.open(str(path)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    pages.append(PageText(page=i, text=page_text))
        return pages

    def _load_docx(self, path: Path) -> list[PageText]:
        from docx import Document as DocxDocument

        doc = DocxDocument(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        per_page = max(1, len(paragraphs) // max(1, len(paragraphs) // 20))
        pages: list[PageText] = []
        page_num = 1
        for i in range(0, len(paragraphs), per_page):
            chunk = "\n\n".join(paragraphs[i : i + per_page])
            pages.append(PageText(page=page_num, text=chunk))
            page_num += 1
        if not pages and full_text.strip():
            pages.append(PageText(page=1, text=full_text))
        return pages

    def _load_text(self, path: Path) -> list[PageText]:
        encodings = ["utf-8", "gbk", "gb2312", "gb18030"]
        for enc in encodings:
            try:
                full_text = path.read_text(encoding=enc)
                lines = full_text.splitlines()
                per_page = 50
                pages: list[PageText] = []
                page_num = 1
                for i in range(0, len(lines), per_page):
                    pages.append(PageText(page=page_num, text="\n".join(lines[i : i + per_page])))
                    page_num += 1
                if not pages and full_text.strip():
                    pages.append(PageText(page=1, text=full_text))
                return pages
            except (UnicodeDecodeError, LookupError):
                continue
        raise RuntimeError(f"Cannot decode file: {path}")
