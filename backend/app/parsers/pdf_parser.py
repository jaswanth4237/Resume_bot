import io
import logging
from pypdf import PdfReader
import pdfplumber

logger = logging.getLogger(__name__)


def parse_pdf(file_bytes: bytes) -> str:
    """
    Parses PDF bytes using PyPDF with a fallback to pdfplumber for complex layouts.
    Returns cleaned extracted text.
    """
    if not file_bytes:
        raise ValueError("PDF file buffer is empty")

    text_content = []

    # First attempt: pypdf
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_content.append(page_text.strip())
    except Exception as e:
        logger.warning(f"pypdf extraction failed, trying pdfplumber: {e}")
        text_content = []

    # Second attempt fallback: pdfplumber if pypdf returned minimal text
    if not text_content or len("\n".join(text_content).strip()) < 30:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(page_text.strip())
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")

    extracted = "\n\n".join(text_content).strip()

    if not extracted:
        raise ValueError("Could not extract readable text from PDF (file may be empty, corrupt, or scanned image without OCR)")

    return extracted
