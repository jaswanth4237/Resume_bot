import logging

logger = logging.getLogger(__name__)


def parse_txt(file_bytes: bytes) -> str:
    """
    Parses plain text bytes handling multiple character encodings.
    """
    if not file_bytes:
        raise ValueError("TXT file buffer is empty")

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]

    for enc in encodings:
        try:
            decoded = file_bytes.decode(enc).strip()
            if decoded:
                return decoded
        except Exception:
            continue

    raise ValueError("Failed to decode TXT file with standard text encodings")
