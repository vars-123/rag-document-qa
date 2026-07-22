from unittest.mock import MagicMock, patch

from app.services.pdf_service import extract_text


def test_extract_text_uses_word_fallback() -> None:
    first_page = MagicMock()
    first_page.extract_text.return_value = "First page text"
    first_page.extract_words.return_value = []

    second_page = MagicMock()
    second_page.extract_text.return_value = None
    second_page.extract_words.return_value = [
        {"text": "Fallback", "top": 10, "x0": 0},
        {"text": "words", "top": 10, "x0": 50},
        {"text": "second", "top": 25, "x0": 0},
        {"text": "line", "top": 25, "x0": 60},
    ]

    pdf = MagicMock()
    pdf.pages = [first_page, second_page]

    mock_open = MagicMock()
    mock_open.__enter__.return_value = pdf

    with patch("app.services.pdf_service.pdfplumber.open", return_value=mock_open):
        text = extract_text("ignored.pdf")

    assert text == "First page text\n\nFallback words\nsecond line"
