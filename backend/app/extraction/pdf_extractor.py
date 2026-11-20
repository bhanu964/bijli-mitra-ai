import fitz
from typing import List, Dict, Any

class PDFExtractor:
    @staticmethod
    def extract_text_by_pages(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts digital text and metadata from PDF pages using PyMuPDF.
        """
        results = []
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            char_count = len(text.strip())
            results.append({
                "page_number": i + 1,
                "text": text,
                "is_scanned": char_count < 30,
                "char_count": char_count
            })
        doc.close()
        return results
