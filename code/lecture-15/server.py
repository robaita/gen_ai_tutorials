# server.py
from mcp.server.fastmcp import FastMCP, Image
import requests
from bs4 import BeautifulSoup
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import openai
import re
import fitz  # PyMuPDF
import urllib.parse
from mcp.server.fastmcp.prompts import base
from PIL import Image as PILImage


# Import Ollama functions for summarization
from ollama import chat, ChatResponse

# Create an MCP server
mcp = FastMCP("MCP-Demo")

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

        print(f"Loaded {len(chapter_map)} chapters from Ramayan.")

    except Exception as e:
        print(f"Error reading Ramayan PDF: {e}")

load_ramayan_chapters("data/RAMAYANA.pdf")

@mcp.tool()
def summarize_wikipedia_article(url: str) -> str:
    """
    Fetch the first clean paragraph from a Wikipedia article.
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
        return cleaned_paragraphs

    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Unexpected error: {str(e)}")) from e
    
# Get the current temprature
@mcp.tool()
def get_weather_details(city: str) -> str:
    """
    Given the city name, the system could help with the following details:
    Location, Visibility, Pressure, Humidity, Dew Point
    """

    URL = "https://www.timeanddate.com/weather/india/" + city.lower()
    HEADERS = { "User-Agent": "Mozilla/5.0" }

    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.select_one("section.bk-focus table")
    if not table:
        raise ValueError("Weather information table not found.")

    weather_data = {}
    for row in table.find_all("tr"):
        heading = row.find("th").text.strip().rstrip(":")
        value = row.find("td").text.strip()

        if heading == "Location":
            weather_data["Location"] = value
        elif heading == "Dew Point":
            weather_data["Dew Point"] = value
        elif heading == "Humidity":
            weather_data["Humidity"] = value
        elif heading == "Pressure":
            weather_data["Pressure"] = value
        elif heading == "Visibility":
            weather_data["Visibility"] = value

    return weather_data


# Resource to retrieve document content by ID
@mcp.resource("doc://{doc_id}")
def get_document(doc_id: str) -> str:
    """Retrieve the content of Ramayan document"""
    try:
        decoded_id = urllib.parse.unquote(doc_id)
        return documents[decoded_id]
    except:
        return f"No chapter found with ID '{doc_id}'"

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name.upper()}!"


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]


