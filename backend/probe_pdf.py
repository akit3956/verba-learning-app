import pdfplumber
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(script_dir, "../N5~N1PDF")
pdf_path = os.path.join(pdf_dir, "N5R.pdf")

print(f"Script Dir: {script_dir}")
print(f"PDF Dir: {pdf_dir}")
print(f"Inspecting: {pdf_path}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        
        # Inspect first 3 pages
        for i, page in enumerate(pdf.pages[:3]):
            print(f"\n--- Page {i+1} ---")
            # Check for images
            if page.images:
                print(f"Found {len(page.images)} images.")
                for img in page.images:
                    print(f" - Image: {img['width']}x{img['height']}")
            else:
                print("No images found.")
except Exception as e:
    print(f"Error: {e}")
