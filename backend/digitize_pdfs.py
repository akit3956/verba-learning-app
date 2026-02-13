import os
import glob
import json
import base64
import io
import asyncio
import pdfplumber
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Setup
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
PDF_DIR = os.path.join(os.path.dirname(__file__), "../N5~N1PDF")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data/few_shot")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

client = AsyncOpenAI(api_key=API_KEY)

async def process_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    print(f"Processing {filename}...")
    
    # Parse filename for level/category (e.g. N4G.pdf)
    level_cat = os.path.splitext(filename)[0] # N4G
    
    questions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Limit to first 3 pages + random middle page to get variety
            # Typically exams cover pages 2-10.
            # Let's pick page 2 and 3 specifically as they usually have Q1-Q5.
            target_pages = [1, 2, 3] # 0-indexed
            
            for page_idx in target_pages:
                if page_idx >= len(pdf.pages):
                    continue
                    
                print(f"  Scanning page {page_idx + 1}...")
                page = pdf.pages[page_idx]
                
                # Convert to image
                im_obj = page.to_image(resolution=150)
                pil_image = im_obj.original
                
                buffered = io.BytesIO()
                pil_image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # Call Vision API
                qs = await recognize_questions(img_str)
                if qs:
                    questions.extend(qs)
                    
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return

    # Save to JSON
    if questions:
        out_path = os.path.join(OUTPUT_DIR, f"{level_cat}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(questions)} questions to {out_path}")
    else:
        print(f"No questions found for {filename}")

async def recognize_questions(img_str):
    prompt = """
    Analyze this JLPT exam page.
    Extract all questions into this JSON format:
    [
      {
        "question": "Question text (include Kanzi/Furigana if possible)",
        "options": ["A", "B", "C", "D"],
        "correctIndex": 0, (Guess the most likely answer if not marked, or default to 0)
        "explanation": "Brief explanation of grammar/vocab point"
      }
    ]
    Return ONLY valid JSON array. If no questions, return [].
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                    ]
                }
            ],
            max_tokens=1500
        )
        content = response.choices[0].message.content
        # Simple clean info
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Vision API Error: {e}")
        return []

async def main():
    if not API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        return

    # Find all PDFs
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDFs.")
    
    # Run sequentially to accurately track progress (and cost)
    for pdf in pdf_files:
        await process_pdf(pdf)

if __name__ == "__main__":
    asyncio.run(main())
