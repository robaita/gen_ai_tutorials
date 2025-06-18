import fitz  # PyMuPDF
import re

documents = {}

def load_ramayan_chapters(pdf_path: str):
    """Reads Ramayan PDF and splits it into chapters"""
    try:
        chapter_map = {
                "Introduction".upper(): range(0, 2),
                "THE BIRTH OF RAMA".upper(): range(2, 3),
                "The Valiant Princes".upper(): range(3, 6),
                "SITA'S SWAYAMVAR".upper(): range(6, 8),
                "KAIKEYI AND HER WISHES".upper(): range(7, 21),
                "The demons in the forests".upper(): range(21, 24),
                "The Kidnapping of Sita".upper(): range(24, 27),
                "Rama searches for Sita".upper(): range(27, 29),
                "The land of the monkeys".upper(): range(29, 33),
                "Hanuman meets Sita - Lanka is destroyed".upper(): range(33, 37),
                "The War".upper(): range(37, 46),  
            }
        
        chapters = {}
        with fitz.open(pdf_path) as doc:
            for chapter, pages in chapter_map.items():
                full_text = ""
                for i, page in enumerate(doc):
                    pages = list(pages)
                    # print("Pages:",pages)
                    if i in pages:
                        chapter_name = chapter
                        break
                    else:
                        chapter_name = "Unknown Chapter"

                    full_text += page.get_text()
                documents[chapter_name] = full_text

        # # Split into chapters based on keyword (adjust as per actual book format)
        
        # print(chapters)
        
        # # `chapters` will have format: ['', '1', 'Chapter 1 content...', '2', 'Chapter 2 content...', ...]
        # for i in range(1, len(chapters), 2):
        #     chapter_number = chapters[i]
        #     chapter_content = chapters[i + 1].strip()
        #     doc_id = f"ramayan-chapter-{chapter_number}"
        #     documents[doc_id] = chapter_content

        print(f"Loaded {len(chapter_map)} chapters from Ramayan.")

    except Exception as e:
        print(f"Error reading Ramayan PDF: {e}")


def get_document(doc_id: str) -> str:
    """Retrieve the content of a specific chapter from Ramayan"""
    global documents
    print(documents.keys())
    return documents.get(doc_id, f"No chapter found with ID '{doc_id}'")

load_ramayan_chapters("data/RAMAYANA.pdf")

chapter_info = get_document("THE BIRTH OF RAMA")
print(chapter_info)