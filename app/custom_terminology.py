"""
Custom terminology management for spell checking.
Allows users to maintain a whitelist of terms that should be skipped during spelling checks.
"""

import json
import os
from typing import List, Set
import logging

class CustomTerminologyManager:
    """Manages custom terminology whitelist for spell checking."""
    
    def __init__(self, config_file: str = None):
        """Initialize the terminology manager.
        
        Args:
            config_file: Path to the custom terminology configuration file.
                        If None, uses default location.
        """
        if config_file is None:
            # Default location in the rules directory
            rules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules')
            config_file = os.path.join(rules_dir, 'custom_terminology.json')
           
        self.config_file = config_file
        self.custom_terms: Set[str] = set()
        self.load_custom_terms()
    
    def load_custom_terms(self) -> None:
        """Load custom terms from the configuration file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Support both list format and categorized format
                if isinstance(data, list):
                    self.custom_terms = set(term.lower() for term in data)
                elif isinstance(data, dict):
                    # Flatten all categories
                    terms = []
                    for category_terms in data.values():
                        if isinstance(category_terms, list):
                            terms.extend(category_terms)
                    self.custom_terms = set(term.lower() for term in terms)
                    
                print(f"Loaded {len(self.custom_terms)} custom terms from {self.config_file}")
            else:
                # Create default configuration with some common industrial/technical terms
                self._create_default_config()
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not load custom terminology from {self.config_file}: {e}")
            self.custom_terms = set()
    
    def _create_default_config(self) -> None:
        """Create a default configuration file with common terms."""
        default_terms = {
            "industrial_automation": [
                "runtime", "wincc", "siemens", "plc", "hmi", "scada",
                "fieldbus", "profibus", "profinet", "modbus", "ethernet",
                "opcua", "tia", "step7", "winac", "unified"
            ],
            "software_terms": [
                "config", "configs", "repo", "repos", "admin", "admins",
                "backend", "frontend", "middleware", "dataset", "datasets",
                "namespace", "namespaces", "workflow", "workflows",
                "timestamp", "timestamps", "hostname", "hostnames"
            ],
            "company_specific": [
                # Add your company/project specific terms here
            ],
            "technical_acronyms": [
                "api", "sdk", "ide", "gui", "cli", "url", "uri", "http", "https",
                "tcp", "udp", "dns", "vpn", "ssl", "tls", "json", "xml", "yaml"
            ]
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_terms, f, indent=4, sort_keys=True)
            
            # Load the default terms
            self.load_custom_terms()
            print(f"Created default custom terminology file: {self.config_file}")
            
        except IOError as e:
            print(f"Could not create default terminology file: {e}")
    
    def save_custom_terms(self) -> bool:
        """Save current custom terms to the configuration file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Load existing structure to preserve categories
            existing_data = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # If it's a simple list, convert to categorized format
            if isinstance(existing_data, list):
                existing_data = {"custom_terms": existing_data}
            
            # Update with current terms (maintain existing categories + add new ones)
            if "user_added" not in existing_data:
                existing_data["user_added"] = []
            
            # Add any new terms to user_added category
            all_existing_terms = set()
            for category_terms in existing_data.values():
                if isinstance(category_terms, list):
                    all_existing_terms.update(term.lower() for term in category_terms)
            
            new_terms = self.custom_terms - all_existing_terms
            if new_terms:
                existing_data["user_added"].extend(sorted(new_terms))
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, sort_keys=True)
            
            print(f"Saved custom terminology to {self.config_file}")
            return True
            
        except IOError as e:
            print(f"Could not save custom terminology: {e}")
            return False
    
    def add_term(self, term: str) -> bool:
        """Add a term to the custom whitelist.
        
        Args:
            term: The term to add.
            
        Returns:
            True if term was added, False if it already existed.
        """
        term_lower = term.lower().strip()
        if term_lower and term_lower not in self.custom_terms:
            self.custom_terms.add(term_lower)
            print(f"Added custom term: {term_lower}")
            return True
        return False
    
    def remove_term(self, term: str) -> bool:
        """Remove a term from the custom whitelist.
        
        Args:
            term: The term to remove.
            
        Returns:
            True if term was removed, False if it didn't exist.
        """
        term_lower = term.lower().strip()
        if term_lower in self.custom_terms:
            self.custom_terms.remove(term_lower)
            print(f"Removed custom term: {term_lower}")
            return True
        return False
    
    def add_terms(self, terms: List[str]) -> int:
        """Add multiple terms to the custom whitelist.
        
        Args:
            terms: List of terms to add.
            
        Returns:
            Number of new terms added.
        """
        added_count = 0
        for term in terms:
            if self.add_term(term):
                added_count += 1
        return added_count
    
    def is_whitelisted(self, word: str) -> bool:
        """Check if a word is in the custom whitelist.
        
        Args:
            word: The word to check.
            
        Returns:
            True if the word should be skipped in spell checking.
        """
        return word.lower().strip() in self.custom_terms
    
    def get_all_terms(self) -> List[str]:
        """Get all custom terms as a sorted list.
        
        Returns:
            Sorted list of all custom terms.
        """
        return sorted(self.custom_terms)
    
    def get_terms_count(self) -> int:
        """Get the number of custom terms.
        
        Returns:
            Number of terms in the whitelist.
        """
        return len(self.custom_terms)
    
    def clear_all_terms(self) -> None:
        """Clear all custom terms from memory (doesn't save automatically)."""
        self.custom_terms.clear()
        print("Cleared all custom terms from memory")

# Global instance for easy access
_terminology_manager = None

def get_terminology_manager() -> CustomTerminologyManager:
    """Get the global terminology manager instance."""
    global _terminology_manager
    if _terminology_manager is None:
        _terminology_manager = CustomTerminologyManager()
    return _terminology_manager

def is_custom_whitelisted(word: str) -> bool:
    """Check if a word is in the custom terminology whitelist.
    
    This is a convenience function for the spelling checker.
    """
    return get_terminology_manager().is_whitelisted(word)

def add_custom_term(term: str) -> bool:
    """Add a term to the custom whitelist and save.
    
    This is a convenience function that also saves the changes.
    """
    manager = get_terminology_manager()
    if manager.add_term(term):
        manager.save_custom_terms()
        return True
    return False

def get_custom_terms() -> List[str]:
    """Get all custom terms for use in spell checking."""
    return get_terminology_manager().get_all_terms()
