import re
from bs4 import BeautifulSoup
import html

def preprocess_text(content):
    # Strip HTML tags and decode entities
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    return text_content

def get_lines_with_numbers(text_content):
    return [(i + 1, line) for i, line in enumerate(text_content.split("\n"))]