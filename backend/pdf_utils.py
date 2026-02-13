import os
import random
import pdfplumber
import io
import base64

# Path to PDFs
PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../N5~N1PDF")

def get_random_page_image(level: str):
    """
    Selects a random PDF for the given level (e.g., 'N4') 
    and returns a random page as a base64 encoded image string.
    """
    if not os.path.exists(PDF_DIR):
        print(f"PDF Dir not found: {PDF_DIR}")
        return None, "PDF directory not found"

    # Filter files for the level (e.g., starts with "N4")
    files = [f for f in os.listdir(PDF_DIR) if f.startswith(level) and f.endswith(".pdf")]
    
    if not files:
        return None, f"No PDFs found for level {level}"
    
    selected_file = random.choice(files)
    pdf_path = os.path.join(PDF_DIR, selected_file)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            if total_pages == 0:
                return None, "Empty PDF"
                
            # Pick casual page (avoid first cover page if possible)
            # Exams usually start around page 1 or 2.
            page_idx = random.randint(0, total_pages - 1)
            page = pdf.pages[page_idx]
            
            # Convert to image (Resolution 150 is decent for OCR)
            # Note: page.to_image() returns a PageImage object, .original is the PIL Image
            im_obj = page.to_image(resolution=200)
            pil_image = im_obj.original
            
            # Convert to Base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return {
                "filename": selected_file,
                "page": page_idx + 1,
                "image_base64": img_str
            }, None
            
    except Exception as e:
        return None, str(e)
