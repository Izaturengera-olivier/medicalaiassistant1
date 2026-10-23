"""Optical character recognition for photographed or scanned clinical reports.

Images carry no text layer, so without this step a photo of a lab sheet would be
analysed from its filename alone.
"""

import io
import logging

from django.conf import settings

from core.exceptions import DocumentParseError

logger = logging.getLogger(__name__)

# OCR accuracy on phone photos drops sharply below this, so smaller images are enlarged.
MIN_OCR_EDGE_PX = 1200


class DocumentOCRService:
    """Reads printed text out of an uploaded image with the Tesseract engine."""

    def read(self, image_bytes: bytes) -> str:
        """Return the text found in the image, or raise DocumentParseError."""
        if not image_bytes:
            raise DocumentParseError("The uploaded image is empty.")

        try:
            import pytesseract
        except ImportError as exc:
            raise DocumentParseError(
                "Image reading is not available on this server (pytesseract is not installed)."
            ) from exc

        prepared = self._prepare(image_bytes)

        command = getattr(settings, "TESSERACT_CMD", "")
        if command:
            pytesseract.pytesseract.tesseract_cmd = command

        try:
            # psm 6 treats the page as one block of text, which suits lab and scan tables.
            text = pytesseract.image_to_string(prepared, lang="eng", config="--psm 6")
        except pytesseract.TesseractNotFoundError as exc:
            logger.warning("Tesseract binary not found (TESSERACT_CMD=%r)", command)
            raise DocumentParseError(
                "This server cannot read text from images yet: the Tesseract OCR engine "
                "is not installed. Install it, or upload the report as a PDF or Word file."
            ) from exc
        except Exception as exc:
            logger.warning("OCR failed: %s", exc)
            raise DocumentParseError("The text in this image could not be read.") from exc

        return (text or "").strip()

    def _prepare(self, image_bytes: bytes):
        """Grayscale, contrast-normalise and upscale the image before recognition."""
        from PIL import Image, ImageOps

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img = img.convert("L")
                if max(img.size) < MIN_OCR_EDGE_PX:
                    scale = MIN_OCR_EDGE_PX / max(img.size)
                    img = img.resize(
                        (round(img.width * scale), round(img.height * scale)),
                        Image.LANCZOS,
                    )
                return ImageOps.autocontrast(img)
        except Exception as exc:
            logger.warning("Image could not be opened for OCR: %s", exc)
            raise DocumentParseError(
                "This file is not a readable image."
            ) from exc
