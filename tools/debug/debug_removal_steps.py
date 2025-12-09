#!/usr/bin/env python3
"""
Step-by-step debug to see what gets removed
"""
import requests
from bs4 import BeautifulSoup

def debug_removal_steps():
    url = "https://learn.microsoft.com/en-us/style-guide/welcome/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    
    print(f"Initial text length: {len(soup.get_text())}")
    
    # Test each removal step individually
    removals = [
        (["nav", "footer", "aside", "script", "style", "noscript"], "Basic tags"),
        (["[class*='toc']"], "TOC elements"),
        (["[class*='nav']"], "Nav class elements"),
        (["[class*='breadcrumb']"], "Breadcrumb elements"),
        (["[class*='sidebar']"], "Sidebar elements"),
        (["[class*='menu']"], "Menu elements"),
        (["[role='navigation']"], "Navigation role"),
        (["[class*='skip']"], "Skip elements"),
        (["[class*='alert']"], "Alert elements"),
        (["[class*='banner']"], "Banner elements"),
        (["[class*='header']"], "Header elements"),
        ([".uhf-"], "UHF elements"),
        (["[id*='uhf']"], "UHF ID elements"),
    ]
    
    for selectors, name in removals:
        soup_copy = BeautifulSoup(html, "html.parser")
        
        # Remove previous steps
        for prev_selectors, _ in removals[:removals.index((selectors, name))]:
            for sel in prev_selectors:
                if sel.startswith("[") or "." in sel:
                    for el in soup_copy.select(sel):
                        el.decompose()
                else:
                    for el in soup_copy(sel):
                        el.decompose()
        
        # Count elements matching current selector
        count = 0
        for selector in selectors:
            if selector.startswith("[") or "." in selector:
                elements = soup_copy.select(selector)
            else:
                elements = soup_copy(selector)
            count += len(elements)
            
        before_text = len(soup_copy.get_text())
        
        # Remove current selector elements
        for selector in selectors:
            if selector.startswith("[") or "." in selector:
                for el in soup_copy.select(selector):
                    el.decompose()
            else:
                for el in soup_copy(selector):
                    el.decompose()
        
        after_text = len(soup_copy.get_text())
        print(f"{name}: found {count} elements, text length {before_text} -> {after_text} (removed {before_text - after_text})")

if __name__ == "__main__":
    debug_removal_steps()
