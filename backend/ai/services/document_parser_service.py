"""Document parser service for extracting clinical text and metadata from uploaded files."""

import io
import logging
import os
import re
import zipfile
from html import unescape
from typing import Any, Dict, Optional, Tuple

from core.exceptions import DocumentParseError

from .ocr_service import DocumentOCRService

logger = logging.getLogger(__name__)

# Keywords for document categorization
_IMAGING_KEYWORDS = [
    r"\bct\b", r"\bmri\b", r"\bx-?ray\b", r"\bultrasound\b", r"\bsonograph\w*",
    r"\bradiolog\w*", r"\bcomputed tomography\b", r"\bmagnetic resonance\b",
    r"\bscanner\b", r"\bscan\b", r"\bmammogra\w*", r"\bpet-ct\b", r"\bpet scan\b",
    r"\bfluoroscop\w*", r"\bechocardiogra\w*", r"\bcontrast\b", r"\battenuation\b",
    r"\bhounsfield\b", r"\baxial\b", r"\bcoronal\b", r"\bsagittal\b", r"\bimpression:\b",
    r"\bfindings:\b", r"\btechnique:\b"
]

_LAB_KEYWORDS = [
    r"\bcbc\b", r"\bcomplete blood count\b", r"\bwbc\b", r"\brbc\b", r"\bhemoglobin\b",
    r"\bhematocrit\b", r"\bplatelet\w*", r"\bcreatinine\b", r"\bbun\b", r"\be?gfr\b",
    r"\balt\b", r"\bast\b", r"\balp\b", r"\bbilirubin\b", r"\bglucose\b", r"\bhba1c\b",
    r"\burinalysis\b", r"\blipid panel\b", r"\bcholesterol\b", r"\btriglyceride\w*",
    r"\belectrolyte\w*", r"\bpotassium\b", r"\bsodium\b", r"\bcalcium\b", r"\btsh\b",
    r"\bcrp\b", r"\besr\b", r"\breference range\b", r"\bnormal range\b", r"\bmg/dl\b",
    r"\bmmol/l\b", r"\bu/l\b", r"\bg/dl\b", r"\blab results?\b", r"\blaboratory\b"
]

_PATHOLOGY_KEYWORDS = [
    r"\bbiopsy\b", r"\bhistopatholog\w*", r"\bcytolog\w*", r"\bimmunohistochem\w*",
    r"\bmalignan\w*", r"\bcarcinoma\b", r"\bneoplasm\b", r"\bpathology report\b",
    r"\bmicroscopic description\b", r"\bgross description\b", r"\bspecimen\b"
]

_DISCHARGE_KEYWORDS = [
    r"\bdischarge summary\b", r"\badmission date\b", r"\bdischarge date\b",
    r"\bhospital course\b", r"\bdischarge diagnosis\b", r"\bdischarge medications\b"
]

_PRESCRIPTION_KEYWORDS = [
    r"\bprescription\b", r"\brx\b", r"\bsig:\b", r"\bdispense\b", r"\brefill\w*",
    r"\bdosage\b", r"\btablets?\b", r"\bcapsules?\b"
]


def read_file_bytes(file_obj) -> bytes:
    """Read every byte from an uploaded file, leaving the cursor at the start."""
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        data = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        return data if isinstance(data, bytes) else str(data).encode("utf-8")
    except Exception as exc:
        raise DocumentParseError("The uploaded file could not be read.") from exc


