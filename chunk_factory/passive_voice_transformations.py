"""
Passive Voice Transformation Examples for RAG Database

This file contains 100+ passive→active transformations to strengthen
the RAG fallback when deterministic patterns don't match.

ChromaDB will index these examples so when a passive voice sentence
doesn't match any deterministic pattern, RAG retrieves similar
transformations instead of random writing advice.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk
from typing import List


# Passive voice transformation examples (100+ pairs)
PASSIVE_TRANSFORMATIONS = [
    # === Reference/Documentation Patterns ===
    {
        "category": "reference_patterns",
        "examples": [
            {
                "passive": "The MQTT topic is as given in the below links.",
                "active": "See the below links for the MQTT topic.",
                "pattern": "is as given in"
            },
            {
                "passive": "An example for typical procedure is as follows:",
                "active": "An example for typical procedure:",
                "pattern": "is as follows"
            },
            {
                "passive": "The configuration details are as shown in the figure below.",
                "active": "See the figure below for the configuration details.",
                "pattern": "are as shown in"
            },
            {
                "passive": "The parameters are listed in Table 3.",
                "active": "Table 3 lists the parameters.",
                "pattern": "are listed in"
            },
            {
                "passive": "The settings are described in the configuration file.",
                "active": "The configuration file describes the settings.",
                "pattern": "are described in"
            },
            {
                "passive": "The error codes are defined in the appendix.",
                "active": "The appendix defines the error codes.",
                "pattern": "are defined in"
            },
            {
                "passive": "The steps are outlined in Section 4.",
                "active": "Section 4 outlines the steps.",
                "pattern": "are outlined in"
            },
            {
                "passive": "The requirements are specified in the documentation.",
                "active": "The documentation specifies the requirements.",
                "pattern": "are specified in"
            },
        ]
    },
    
    # === Modal Passives (must/can/should be done) ===
    {
        "category": "modal_passives",
        "examples": [
            {
                "passive": "The configuration must be done by the administrator.",
                "active": "The administrator must do the configuration.",
                "pattern": "must be done by"
            },
            {
                "passive": "The analysis must be performed by the client.",
                "active": "The client must perform the analysis.",
                "pattern": "must be performed by"
            },
            {
                "passive": "The validation can be executed by the system.",
                "active": "The system can execute the validation.",
                "pattern": "can be executed by"
            },
            {
                "passive": "The data should be verified by the user.",
                "active": "The user should verify the data.",
                "pattern": "should be verified by"
            },
            {
                "passive": "The file must be configured before startup.",
                "active": "Configure the file before startup.",
                "pattern": "must be configured"
            },
            {
                "passive": "The settings can be modified in the control panel.",
                "active": "Modify the settings in the control panel.",
                "pattern": "can be modified"
            },
            {
                "passive": "The parameter should be checked regularly.",
                "active": "Check the parameter regularly.",
                "pattern": "should be checked"
            },
        ]
    },
    
    # === Infinitive Passives (to be verb-ed) ===
    {
        "category": "infinitive_passives",
        "examples": [
            {
                "passive": "The client must provide data to be written to the device.",
                "active": "The client must provide data to write to the device.",
                "pattern": "to be written"
            },
            {
                "passive": "The file needs to be read from the server.",
                "active": "The file needs to read from the server.",
                "pattern": "to be read"
            },
            {
                "passive": "Messages to be sent to the broker must be formatted correctly.",
                "active": "Messages to send to the broker must be formatted correctly.",
                "pattern": "to be sent"
            },
            {
                "passive": "Parameters to be configured are listed below.",
                "active": "Parameters to configure are listed below.",
                "pattern": "to be configured"
            },
            {
                "passive": "Data to be processed arrives via MQTT.",
                "active": "Data to process arrives via MQTT.",
                "pattern": "to be processed"
            },
        ]
    },
    
    # === Display/Interface Patterns ===
    {
        "category": "display_patterns",
        "examples": [
            {
                "passive": "The tags are displayed in the monitoring interface.",
                "active": "The monitoring interface displays the tags.",
                "pattern": "are displayed in"
            },
            {
                "passive": "The results are shown on the dashboard.",
                "active": "The dashboard shows the results.",
                "pattern": "are shown on"
            },
            {
                "passive": "The details are displayed in the log file.",
                "active": "The log file displays the details.",
                "pattern": "are displayed in"
            },
            {
                "passive": "Error messages are presented to the user.",
                "active": "The system presents error messages to the user.",
                "pattern": "are presented to"
            },
            {
                "passive": "Status indicators are rendered in the UI.",
                "active": "The UI renders status indicators.",
                "pattern": "are rendered in"
            },
        ]
    },
    
    # === Provision/Supply Patterns ===
    {
        "category": "provision_patterns",
        "examples": [
            {
                "passive": "The data is provided by the PROFINET IO Connector.",
                "active": "The PROFINET IO Connector provides the data.",
                "pattern": "is provided by"
            },
            {
                "passive": "The services are supplied by the middleware.",
                "active": "The middleware supplies the services.",
                "pattern": "are supplied by"
            },
            {
                "passive": "The information is returned by the API.",
                "active": "The API returns the information.",
                "pattern": "is returned by"
            },
            {
                "passive": "The values are generated by the system.",
                "active": "The system generates the values.",
                "pattern": "are generated by"
            },
            {
                "passive": "The output is produced by the function.",
                "active": "The function produces the output.",
                "pattern": "is produced by"
            },
        ]
    },
    
    # === State/Status Changes ===
    {
        "category": "state_patterns",
        "examples": [
            {
                "passive": "The feature is enabled in the configuration.",
                "active": "The configuration enables the feature.",
                "pattern": "is enabled in"
            },
            {
                "passive": "The module is activated at startup.",
                "active": "The system activates the module at startup.",
                "pattern": "is activated"
            },
            {
                "passive": "The connection is initialized automatically.",
                "active": "The system initializes the connection automatically.",
                "pattern": "is initialized"
            },
            {
                "passive": "The service is started by the daemon.",
                "active": "The daemon starts the service.",
                "pattern": "is started by"
            },
            {
                "passive": "The process is stopped when errors occur.",
                "active": "The system stops the process when errors occur.",
                "pattern": "is stopped"
            },
        ]
    },
    
    # === Data Operations ===
    {
        "category": "data_operations",
        "examples": [
            {
                "passive": "The data is stored in the database.",
                "active": "The database stores the data.",
                "pattern": "is stored in"
            },
            {
                "passive": "The configuration is saved to a file.",
                "active": "The system saves the configuration to a file.",
                "pattern": "is saved to"
            },
            {
                "passive": "The parameters are loaded from the registry.",
                "active": "The registry loads the parameters.",
                "pattern": "are loaded from"
            },
            {
                "passive": "The values are read from the device.",
                "active": "The device reads the values.",
                "pattern": "are read from"
            },
            {
                "passive": "The bytes are written to memory.",
                "active": "The system writes the bytes to memory.",
                "pattern": "are written to"
            },
            {
                "passive": "The logs are transferred to the server.",
                "active": "The system transfers the logs to the server.",
                "pattern": "are transferred to"
            },
        ]
    },
    
    # === Past Tense Passives ===
    {
        "category": "past_tense",
        "examples": [
            {
                "passive": "The file was opened successfully.",
                "active": "The system opened the file successfully.",
                "pattern": "was opened"
            },
            {
                "passive": "The connection was established.",
                "active": "The system established the connection.",
                "pattern": "was established"
            },
            {
                "passive": "The data was sent to the broker.",
                "active": "The system sent the data to the broker.",
                "pattern": "was sent"
            },
            {
                "passive": "The request was received at 10:30.",
                "active": "The system received the request at 10:30.",
                "pattern": "was received"
            },
            {
                "passive": "The changes were applied automatically.",
                "active": "The system applied the changes automatically.",
                "pattern": "were applied"
            },
        ]
    },
    
    # === Technical Writing Specific ===
    {
        "category": "technical_writing",
        "examples": [
            {
                "passive": "The record data must be analyzed by the client application.",
                "active": "The client application must analyze the record data.",
                "pattern": "must be analyzed by"
            },
            {
                "passive": "The timestamps are removed to get better overview.",
                "active": "Remove the timestamps to get better overview.",
                "pattern": "are removed"
            },
            {
                "passive": "The raw data is provided by the connector.",
                "active": "The connector provides the raw data.",
                "pattern": "is provided by"
            },
            {
                "passive": "An array of bytes must be provided as input.",
                "active": "Provide an array of bytes as input.",
                "pattern": "must be provided"
            },
            {
                "passive": "The example is included below.",
                "active": "See the example below.",
                "pattern": "is included below"
            },
        ]
    },
]


def generate_passive_voice_chunks() -> List[DecisionChunk]:
    """
    Convert passive voice transformation examples into DecisionChunk objects
    for ChromaDB indexing.
    
    Returns:
        List of DecisionChunk objects
    """
    chunks = []
    chunk_id_counter = 1
    
    for category_group in PASSIVE_TRANSFORMATIONS:
        category = category_group["category"]
        
        for example in category_group["examples"]:
            passive = example["passive"]
            active = example["active"]
            pattern = example["pattern"]
            
            # Create Q&A chunk
            chunk = DecisionChunk(
                chunk_id=f"passive_transform_{chunk_id_counter}",
                question=f"How to convert this passive voice to active: '{passive}'",
                answer=f"Active voice: '{active}'. This uses the '{pattern}' pattern. The transformation removes passive construction while preserving meaning.",
                context={
                    "category": category,
                    "pattern": pattern,
                    "issue_type": "passive_voice",
                    "before": passive,
                    "after": active
                },
                source="passive_voice_transformations.py",
                confidence=0.95,
                tags=[category, "passive_voice", pattern, "transformation"]
            )
            chunks.append(chunk)
            chunk_id_counter += 1
            
            # Create pattern explanation chunk
            pattern_chunk = DecisionChunk(
                chunk_id=f"passive_pattern_{chunk_id_counter}",
                question=f"What is the '{pattern}' passive voice pattern?",
                answer=f"The '{pattern}' pattern appears in sentences like '{passive}'. Convert to active by identifying the actor and making them the subject: '{active}'.",
                context={
                    "category": category,
                    "pattern": pattern,
                    "issue_type": "passive_voice"
                },
                source="passive_voice_transformations.py",
                confidence=0.90,
                tags=[category, "passive_voice", pattern, "explanation"]
            )
            chunks.append(pattern_chunk)
            chunk_id_counter += 1
    
    return chunks


def get_passive_voice_chunks() -> List[DecisionChunk]:
    """Public API to get all passive voice transformation chunks."""
    return generate_passive_voice_chunks()


if __name__ == "__main__":
    # Generate and display chunks
    chunks = generate_passive_voice_chunks()
    print(f"Generated {len(chunks)} passive voice transformation chunks")
    
    # Show sample
    for chunk in chunks[:5]:
        print(f"\n{chunk.chunk_id}:")
        print(f"Q: {chunk.question}")
        print(f"A: {chunk.answer}")
