import pdfplumber

def read_pdf_plumb(path: str) -> None:
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- Page {i+1} ---")
            print(page.extract_text() or "[No text found]")

if __name__ == "__main__":
    read_pdf_plumb("20230629-shailesh .pdf")
