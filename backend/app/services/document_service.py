import os
import logging
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx
from app.parsers.txt_parser import parse_txt
from app.config.settings import settings

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class DocumentService:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    @classmethod
    def extract_text(cls, filename: str, file_bytes: bytes) -> str:
        if not file_bytes:
            raise DocumentProcessingError("INVALID_FILE", "File is empty")

        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_size_bytes:
            raise DocumentProcessingError(
                "FILE_TOO_LARGE",
                f"File size exceeds limit of {settings.MAX_FILE_SIZE_MB}MB"
            )

        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise DocumentProcessingError(
                "UNSUPPORTED_FILE_TYPE",
                f"Unsupported file type '{ext}'. Supported formats: PDF, DOCX, TXT"
            )

        try:
            if ext == ".pdf":
                return parse_pdf(file_bytes)
            elif ext == ".docx":
                return parse_docx(file_bytes)
            elif ext == ".txt":
                return parse_txt(file_bytes)
            else:
                raise DocumentProcessingError("UNSUPPORTED_FILE_TYPE", f"Unsupported extension: {ext}")
        except ValueError as ve:
            raise DocumentProcessingError("DOCUMENT_EXTRACTION_FAILED", str(ve))
        except Exception as e:
            logger.error(f"Unexpected document extraction error on {filename}: {e}")
            raise DocumentProcessingError("DOCUMENT_EXTRACTION_FAILED", f"Error processing file: {str(e)}")
