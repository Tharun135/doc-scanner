# Custom Terminology Management for Spell Checking

This document explains how to manage custom terminology that should be skipped during spell checking in the doc-scanner tool.

## Overview

The spell checker in doc-scanner can be configured to skip certain words that are not misspellings but rather technical terms, company-specific terminology, or domain-specific vocabulary. This prevents false positives where correct technical terms like "runtime", "WinCC", "SCADA", etc. are flagged as spelling errors.

## Quick Start

### Check if a word is whitelisted
```bash
python manage_terms.py check runtime
# Output: runtime: YES

python manage_terms.py check untie  
# Output: untie: NO
```

### View all whitelisted terms
```bash
python manage_terms.py list
```

### Count total terms
```bash
python manage_terms.py count
# Output: Total custom terms: 53
```

### Add a new term (temporary)
```bash
python manage_terms.py add myterm
# Output: Added: myterm
# Note: To persist this change, edit simple_terminology.py
```

## Default Terminology Included

The system comes pre-configured with common technical terms in these categories:

### Industrial Automation
- runtime, wincc, siemens, plc, hmi, scada
- fieldbus, profibus, profinet, modbus, ethernet
- opcua, tia, step7, winac, unified

### Software Terms
- config, configs, repo, repos, admin, admins
- backend, frontend, middleware, dataset, datasets
- namespace, namespaces, workflow, workflows
- timestamp, timestamps, hostname, hostnames

### Technical Acronyms
- api, sdk, ide, gui, cli, url, uri, http, https
- tcp, udp, dns, vpn, ssl, tls, json, xml, yaml

## Adding Custom Terms Permanently

To permanently add terms to the whitelist, edit the file `app/simple_terminology.py`:

1. Open the file in your editor
2. Find the `DEFAULT_TERMS` list
3. Add your terms to the appropriate section or add new ones at the end
4. Save the file

Example:
```python
DEFAULT_TERMS = [
    # ... existing terms ...
    "mynewterm",
    "anotherterm",
    "companyname"
]
```

## Integration with Spell Checker

The spell checker automatically uses the custom terminology. When processing text:

1. **Whitelisted terms are skipped** - No spelling suggestions generated
2. **Non-whitelisted terms are checked** - Spelling suggestions provided if misspelled
3. **Case insensitive matching** - "Runtime", "RUNTIME", "runtime" all match

## Example Usage

### Before Custom Terminology
Text: "The WinCC Unified Runtime app supports the configuration"
Result: Multiple spelling errors flagged for "WinCC", "Runtime", etc.

### After Custom Terminology  
Text: "The WinCC Unified Runtime app supports the configuration"
Result: No spelling errors - all terms are whitelisted

### Still Catches Real Errors
Text: "The runtyme is incorect"  
Result: Flags "runtyme" → "runtime" and "incorect" → "incorrect"

## Technical Implementation

The custom terminology system works by:

1. **Loading terms at startup** from `simple_terminology.py`
2. **Case-insensitive matching** against input words
3. **Early filtering** before expensive spell checking operations
4. **Integration** with both PySpellChecker and fallback methods

### Files Involved
- `app/simple_terminology.py` - Main terminology list and functions
- `app/rules/spelling_checker.py` - Spell checker with terminology integration
- `manage_terms.py` - Command-line management script

## Best Practices

1. **Keep terms lowercase** in the list for consistency
2. **Group terms by category** for easier maintenance  
3. **Avoid common words** that might mask real spelling errors
4. **Test thoroughly** after adding new terms
5. **Document company-specific terms** for team members

## Troubleshooting

### Term not being recognized
1. Check spelling in the terminology list
2. Ensure case-insensitive matching is working
3. Verify the term is in `DEFAULT_TERMS`
4. Test with `python manage_terms.py check yourterm`

### False positives still occurring
1. Add the problematic term to the list
2. Restart the application to reload terms
3. Check for typos in the terminology file

### Performance issues
1. Keep the terminology list reasonable in size
2. Consider grouping related terms
3. Remove unused or outdated terms

## API Reference

### Functions in simple_terminology.py

#### `is_custom_whitelisted(word)`
- **Purpose**: Check if a word should be skipped in spell checking
- **Parameters**: `word` (string) - The word to check
- **Returns**: `True` if whitelisted, `False` otherwise
- **Example**: `is_custom_whitelisted('runtime')` → `True`

#### `get_custom_terms()`
- **Purpose**: Get all custom terms for spell checker integration
- **Returns**: List of all terminology strings
- **Example**: `['runtime', 'wincc', 'api', ...]`

#### `add_custom_term(term)`
- **Purpose**: Add a term to the whitelist (runtime only)
- **Parameters**: `term` (string) - The term to add
- **Returns**: `True` if added, `False` if already exists
- **Note**: Changes are not persisted to file

### Command Line Interface

#### `python manage_terms.py check <term>`
Check if a specific term is whitelisted

#### `python manage_terms.py list`
Display all whitelisted terms with numbering

#### `python manage_terms.py count`
Show total number of whitelisted terms

#### `python manage_terms.py add <term>`
Add term to runtime list (not persisted)

## Contributing

When adding new terminology:

1. Consider if the term is truly technical/specialized
2. Check if it might be a common misspelling instead
3. Test with sample documents in your domain
4. Document the reason for inclusion
5. Group with similar terms for organization

## Examples for Your Domain

### For Software Documentation
```python
# Add to DEFAULT_TERMS:
"microservice", "kubernetes", "docker", "containerization",
"devops", "cicd", "webhook", "oauth", "restful"
```

### For Manufacturing/Industrial
```python
# Add to DEFAULT_TERMS:  
"plc", "hmi", "scada", "fieldbus", "modbus", "profinet",
"ethernet", "opcua", "automation", "robotics"
```

### For Company-Specific Terms
```python
# Add to DEFAULT_TERMS:
"acme", "acmesuite", "proprietary", "internal-tool-name"
```

This system provides a flexible, maintainable way to handle domain-specific terminology while still catching genuine spelling errors.
