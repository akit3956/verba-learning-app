import pdfplumber
import sys
import os

files = [
    "/Users/akiratakushi/AI学習/jlpt_app/N5~N1PDF/N4G.pdf",
    "/Users/akiratakushi/AI学習/jlpt_app/N5~N1PDF/N1R.pdf"
]

for pdf_path in files:
    print(f"\n====== Inspecting: {os.path.basename(pdf_path)} ======")
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        continue

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages[:3]): # Read first 3 pages
                print(f"--- Page {i+1} ---")
                text = page.extract_text()
                print(text)
                print("\n")
    except Exception as e:
        print(f"Error reading PDF: {e}")
