import os
import glob
import pdfplumber
import random

# Base Directory for PDFs
PDF_DIR = os.path.join(os.path.dirname(__file__), "../N5~N1PDF")

# Cache to store loaded text to avoid re-reading PDFs
# Key: "N3_G", Value: "extracted text..."
_pdf_cache = {}

def load_context_for_level(level: str, category: str) -> str:
    """
    Loads relevant PDF text context based on JLPT level and category.
    
    Args:
        level: JLPT Level (e.g., "N3")
        category: Question category (e.g., "grammar", "reading", "vocab")
        
    Returns:
        Extracted text content from the PDF, or empty string if no PDF found.
    """
    global _pdf_cache
    
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
    if cache_key in _pdf_cache:
        print(f"PDF Context: Using cached content for {cache_key}")
        return _pdf_cache[cache_key]
    
    # 1. Search for "Textbook" (Minna no Nihongo) - Highest Priority
    # This provides high-quality, natural Japanese context (Dialogue, Sentence Patterns)
    # which is better than just a grammar list for generating natural quizzes.
    search_pattern_textbook = os.path.join(PDF_DIR, f"*{level}*みんなの日本語*.pdf")
    files_textbook = glob.glob(search_pattern_textbook)

    if files_textbook:
        target_file = files_textbook[0]
        print(f"PDF Context: Found TEXTBOOK match: {os.path.basename(target_file)}")
    
    # 2. If no textbook, search for Specific Logic (Level + Category)
    elif category:
        # Pattern: *N3*G*.pdf
        search_pattern_specific = os.path.join(PDF_DIR, f"*{level}*{cat_code}*.pdf")
        files_specific = glob.glob(search_pattern_specific)
        if files_specific:
            target_file = files_specific[0]
            print(f"PDF Context: Found specific match: {os.path.basename(target_file)}")
            
    # 3. Fallback to General Level PDF if still no target
    if not target_file:
        # Pattern: *N3*.pdf
        search_pattern_general = os.path.join(PDF_DIR, f"*{level}*.pdf")
        files_general = glob.glob(search_pattern_general)
        
        if files_general:
            # Sort by length to likely pick 'JLPT N3.pdf' over 'N3G.pdf' if both exist and handled above
            files_general.sort(key=len)
            target_file = files_general[0]
            print(f"PDF Context: Found general match: {os.path.basename(target_file)}")

    if not target_file:
        print(f"PDF Context: No PDF found for {level} {category}")
        return ""
        
    # Extract Text
    try:
        text_content = ""
        with pdfplumber.open(target_file) as pdf:
            # Limit to first 5-10 pages to capture style without overloading context
            # Or pick random pages?
            # Let's take pages 2-6 (skipping cover)
            max_pages = min(len(pdf.pages), 10)
            selected_pages = range(1, max_pages) # 0-indexed, skip 0 (cover)
            
            for i in selected_pages:
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text_content += page_text + "\n\n"
                    
        # Clean up
        text_content = text_content.strip()
        
        # Cache it (Limit size if needed, but text is usually small enough)
        # Truncate to approx 2000 chars to strictly limit context usage
        if len(text_content) > 3000:
             text_content = text_content[:3000] + "...(truncated)"
             
        _pdf_cache[cache_key] = text_content
        return text_content
        
    except Exception as e:
        print(f"PDF Context Error reading {target_file}: {e}")
        return ""
