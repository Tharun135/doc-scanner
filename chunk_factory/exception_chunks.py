"""
Exception/Negative Knowledge Chunk Generator

Creates chunks for what NOT to do - critical for preventing bad rewrites.

Categories:
- UI labels (never rewrite)
- Legal text (never rewrite)
- Safety warnings (never rewrite)
- Error codes (never rewrite)
- Standards references (never rewrite)

Target: 100-200 chunks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk, ChunkTemplates
from typing import List, Dict, Any


# Negative knowledge - what NOT to do
NEGATIVE_KNOWLEDGE = [
    # UI Labels
    {
        "context": "UI button labels",
        "forbidden_action": "rewriting button text",
        "reason": "UI labels must match the actual interface exactly. Rewriting them will confuse users who cannot find the button you describe.",
        "doc_type": "ui",
        "severity": "critical",
        "examples": ["Save", "Cancel", "Submit", "Delete", "OK", "Apply"]
    },
    {
        "context": "menu items",
        "forbidden_action": "rewriting menu names",
        "reason": "Menu items must match the product interface exactly. Users follow documentation to find specific menus.",
        "doc_type": "ui",
        "severity": "critical",
        "examples": ["File > Open", "Edit > Preferences", "View > Toolbar"]
    },
    {
        "context": "field labels in forms",
        "forbidden_action": "rewriting form field names",
        "reason": "Field labels must match the UI exactly so users can locate the correct input field.",
        "doc_type": "ui",
        "severity": "critical",
        "examples": ["Username", "Email Address", "Password", "Confirm Password"]
    },
    {
        "context": "dialog box titles",
        "forbidden_action": "rewriting dialog titles",
        "reason": "Dialog titles must match exactly so users can identify which window the documentation refers to.",
        "doc_type": "ui",
        "severity": "critical",
        "examples": ["Save As", "Preferences", "Error", "Warning"]
    },
    {
        "context": "tab names",
        "forbidden_action": "rewriting tab labels",
        "reason": "Tab names must be exact matches to help users navigate multi-tab interfaces.",
        "doc_type": "ui",
        "severity": "critical",
        "examples": ["General", "Advanced", "Network", "Security"]
    },
    
    # Error Codes
    {
        "context": "error codes",
        "forbidden_action": "rewriting error code identifiers",
        "reason": "Error codes are exact identifiers used for troubleshooting. Changing them prevents users from finding solutions.",
        "doc_type": "api",
        "severity": "critical",
        "examples": ["ERROR_404", "ERR_CONNECTION_REFUSED", "0x80070005"]
    },
    {
        "context": "HTTP status codes",
        "forbidden_action": "rewriting standard HTTP codes",
        "reason": "HTTP status codes are international standards. They must be exact (200, 404, 500, etc.).",
        "doc_type": "api",
        "severity": "critical",
        "examples": ["200 OK", "404 Not Found", "500 Internal Server Error"]
    },
    
    # Legal/Safety
    {
        "context": "copyright notices",
        "forbidden_action": "rewriting copyright text",
        "reason": "Copyright notices are legal text that must remain exactly as written. Changes can invalidate legal protections.",
        "doc_type": "legal",
        "severity": "critical",
        "examples": ["Copyright © 2025", "All rights reserved", "Patent pending"]
    },
    {
        "context": "safety warnings",
        "forbidden_action": "rewriting safety text",
        "reason": "Safety warnings are legally required text that cannot be modified without legal review. They protect users and the company.",
        "doc_type": "safety",
        "severity": "critical",
        "examples": ["WARNING", "DANGER", "CAUTION", "NOTICE"]
    },
    {
        "context": "warranty disclaimers",
        "forbidden_action": "rewriting warranty text",
        "reason": "Warranty text is legal language reviewed by lawyers. Changing it can affect legal liability.",
        "doc_type": "legal",
        "severity": "critical",
        "examples": ["AS IS", "WITHOUT WARRANTY", "LIMITED WARRANTY"]
    },
    {
        "context": "regulatory compliance statements",
        "forbidden_action": "rewriting compliance text",
        "reason": "Compliance statements must match regulatory requirements exactly. Changes can void certifications.",
        "doc_type": "legal",
        "severity": "critical",
        "examples": ["FCC Compliance", "CE Mark", "ISO 9001 Certified"]
    },
    
    # Standards & Specifications
    {
        "context": "standard references",
        "forbidden_action": "rewriting standard names or numbers",
        "reason": "Standards have exact identifiers. Changing them makes it impossible to find the correct standard.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["ISO 8601", "RFC 2616", "IEEE 802.11"]
    },
    {
        "context": "API endpoints",
        "forbidden_action": "rewriting API URLs or paths",
        "reason": "API endpoints must be character-perfect. Any change breaks code examples and integration.",
        "doc_type": "api",
        "severity": "critical",
        "examples": ["/api/v1/users", "GET /posts/{id}", "https://api.example.com"]
    },
    {
        "context": "code snippets",
        "forbidden_action": "rewriting code syntax",
        "reason": "Code must be syntactically correct. Rewriting for style breaks functionality.",
        "doc_type": "api",
        "severity": "critical",
        "examples": ["import sys", "function getData()", "SELECT * FROM users"]
    },
    {
        "context": "version numbers",
        "forbidden_action": "rewriting version identifiers",
        "reason": "Version numbers are exact specifications. Changing them refers to wrong software versions.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["v2.5.1", "Version 3.0", "Build 12345"]
    },
    {
        "context": "file paths and names",
        "forbidden_action": "rewriting file system paths",
        "reason": "File paths must be exact for users to locate files and folders correctly.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["/etc/config.yaml", "C:\\Program Files\\", "~/.bashrc"]
    },
    
    # Product Names & Trademarks
    {
        "context": "product names",
        "forbidden_action": "rewriting official product names",
        "reason": "Product names are trademarks with specific capitalization and spacing. Changes violate brand guidelines.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["Microsoft Windows", "iPhone", "PostgreSQL"]
    },
    {
        "context": "trademarked terms",
        "forbidden_action": "rewriting trademarked names",
        "reason": "Trademarks must use exact spelling and capitalization to maintain legal protection.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["Bluetooth®", "Wi-Fi™", "UNIX®"]
    },
    {
        "context": "company names",
        "forbidden_action": "rewriting company names",
        "reason": "Company names have official spellings that must be preserved for legal and brand reasons.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["Microsoft Corporation", "Apple Inc.", "Google LLC"]
    },
    
    # Technical Specifications
    {
        "context": "units of measurement",
        "forbidden_action": "rewriting measurement units",
        "reason": "Units must be standard abbreviations (kg, m, GB) for technical accuracy.",
        "doc_type": "manual",
        "severity": "high",
        "examples": ["5 GB", "100 MHz", "25°C", "10 km/h"]
    },
    {
        "context": "mathematical formulas",
        "forbidden_action": "rewriting mathematical expressions",
        "reason": "Formulas must be mathematically exact. Rewriting changes meaning and results.",
        "doc_type": "manual",
        "severity": "critical",
        "examples": ["E = mc²", "a² + b² = c²", "∫ f(x) dx"]
    },
    {
        "context": "chemical formulas",
        "forbidden_action": "rewriting chemical notation",
        "reason": "Chemical formulas are exact scientific notation. Changes refer to different substances.",
        "doc_type": "manual",
        "severity": "critical",
        "examples": ["H₂O", "CO₂", "C₆H₁₂O₆"]
    },
]


def generate_exception_chunks() -> List[DecisionChunk]:
    """
    Generate negative knowledge chunks.
    
    These chunks explicitly tell the AI what NOT to rewrite.
    Critical for preventing damage to UI references, legal text, etc.
    
    Returns:
        List of DecisionChunks (target: 100-200 chunks)
    """
    chunks = []
    
    for item in NEGATIVE_KNOWLEDGE:
        # Main negative knowledge chunk
        chunks.append(ChunkTemplates.negative_knowledge(
            context=item["context"],
            forbidden_action=item["forbidden_action"],
            reason=item["reason"],
            doc_type=item["doc_type"],
            severity=item["severity"]
        ))
        
        # Create example chunks for each example
        if "examples" in item:
            for i, example in enumerate(item["examples"]):
                chunks.append(DecisionChunk.create(
                    title=f"Do NOT rewrite: {item['context']} - Example {i+1}",
                    question=f"Should this {item['context']} be rewritten: '{example}'?",
                    answer=f"NO. Never rewrite {item['context']}. They must remain exactly as shown. Reason: {item['reason']}",
                    knowledge_type="negative",
                    rewrite_allowed=False,
                    severity=item["severity"],
                    doc_type=item["doc_type"],
                    metadata={
                        "example": example,
                        "category": item["context"]
                    }
                ))
    
    print(f"✅ Generated {len(chunks)} negative knowledge chunks from {len(NEGATIVE_KNOWLEDGE)} categories")
    return chunks


def add_negative_knowledge(context: str, forbidden_action: str, reason: str,
                           doc_type: str = "ui", severity: str = "high",
                           examples: List[str] = None) -> List[DecisionChunk]:
    """
    Add custom negative knowledge.
    
    Use this to add company-specific or project-specific forbidden rewrites.
    """
    item = {
        "context": context,
        "forbidden_action": forbidden_action,
        "reason": reason,
        "doc_type": doc_type,
        "severity": severity,
        "examples": examples or []
    }
    
    NEGATIVE_KNOWLEDGE.append(item)
    
    chunks = []
    
    # Main chunk
    chunks.append(ChunkTemplates.negative_knowledge(
        context=context,
        forbidden_action=forbidden_action,
        reason=reason,
        doc_type=doc_type,
        severity=severity
    ))
    
    # Example chunks
    for i, example in enumerate(item["examples"]):
        chunks.append(DecisionChunk.create(
            title=f"Do NOT rewrite: {context} - Example {i+1}",
            question=f"Should this {context} be rewritten: '{example}'?",
            answer=f"NO. Never rewrite {context}. They must remain exactly as shown. Reason: {reason}",
            knowledge_type="negative",
            rewrite_allowed=False,
            severity=severity,
            doc_type=doc_type,
            metadata={
                "example": example,
                "category": context
            }
        ))
    
    return chunks


if __name__ == "__main__":
    # Test generation
    chunks = generate_exception_chunks()
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Average token count: {sum(c.get_token_count() for c in chunks) / len(chunks):.1f}")
    print(f"   Severity distribution:")
    for severity in ["low", "medium", "high", "critical"]:
        count = sum(1 for c in chunks if c.severity == severity)
        print(f"      {severity}: {count}")
    print(f"   Doc type distribution:")
    for doc_type in set(c.doc_type for c in chunks):
        count = sum(1 for c in chunks if c.doc_type == doc_type)
        print(f"      {doc_type}: {count}")
    print(f"\n✅ Negative knowledge chunk generation successful!")
