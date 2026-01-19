"""
Strengthen RAG Database with All Issue Type Examples

This script adds transformation examples for ALL issue types to ChromaDB
so RAG can provide relevant examples for any detected issue.

Issue types covered:
- Long sentences
- Vague terms
- Missing prerequisites
- Undefined acronyms
- Inconsistent terminology
- Mixed tense
- Dense steps
- Step order problems

Usage:
    python scripts/strengthen_rag_all_issues.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import chromadb
from chromadb.config import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_transformation_examples():
    """Get transformation examples for all issue types."""
    
    return {
        # LONG SENTENCES - Break into shorter, clearer sentences
        "long_sentence": [
            (
                "The system processes incoming requests by first validating the user credentials, then checking the request parameters against the schema, and finally forwarding the validated request to the appropriate handler for processing.",
                "The system processes incoming requests in three steps. First, it validates user credentials. Next, it checks request parameters against the schema. Finally, it forwards the validated request to the appropriate handler.",
                "42-word sentence → 4 shorter sentences"
            ),
            (
                "In the configuration file you can activate to print out this information in the user log file in a cyclic way which means that older entries will be overwritten when the maximum file size is reached.",
                "In the configuration file, you can activate cyclic logging. This prints information to the user log file. When the file reaches maximum size, older entries are overwritten.",
                "Split on natural boundaries (prepositional phrases)"
            ),
            (
                "The application monitors the device status continuously and when an error is detected it automatically sends a notification to the administrator and creates a log entry in the system database for future reference.",
                "The application monitors the device status continuously. When an error is detected, it performs two actions. First, it sends a notification to the administrator. Second, it creates a log entry in the system database.",
                "Split on conjunction 'and'"
            ),
            (
                "To configure the network settings, open the configuration panel, navigate to the network section, select the appropriate interface, enter the IP address and subnet mask, and click Apply to save the changes.",
                "To configure the network settings, follow these steps. Open the configuration panel and navigate to the network section. Select the appropriate interface. Enter the IP address and subnet mask. Click Apply to save the changes.",
                "Break procedural sentence into steps"
            ),
        ],
        
        # VAGUE TERMS - Replace with specific, concrete terms
        "vague_term": [
            (
                "The system handles various types of requests.",
                "The system handles GET, POST, PUT, and DELETE requests.",
                "Replace 'various types' with specific list"
            ),
            (
                "Some settings may need to be configured.",
                "The timeout, retry count, and buffer size settings must be configured.",
                "Replace 'some settings' with exact settings"
            ),
            (
                "Several factors affect performance.",
                "Network latency, CPU usage, and memory allocation affect performance.",
                "Replace 'several factors' with specific factors"
            ),
            (
                "You can do various things with this API.",
                "You can create, read, update, and delete resources with this API.",
                "Replace 'various things' with specific operations"
            ),
            (
                "The system provides multiple options.",
                "The system provides three authentication options: basic, OAuth2, and API key.",
                "Replace 'multiple options' with enumerated options"
            ),
            (
                "There are different ways to connect.",
                "You can connect via USB, Ethernet, or Wi-Fi.",
                "Replace 'different ways' with specific connection methods"
            ),
        ],
        
        # MISSING PREREQUISITES - Add prerequisites before procedural steps
        "missing_prerequisite": [
            (
                "To configure the device, open the settings panel and enter the parameters.",
                "Prerequisites: Ensure the device is powered on and connected to the network.\n\nTo configure the device, open the settings panel and enter the parameters.",
                "Add prerequisite about device state"
            ),
            (
                "Run the installation script to set up the application.",
                "Prerequisites: Install Python 3.11 or later and ensure pip is available.\n\nRun the installation script to set up the application.",
                "Add software prerequisites"
            ),
            (
                "To access the admin panel, navigate to /admin in your browser.",
                "Prerequisites: You must have administrator credentials and be logged in.\n\nTo access the admin panel, navigate to /admin in your browser.",
                "Add permission prerequisites"
            ),
        ],
        
        # UNDEFINED ACRONYMS - Define acronyms on first use
        "undefined_acronym": [
            (
                "The API supports REST operations.",
                "The API supports REST (Representational State Transfer) operations.",
                "Define REST on first use"
            ),
            (
                "Configure the MQTT broker settings.",
                "Configure the MQTT (Message Queuing Telemetry Transport) broker settings.",
                "Define MQTT on first use"
            ),
            (
                "The system uses TLS encryption.",
                "The system uses TLS (Transport Layer Security) encryption.",
                "Define TLS on first use"
            ),
            (
                "Connect via SSH to access the device.",
                "Connect via SSH (Secure Shell) to access the device.",
                "Define SSH on first use"
            ),
            (
                "The JSON response contains the data.",
                "The JSON (JavaScript Object Notation) response contains the data.",
                "Define JSON on first use"
            ),
        ],
        
        # INCONSISTENT TERMINOLOGY - Use same term throughout
        "inconsistent_terminology": [
            (
                "First, configure the settings. Then, modify the preferences. Finally, update the options.",
                "First, configure the settings. Then, modify the settings. Finally, update the settings.",
                "Use 'settings' consistently instead of settings/preferences/options"
            ),
            (
                "The program starts the service. The application initializes the daemon.",
                "The application starts the service. The application initializes the daemon.",
                "Use 'application' consistently instead of program/application"
            ),
            (
                "Click the button to submit. Press the key to confirm.",
                "Click the button to submit. Click the button to confirm.",
                "Use 'click' consistently instead of click/press"
            ),
        ],
        
        # MIXED TENSE - Use consistent tense (present for technical docs)
        "mixed_tense": [
            (
                "The system will process the request and sent the response.",
                "The system processes the request and sends the response.",
                "Use present tense consistently"
            ),
            (
                "The application started and initializes the database.",
                "The application starts and initializes the database.",
                "Use present tense consistently"
            ),
            (
                "Users can configure settings and will receive notifications.",
                "Users can configure settings and receive notifications.",
                "Use present tense consistently"
            ),
        ],
        
        # DENSE STEPS - Break complex steps into substeps
        "dense_step": [
            (
                "Configure the network by opening the settings, selecting the network tab, entering the IP address, subnet mask, gateway, and DNS servers, and clicking Apply.",
                "Configure the network:\n1. Open the settings panel\n2. Select the network tab\n3. Enter the following:\n   - IP address\n   - Subnet mask\n   - Gateway\n   - DNS servers\n4. Click Apply",
                "Break into numbered substeps"
            ),
            (
                "Install the software by downloading the installer, running it with administrator privileges, accepting the license, choosing the installation directory, selecting components, and clicking Install.",
                "Install the software:\n1. Download the installer\n2. Run the installer with administrator privileges\n3. Accept the license agreement\n4. Choose the installation directory\n5. Select the components to install\n6. Click Install",
                "One action per step"
            ),
        ],
        
        # STEP ORDER PROBLEMS - Reorder steps logically
        "step_order_problem": [
            (
                "1. Start the application\n2. Connect to the network\n3. Install the software",
                "1. Install the software\n2. Connect to the network\n3. Start the application",
                "Install before use"
            ),
            (
                "1. Enter your password\n2. Enter your username\n3. Click Login",
                "1. Enter your username\n2. Enter your password\n3. Click Login",
                "Username before password"
            ),
            (
                "1. Click Save\n2. Make your changes\n3. Open the file",
                "1. Open the file\n2. Make your changes\n3. Click Save",
                "Open → Edit → Save logical order"
            ),
        ],
    }


def strengthen_rag_database():
    """Add all issue type examples to ChromaDB."""
    
    logger.info("Creating transformation examples for all issue types...")
    all_examples = get_all_transformation_examples()
    
    total_count = sum(len(examples) for examples in all_examples.values())
    logger.info(f"Generated {total_count} transformation examples across {len(all_examples)} issue types")
    
    # Connect to ChromaDB
    logger.info("Connecting to ChromaDB...")
    chroma_client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection(name="writing_rules")
        logger.info(f"Found existing collection with {collection.count()} documents")
    except Exception as e:
        logger.info(f"Creating new collection: {e}")
        collection = chroma_client.create_collection(
            name="writing_rules",
            metadata={"description": "Technical writing rules and transformations"}
        )
    
    # Prepare data for ChromaDB
    documents = []
    metadatas = []
    ids = []
    doc_counter = collection.count() + 1  # Start after existing documents
    
    for issue_type, examples in all_examples.items():
        logger.info(f"Processing {len(examples)} examples for {issue_type}...")
        
        for before, after, explanation in examples:
            # Create document text
            doc_text = f"Issue Type: {issue_type}\n\nBefore: {before}\n\nAfter: {after}\n\nExplanation: {explanation}"
            documents.append(doc_text)
            
            # Create metadata
            metadata = {
                "rule_id": issue_type,
                "issue_type": issue_type,
                "before": before[:200],  # Truncate for metadata
                "after": after[:200],
                "explanation": explanation,
                "source": "all_issues_transformations"
            }
            metadatas.append(metadata)
            
            # Use unique ID
            ids.append(f"{issue_type}_example_{doc_counter}")
            doc_counter += 1
    
    # Add to ChromaDB
    logger.info(f"Adding {len(documents)} documents to ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.info(f"✅ Successfully added {len(documents)} transformation examples to ChromaDB")
    logger.info(f"📊 Collection now has {collection.count()} total documents")
    
    # Test queries for each issue type
    logger.info("\n🧪 Testing queries for each issue type...")
    
    test_queries = {
        "long_sentence": "The system processes incoming requests by first validating and then checking parameters and finally forwarding to handler",
        "vague_term": "The system handles various types of data",
        "undefined_acronym": "Configure the API settings",
        "inconsistent_terminology": "Configure the settings and modify the preferences",
    }
    
    for issue_type, query in test_queries.items():
        logger.info(f"\n  Testing {issue_type}: '{query[:50]}...'")
        results = collection.query(
            query_texts=[query],
            n_results=2,
            where={"issue_type": issue_type}
        )
        
        if results and results.get('documents') and results['documents'][0]:
            logger.info(f"    ✅ Found {len(results['documents'][0])} relevant examples")
            if results['documents'][0]:
                meta = results['metadatas'][0][0]
                logger.info(f"    Top match: {meta.get('explanation', 'N/A')}")
        else:
            logger.info(f"    ⚠️ No matches found")
    
    return collection


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("STRENGTHENING RAG DATABASE WITH ALL ISSUE TYPE EXAMPLES")
    logger.info("=" * 70)
    
    collection = strengthen_rag_database()
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ RAG DATABASE FULLY STRENGTHENED")
    logger.info("=" * 70)
    logger.info("\nIssue types now covered:")
    logger.info("  ✅ Passive voice (27 examples)")
    logger.info("  ✅ Long sentences (4 examples)")
    logger.info("  ✅ Vague terms (6 examples)")
    logger.info("  ✅ Missing prerequisites (3 examples)")
    logger.info("  ✅ Undefined acronyms (5 examples)")
    logger.info("  ✅ Inconsistent terminology (3 examples)")
    logger.info("  ✅ Mixed tense (3 examples)")
    logger.info("  ✅ Dense steps (2 examples)")
    logger.info("  ✅ Step order problems (3 examples)")
    logger.info("\nNext steps:")
    logger.info("1. Restart your Flask app")
    logger.info("2. Test AI suggestions for all issue types")
    logger.info("3. RAG will now provide relevant examples for any detected issue")
