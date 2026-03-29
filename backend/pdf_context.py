import os
import glob
import pdfplumber
import random

# Base Directory for 教材 (PDFs, PPTs, etc.)
PDF_DIR = os.path.join(os.path.dirname(__file__), "../N5~N1PDF")

# Cache to store loaded text to avoid re-reading files
_context_cache = {}

def extract_text_from_file(file_path: str) -> str:
    """Extracts text based on file extension (PDF, PPTX, XLSX)."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                # Limit to first 10 pages for search relevance and context size
                max_pages = min(len(pdf.pages), 10)
                for i in range(max_pages):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
            return text_content
        elif ext == ".pptx":
            from utils import extract_text_from_pptx
            with open(file_path, "rb") as f:
                return extract_text_from_pptx(f.read())
        elif ext == ".xlsx":
            from utils import extract_text_from_xlsx
            with open(file_path, "rb") as f:
                return extract_text_from_xlsx(f.read())
    except Exception as e:
        print(f"Error extracting from {file_path}: {e}")
    return ""

def load_context_for_level(level: str, category: str) -> str:
    """
    Loads relevant PDF/PPT/Excel context based on JLPT level and category.
    Searches the N5~N1PDF directory.
    """
    global _context_cache
    
    # Map category to file code
    cat_code = ""
    if category in ["grammar", "文法", "quiz"]:
        cat_code = "G"
    elif category in ["reading", "読解"]:
        cat_code = "R"
    elif category in ["vocab", "語彙"]:
        cat_code = "V"
        
    cache_key = f"{level}_{cat_code}"
    
    # Return cached content if available
    if cache_key in _context_cache:
        return _context_cache[cache_key]
    
    # Extensions to search for
    extensions = [".pdf", ".pptx", ".xlsx"]
    target_file = None

    # 1. Search for "みんなの日本語" (Textbook) - Highest Priority
    for ext in extensions:
        search_pattern = os.path.join(PDF_DIR, f"*{level}*みんなの日本語*{ext}")
        files = glob.glob(search_pattern)
        if files:
            target_file = files[0]
            break
    
    # 2. Search for Specific (Level + Category code)
    if not target_file and cat_code:
        for ext in extensions:
            search_pattern = os.path.join(PDF_DIR, f"*{level}*{cat_code}*{ext}")
            files = glob.glob(search_pattern)
            if files:
                target_file = files[0]
                break
            
    # 3. Fallback to General Level match
    if not target_file:
        for ext in extensions:
            search_pattern = os.path.join(PDF_DIR, f"*{level}*{ext}")
            files = glob.glob(search_pattern)
            if files:
                files.sort(key=len) # Pick the shortest match (e.g., 'N3.pdf' over 'N3_Vocab.pdf')
                target_file = files[0]
                break

    if not target_file:
        print(f"教材 Loader: No matching file found for {level} {category} in {PDF_DIR}")
        return ""
        
    print(f"教材 Loader: Found reference file: {os.path.basename(target_file)}")
    text_content = extract_text_from_file(target_file)
    text_content = text_content.strip()
    
    # Cache and return (truncate to 3000 chars)
    if len(text_content) > 3000:
         text_content = text_content[:3000] + "...(truncated)"
         
    _context_cache[cache_key] = text_content
    return text_content
