import pytest
from app.parsers.txt_parser import parse_txt
from app.parsers.docx_parser import parse_docx
from app.parsers.pdf_parser import parse_pdf
from app.services.document_service import DocumentService, DocumentProcessingError


def test_txt_parser():
    content = b"Candidate John Doe\nSkills: Python, Java, Docker"
    extracted = parse_txt(content)
    assert "John Doe" in extracted
    assert "Python" in extracted


def test_empty_file_handling():
    with pytest.raises(DocumentProcessingError) as exc_info:
        DocumentService.extract_text("empty.txt", b"")
    assert exc_info.value.code == "INVALID_FILE"


def test_unsupported_file_type():
    with pytest.raises(DocumentProcessingError) as exc_info:
        DocumentService.extract_text("file.xyz", b"hello content")
    assert exc_info.value.code == "UNSUPPORTED_FILE_TYPE"
