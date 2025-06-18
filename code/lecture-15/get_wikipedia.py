# Import Ollama functions for summarization
from ollama import chat
import requests
from bs4 import BeautifulSoup
import html2text
import re


def summarize_wikipedia_article(url: str) -> str:
    """
    Fetch a Wikipedia article at the provided URL, parse its main content,
    Usage:
        summarize_wikipedia_article("https://en.wikipedia.org/wiki/Python_(programming_language)")
    """
    try:
        # Validate input
        if not url.startswith("http"):
            raise ValueError("URL must start with http or https.")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        content_div = soup.find("div", {"id": "bodyContent"})
        if not content_div:
            raise Exception("Could not find article content.")

        # Get the first 3 non-empty paragraphs
        paragraphs = []
        for p in content_div.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
            if len(paragraphs) == 3:
                break

        if not paragraphs:
            raise Exception("No suitable paragraphs found.")

        # Optionally clean citations like [1], [2]
        cleaned_paragraphs = [re.sub(r'\[\d+\]', '', para) for para in paragraphs]


        # text = html2text.html2text(paragraph)
        # print(paragraph)

        # # Create the summarization prompt for Ollama
        # prompt = f"Summarize the following text:\n\n{markdown_text}\n\nSummary:"
        
        # # Call the Ollama model to generate a summary
        # response = chat(
        #     model='llama3.2:1b',  
        #     messages=[
        #         {'role': 'user', 'content': prompt}
        #     ]
        # )
        # summary = response['message']['content']
        # summary = response.message.content.strip()
        return "\n\n".join(cleaned_paragraphs)
    except:
        return "Error"


summary = summarize_wikipedia_article("https://en.wikipedia.org/wiki/Model_Context_Protocol")
print(summary)