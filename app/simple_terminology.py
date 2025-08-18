#!/usr/bin/env python3
"""
Simple terminology whitelist for spell checking.
"""

import json
import os

# Default terminology list including 'runtime'
DEFAULT_TERMS = [
    "runtime", "wincc", "siemens", "plc", "hmi", "scada",
    "fieldbus", "profibus", "profinet", "modbus", "ethernet",
    "opcua", "tia", "step7", "winac", "unified",
    "config", "configs", "repo", "repos", "admin", "admins",
    "backend", "frontend", "middleware", "dataset", "datasets",
    "namespace", "namespaces", "workflow", "workflows",
    "timestamp", "timestamps", "hostname", "hostnames",
    "api", "sdk", "ide", "gui", "cli", "url", "uri", "http", "https",
    "tcp", "udp", "dns", "vpn", "ssl", "tls", "json", "xml", "yaml"
]

def is_custom_whitelisted(word):
    """Check if a word is in the custom terminology whitelist."""
    return word.lower().strip() in [term.lower() for term in DEFAULT_TERMS]

def get_custom_terms():
    """Get all custom terms for use in spell checking."""
    return DEFAULT_TERMS

def add_custom_term(term):
    """Add a term to the custom whitelist."""
    if term.lower() not in [t.lower() for t in DEFAULT_TERMS]:
        DEFAULT_TERMS.append(term)
        return True
    return False

if __name__ == "__main__":
    print(f"Total terms: {len(DEFAULT_TERMS)}")
    print(f"Runtime whitelisted: {is_custom_whitelisted('runtime')}")
    print(f"Test whitelisted: {is_custom_whitelisted('test')}")
