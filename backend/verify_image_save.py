import pdfplumber
import os
from PIL import Image
import io

script_dir = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(script_dir, "../N5~N1PDF")
pdf_path = os.path.join(pdf_dir, "N5R.pdf")
output_path = os.path.join(script_dir, "test_extract.png")

print(f"Extracting image from: {pdf_path}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        if page.images:
            # pdfplumber .images attribute gives metadata. 
            # To get the actual image object, we often need .to_image() 
            # BUT .to_image() requires ImageMagick/Ghostscript usually.
            # Let's try the .images metadata approach + visual debugging?
            # Actually, pdfplumber's Page.to_image() renders the page. 
            # Let's try page.to_image() which renders the page content (including text and images) to a PIL image.
            # This is better because it captures everything as the user sees it.
            
            im = page.to_image(resolution=150)
            im.save(output_path, format="PNG")
            print(f"Success! Saved page render to: {output_path}")
        else:
            print("No images found on page 1.")
except Exception as e:
    print(f"Error: {e}")