class DocumentParserService:
    """Service to parse and extract structured text from medical documents (PDFs, images, text)."""

    MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB limit
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
    SUPPORTED_EXTENSIONS = {
        ".pdf", ".docx", ".txt", ".csv", ".rtf"
    } | IMAGE_EXTENSIONS

    def parse_file(
        self,
        file_obj,
        filename: str,
        content_type: str = ""
    ) -> Dict[str, Any]:
        """
        Extract text, detect clinical document category, and gather metadata.

        Args:
            file_obj: File-like object (or Django UploadedFile / FieldFile)
            filename: Original name of the uploaded file
            content_type: MIME type if provided by client

        Returns:
            Dict containing:
                - text: Extracted plain text content
                - category: Detected DocumentCategory (imaging_scan, lab_result, etc.)
                - exam_type: Inferred exam title / scanner modality
                - page_count: Total pages if PDF, else 1
                - file_size: Total bytes
                - image_meta: Extra metadata for image files (dimensions, format)
                - is_image: Boolean indicating whether file is an image
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise DocumentParseError(
                "Unsupported file type. Upload a PDF, Word (.docx), image "
                "(JPG/PNG/WEBP/TIFF) or text file."
            )

        file_bytes = self._read_bytes(file_obj)
        file_size = len(file_bytes)
        if file_size == 0:
            raise DocumentParseError("The uploaded file is empty.")
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise DocumentParseError(
                f"File is larger than {self.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        if ext == ".pdf" or "pdf" in content_type.lower():
            text, page_count = self._parse_pdf(file_bytes)
            is_image = False
            image_meta = {}
        elif ext in self.IMAGE_EXTENSIONS or "image" in content_type.lower():
            text, image_meta = self._parse_image(file_bytes, filename)
            if not text.strip():
                text = DocumentOCRService().read(file_bytes)
            page_count = 1
            is_image = True
        elif ext == ".docx":
            text, page_count = self._parse_docx(file_bytes, filename)
            is_image = False
            image_meta = {}
        else:
            text = self._parse_plain_text(file_bytes)
            page_count = 1
            is_image = False
            image_meta = {}

        if not text.strip():
            if is_image:
                raise DocumentParseError(
                    "No readable text was found in this image. Check the photo is in focus "
                    "and fills the frame, or upload the original PDF."
                )
            raise DocumentParseError(
                "This file contains no readable text, so it cannot be analysed. "
                "A scanned picture of a report needs OCR."
            )

        category = self._detect_category(text, filename)
        exam_type = self._extract_exam_title(text, filename, category)

        return {
            "text": text.strip(),
            "category": category,
            "exam_type": exam_type,
            "page_count": page_count,
            "file_size": file_size,
            "is_image": is_image,
            "image_meta": image_meta,
            "has_extractable_text": bool(text.strip()),
        }

    def _read_bytes(self, file_obj) -> bytes:
        """Safely read all bytes from a file object, resetting cursor afterwards."""
        return read_file_bytes(file_obj)

    def _parse_pdf(self, file_bytes: bytes) -> Tuple[str, int]:
        """Extract text from PDF pages using pypdf."""
        if not file_bytes:
            return "", 0

        try:
            from pypdf import PdfReader

            stream = io.BytesIO(file_bytes)
            reader = PdfReader(stream)
            page_count = len(reader.pages)
            extracted_pages = []

            for index, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                cleaned = page_text.strip()
                if cleaned:
                    extracted_pages.append(f"[Page {index + 1}]\n{cleaned}")

            return "\n\n".join(extracted_pages), page_count
        except Exception as exc:
            logger.warning("pypdf parsing failed: %s", exc)
            # Guessing at text inside raw PDF bytes produces fragments that the model
            # then reads as real findings, so an unreadable PDF is reported instead.
            raise DocumentParseError(
                "This PDF could not be read; it may be corrupted or password protected."
            ) from exc

    def _parse_docx(self, file_bytes: bytes, filename: str) -> Tuple[str, int]:
        """Extract text from a .docx (a zip of WordprocessingML parts)."""
        if not file_bytes:
            return "", 0

        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
                xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
        except (zipfile.BadZipFile, KeyError, OSError) as exc:
            logger.warning("docx parsing failed for %s: %s", filename, exc)
            raise DocumentParseError(
                "This Word document could not be read. Please upload it as .docx or PDF."
            ) from exc

        # Paragraph and break tags become line breaks, then all other markup is dropped.
        xml = re.sub(r"</w:p[ >]", "\n", xml)
        xml = re.sub(r"<w:br[^>]*/>|<w:tab[^>]*/>", "\n", xml)
        text = re.sub(r"<[^>]+>", "", xml)
        text = unescape(text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        return text, 1

    def _parse_image(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """Inspect and extract metadata / features from image files using PIL."""
        image_meta = {"filename": filename}
        if not file_bytes:
            return "", image_meta

        try:
            from PIL import Image

            stream = io.BytesIO(file_bytes)
            with Image.open(stream) as img:
                image_meta["width"] = img.width
                image_meta["height"] = img.height
                image_meta["format"] = img.format
                image_meta["mode"] = img.mode
        except Exception as exc:
            logger.warning("Image parsing failed: %s", exc)
            return "", image_meta

        # The picture itself carries no text; the OCR step reads it. A synthetic
        # caption here would be analysed by the model as if it were report content.
        return "", image_meta

    def _parse_plain_text(self, file_bytes: bytes) -> str:
        """Decode plain text using common encodings."""
        if not file_bytes:
            return ""

        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"):
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return file_bytes.decode("utf-8", errors="replace")

    def _detect_category(self, text: str, filename: str) -> str:
        """Categorize document based on clinical terms in text and filename."""
        corpus = f"{filename} {text}".lower()

        scores = {
            "imaging_scan": sum(1 for kw in _IMAGING_KEYWORDS if re.search(kw, corpus)),
            "lab_result": sum(1 for kw in _LAB_KEYWORDS if re.search(kw, corpus)),
            "pathology": sum(1 for kw in _PATHOLOGY_KEYWORDS if re.search(kw, corpus)),
            "discharge_summary": sum(1 for kw in _DISCHARGE_KEYWORDS if re.search(kw, corpus)),
            "prescription": sum(1 for kw in _PRESCRIPTION_KEYWORDS if re.search(kw, corpus)),
        }

        best_category = max(scores, key=scores.get)
        if scores[best_category] > 0:
            return best_category

        # Default fallback: if filename suggests scan or image, use imaging_scan
        ext = os.path.splitext(filename)[1].lower()
        if ext in {".jpg", ".jpeg", ".png", ".webp"} or "scan" in corpus or "img" in corpus:
            return "imaging_scan"

        return "general"

    def _extract_exam_title(self, text: str, filename: str, category: str) -> str:
        """Extract or infer the exam/scan modality title."""
        patterns = [
            r"(?:EXAMINATION|STUDY|PROCEDURE|TEST NAME|EXAM):\s*([^\n\r]+)",
            r"(?:CLINICAL INDICATION|REPORT FOR):\s*([^\n\r]+)",
            r"(?:CT|MRI|ULTRASOUND|X-RAY|SCAN)\s+[^\n\r]{5,60}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1 if match.groups() else 0).strip()
                # Clean up punctuation and trailing words
                title = re.sub(r"[\r\n\t]+", " ", title).strip()
                if 4 < len(title) < 90:
                    return title

        clean_name = os.path.splitext(os.path.basename(filename))[0]
        clean_name = re.sub(r"[_\-]+", " ", clean_name).strip()
        if clean_name and len(clean_name) > 3:
            return clean_name.title()

        category_titles = {
            "imaging_scan": "Medical Imaging / Scanner Study",
            "lab_result": "Laboratory Test Report",
            "pathology": "Histopathology Report",
            "discharge_summary": "Hospital Discharge Summary",
            "prescription": "Prescription Order",
            "general": "Medical Clinical Document",
        }
        return category_titles.get(category, "Medical Document")
