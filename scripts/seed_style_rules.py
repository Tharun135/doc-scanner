import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

STYLE_RULES_DATA = [
    {
        "id": "style_length_01",
        "rule_type": "sentence_length",
        "description": "Use as few words as possible (less than 20 words per sentence). Break longer descriptions into smaller chunks.",
        "good_example": "When importing an app from an external source, ensure all dependencies are correctly configured. Check that the app is compatible with the existing system architecture.",
        "bad_example": "When importing an app from an external source, it is crucial to ensure that all dependencies are correctly configured and that the app is compatible with the existing system architecture to avoid potential integration issues."
    },
    {
        "id": "ui_interaction_01",
        "rule_type": "ui_interactions",
        "description": "If a topic describes a UI element that the user clicks on or interacts with, specify this with double quotation marks.",
        "good_example": "Click on \"OK\".",
        "bad_example": "Click on OK."
    },
    {
        "id": "ui_interaction_02",
        "rule_type": "ui_interactions",
        "description": "Entries in UI text fields are added as inline code.",
        "good_example": "Enter `1` in the \"Value\" field.",
        "bad_example": "Enter \"1\" in the `Value` field."
    },
    {
        "id": "ui_interaction_03",
        "rule_type": "ui_interactions",
        "description": "All terminal commands, code settings/parameters, messages, filenames etc. are written in inline code.",
        "good_example": "Change the value of the `dataType` setting to `Boolean`.",
        "bad_example": "Change the dataType to Boolean."
    },
    {
        "id": "ui_interaction_04",
        "rule_type": "ui_interactions",
        "description": "Use ++<key>++ to add keyboard shortcuts.",
        "good_example": "Enter the command and press `++enter++`.",
        "bad_example": "Enter the command and press \"Enter\"."
    },
    {
        "id": "tone_voice_01",
        "rule_type": "tone_voice",
        "description": "Use natural, conversational language. Avoid robotic, funny, cool, or clever expressions.",
        "good_example": "Welcome to this application.",
        "bad_example": "Hey there!"
    },
    {
        "id": "tone_voice_02",
        "rule_type": "tone_voice",
        "description": "Address users in second-person (you) and use first-person plural for the application (we). Use gender-neutral, polite language.",
        "good_example": "their, them, salesperson",
        "bad_example": "his, hers, salesman"
    },
    {
        "id": "tone_voice_03",
        "rule_type": "tone_voice",
        "description": "Avoid using negative contractions (like can't, won't) as they can appear too informal. Use positive contractions (like you'll, we've) to avoid sounding too formal.",
        "good_example": "cannot, will not, you will, we have",
        "bad_example": "can't, won't, you'll, we've"
    },
    {
        "id": "capitalization_01",
        "rule_type": "capitalization",
        "description": "Capitalize the first letter of the first word in a title, sentence, tooltip, menu item, list item, or button.",
        "good_example": "For more information, see Siemens Industry Online Support.",
        "bad_example": "For more information, see Siemens industry online support."
    },
    {
        "id": "capitalization_02",
        "rule_type": "capitalization",
        "description": "Capitalize proper nouns (Siemens, iOS, JavaScript, etc.) and named app functions/UI elements (Go to Settings, Allocate users in User Management, Press OK).",
        "good_example": "Go to Settings. Press OK.",
        "bad_example": "Go To Settings. Press Ok."
    },
    {
        "id": "headings_01",
        "rule_type": "headings",
        "description": "If the text under a heading describes what the user does, use an active sentence (e.g. -ing form) and not an imperative one.",
        "good_example": "Adding a new element",
        "bad_example": "Add a new element"
    },
    {
        "id": "grammar_tense_01",
        "rule_type": "grammar_tenses",
        "description": "Use present simple tense to describe an action or instruction. Only use simple verb forms in the past or future when necessary.",
        "good_example": "click, browse, upload, file loads, file loaded",
        "bad_example": "clicking, being clicked, was clicking, file has been loaded"
    },
    {
        "id": "active_voice_01",
        "rule_type": "active_voice",
        "description": "Use active voice. The reader can identify the actor more easily.",
        "good_example": "Configuration file opens. Click submit.",
        "bad_example": "The configuration file is opened. Submit is clicked by the user."
    },
    {
        "id": "punctuation_01",
        "rule_type": "punctuation",
        "description": "Minimalist punctuation. Use full stops at the end of all full sentences. Avoid colons wherever possible, for example: Username instead of Username:.",
        "good_example": "Username",
        "bad_example": "Username:"
    },
    {
        "id": "spacing_01",
        "rule_type": "spacing",
        "description": "No space before % or ellipsis. Add a space after colon or semi-colon. Add a space before and after quotation marks, hyphens, and em dashes. Add a space before unit of measurement (11 kg, 32 bits) except times (11am).",
        "good_example": "50%, 11am, Browse…",
        "bad_example": "50 %, 11 am, Browse …"
    },
    {
        "id": "lists_01",
        "rule_type": "lists",
        "description": "Use full stops consistently in lists and bullet points. Use fragments or full sentences in lists, not both.",
        "good_example": "Introduce lists with a description followed by a colon. Make lists parallel.",
        "bad_example": "Element 1: Description of element 1"
    },
    {
        "id": "lists_02",
        "rule_type": "lists",
        "description": "When a list item is followed by continuation content (result text or image) on the next indented line, end the list item line with two trailing spaces.",
        "good_example": "1. Click \"Install\".  \n   The \"Install App\" dialog opens.",
        "bad_example": "1. Click \"Install\".\n   The \"Install App\" dialog opens."
    },
    {
        "id": "notices_01",
        "rule_type": "notices",
        "description": "Use correct admonition syntax: danger (DANGER), warning (WARNING), tip (CAUTION), info (NOTICE). Custom titles indicate descriptive named notices; do not replace them with NOTICE.",
        "good_example": "!!! info \"Credentials for Databus\"",
        "bad_example": "!!! info \"Notice\" (lowercase title or generic notice prefix when custom title is intended)"
    },
    {
        "id": "vocabulary_01",
        "rule_type": "vocabulary",
        "description": "Do not use 'last' when you mean 'latest' or 'previous'. Use 'latest' for version to date, 'previous' for prior, 'recent' for time-focused.",
        "good_example": "Latest update. Previous version. Recent events.",
        "bad_example": "Last update. Last version. Last events."
    },
    {
        "id": "words_avoid_01",
        "rule_type": "words_to_avoid",
        "description": "Avoid filler words (therefore, according, furthermore, for that reason), weak expressions (it is, there is), nominalized verbs (preparation of -> prepares), please, should, could.",
        "good_example": "Click submit. Calculate performance.",
        "bad_example": "Therefore you should click submit. Please do not do this."
    }
]

def main():
    print("Initializing ChromaDB PersistentClient...")
    import chromadb
    local_db_path = os.path.join(project_root, 'docscanner_db')
    local_db_client = chromadb.PersistentClient(path=local_db_path)
    
    print("Creating/getting 'style_rules' collection...")
    style_rules_collection = local_db_client.get_or_create_collection(name="style_rules")
    
    print(f"Current documents in collection: {style_rules_collection.count()}")
    
    ids = []
    documents = []
    metadatas = []
    
    for rule in STYLE_RULES_DATA:
        ids.append(rule["id"])
        
        # Format the document text representation for RAG retrieval
        doc_text = (
            f"Rule Type: {rule['rule_type']}\n"
            f"Description: {rule['description']}\n"
            f"Good Example: {rule['good_example']}\n"
            f"Bad Example: {rule['bad_example']}"
        )
        documents.append(doc_text)
        
        metadatas.append({
            "rule_type": rule["rule_type"],
            "description": rule["description"],
            "good_example": rule["good_example"],
            "bad_example": rule["bad_example"]
        })
        
    print(f"Upserting {len(ids)} style rules...")
    style_rules_collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Success! Seeding complete. Total rules in DB: {style_rules_collection.count()}")

if __name__ == "__main__":
    main()
