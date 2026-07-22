import pdfplumber


def _words_to_text(words: list[dict]) -> str:
    if not words:
        return ""

    lines: list[list[str]] = []
    current_top: float | None = None
    current_line: list[str] = []

    for word in sorted(words, key=lambda item: (item.get("top", 0.0), item.get("x0", 0.0))):
        text = str(word.get("text", "")).strip()
        if not text:
            continue

        top = float(word.get("top", 0.0))
        if current_top is None or abs(top - current_top) <= 3.0:
            current_line.append(text)
            current_top = top if current_top is None else (current_top + top) / 2
            continue

        if current_line:
            lines.append(current_line)
        current_line = [text]
        current_top = top

    if current_line:
        lines.append(current_line)

    return "\n".join(" ".join(line) for line in lines if line)


def extract_text(file_path: str) -> str:
    pages: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text)
                continue

            fallback_text = _words_to_text(page.extract_words())
            if fallback_text:
                pages.append(fallback_text)
    return "\n\n".join(pages)
