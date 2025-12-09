"""
Section-Level Context Preservation Test
Tests semantic safety across structured multi-sentence blocks.
"""

import sys
from app.semantic_context import build_document_context, can_be_rewritten, change_alters_meaning
from app.document_first_ai import DocumentFirstAIEngine
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Test sections: product manuals, release notes, troubleshooting, onboarding
TEST_SECTIONS = {
    "product_manual_1": """
The PLC connects to the HMI through Ethernet. 
Configure the IP address in the system settings menu.
Navigate to Settings > Network > IP Configuration.
Enter the static IP address provided by your network administrator.
Click Apply to save the changes.
The system will restart automatically after applying network settings.
Wait for the green LED indicator before proceeding.
Once the LED is solid green, the connection is established.
Open the HMI interface to verify connectivity.
The main dashboard should display real-time sensor data.
If no data appears, check the cable connections first.
Then verify that the PLC firmware version matches the HMI requirements.
The minimum supported firmware is version 2.4.0 or higher.
Older versions may cause communication errors or data loss.
Contact technical support if issues persist after firmware verification.
""",
    
    "product_manual_2": """
The safety interlock prevents operation when guards are open.
Before starting the machine, ensure all protective covers are closed.
Check that the emergency stop button is released and not engaged.
The control panel displays a red indicator when interlocks are active.
Press the Reset button to clear any previous fault conditions.
After reset, the indicator should turn yellow, showing standby mode.
Select the operating mode using the rotary selector switch.
Auto mode enables fully automated operation without manual intervention.
Manual mode requires operator confirmation for each cycle step.
Semi-auto mode combines automated sequences with manual override capability.
Once mode is selected, press the green Start button.
The machine will begin its initialization sequence automatically.
During initialization, motors will perform self-calibration movements.
Do not enter the machine area while the yellow strobe light is flashing.
Wait until the strobe stops and the system beeps three times.
""",

    "release_note": """
Version 3.2.0 introduces enhanced diagnostic capabilities and performance improvements.
The new diagnostic module automatically logs error codes to the system database.
Users can now export diagnostic reports in PDF or CSV format.
Report generation typically completes within 10 seconds for standard datasets.
Large datasets exceeding 10,000 records may require additional processing time.
The dashboard UI has been redesigned for improved accessibility.
Navigation menus now support keyboard shortcuts for power users.
Press Ctrl+D to access diagnostics, Ctrl+R for reports, and Ctrl+S for settings.
The previous version required mouse-only interaction for these functions.
Performance benchmarks show 40% faster query response times compared to version 3.1.5.
Memory usage has been reduced by 25% through optimized data caching.
The installer now supports silent deployment for enterprise environments.
Use the /silent flag when running the installer from command line.
All user settings from version 3.x are automatically migrated during upgrade.
No manual configuration is required after installation completes.
""",

    "troubleshooting": """
The system fails to start when power supply voltage drops below specification.
Check the input voltage using a multimeter at the power terminal block.
Nominal voltage should be 24V DC with tolerance of +/- 10%.
If voltage is outside this range, inspect the power supply unit.
Look for blown fuses in the main distribution panel first.
Then check circuit breaker status in the control cabinet.
A tripped breaker indicates an overcurrent condition occurred.
Reset the breaker only after identifying the root cause of the trip.
Common causes include short circuits, ground faults, or motor overload.
Disconnect peripheral devices and reset the breaker to isolate the fault.
If the breaker trips immediately after reset, the main controller may be damaged.
Measure resistance between power terminals and ground using a megohmmeter.
Resistance should exceed 1 megohm for proper insulation integrity.
Values below this threshold indicate insulation breakdown or moisture ingress.
Contact certified service personnel for component-level diagnostics and repair.
""",

    "onboarding": """
Welcome to the TechDoc System quick-start guide.
This guide will help you complete your first document review in under 10 minutes.
First, log in to the web portal using your assigned credentials.
Your username was sent to your registered email address during account creation.
If you did not receive the email, check your spam folder first.
Then contact the system administrator to resend the credentials.
After successful login, you will see the main dashboard interface.
The left sidebar contains navigation links for all major functions.
Click Upload Document to begin your first review session.
The system accepts PDF, DOCX, and TXT file formats only.
Maximum file size is 50 MB per upload for optimal processing speed.
After upload completes, the document appears in the review queue automatically.
Select the document from the queue to open the review interface.
The interface displays the document text with AI-suggested improvements highlighted.
Accept suggestions by clicking the green checkmark icon next to each item.
""",

    "product_manual_3": """
The CNC controller uses the G-code programming language for machine operations.
G00 commands execute rapid positioning moves at maximum traverse rate.
G01 commands perform linear interpolation cuts at programmed feed rate.
Feed rate is specified using the F parameter in millimeters per minute.
For example, G01 X100 Y50 F500 moves to X=100, Y=50 at 500 mm/min.
The spindle speed is controlled independently using the S parameter.
S1200 sets the spindle to rotate at 1200 revolutions per minute.
M03 activates clockwise spindle rotation before cutting operations begin.
M05 stops the spindle after machining operations are complete.
Tool changes are performed automatically using the M06 command sequence.
The system pauses operation during tool change to ensure safety.
After the tool change completes, the program resumes from the next line.
Always verify tool offset values before running a new program.
Incorrect offsets can cause collisions between the tool and workpiece.
Use the MDI mode to manually test positioning before automatic operation.
"""
}


class SectionValidator:
    def __init__(self):
        self.ai_engine = DocumentFirstAIEngine()
        self.total_sentences = 0
        self.rewrite_attempts = 0
        self.approved_rewrites = 0
        self.blocked_eligibility = 0
        self.blocked_justification = 0
        self.blocked_meaning = 0
        self.false_rewrites = 0
        self.false_blocks = 0
        
        # Justification tracking
        self.justification_histogram = {
            "pronoun_ambiguity": 0,
            "acronym_first_use": 0,
            "ui_duplication": 0,
            "sequence_fuzz": 0,
            "safety_deviation": 0,
            "vague_quantifier": 0,
            "passive_referent_unclear": 0,
            "grammar_tense_error": 0,
            "(no_justification)": 0
        }
    
    def validate_section(self, section_name, text):
        """Validate a single section."""
        # Parse document
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        
        # Build semantic context
        sections = [{"title": section_name, "content": text, "start_index": 0}]
        context = build_document_context(sentences, sections, nlp)
        
        print(f"\n{'='*60}")
        print(f"Section: {section_name}")
        print(f"Sentences: {len(sentences)}")
        print(f"{'='*60}")
        
        for idx, sentence in enumerate(sentences):
            self.total_sentences += 1
            
            # Simulate realistic issue type detection (what atomic rules would find)
            # In real system, these come from atomic_rules.py violation detection
            detected_issue = None
            sentence_lower = sentence.lower()
            
            # Detect passive voice
            if ' is ' in sentence_lower or ' are ' in sentence_lower or ' was ' in sentence_lower or ' were ' in sentence_lower:
                if ' by ' not in sentence_lower:  # Passive without "by" phrase
                    detected_issue = "Passive voice"
            
            # Detect vague terms
            if any(term in sentence_lower for term in [' some ', ' various ', ' several ', ' many ']):
                detected_issue = "Vague terms"
            
            # Try rewrite - gates are checked inside _fallback_suggestion
            self.rewrite_attempts += 1
            original = sentence
            result = self.ai_engine._fallback_suggestion(
                detected_issue or "grammar check",  # feedback_text
                sentence,  # sentence_context
                issue_type=detected_issue,  # Use detected issue or None
                sentence_index=idx,
                document_context=context
            )
            
            # Extract suggestion and method from result dict
            suggestion = result.get("suggestion", sentence) if isinstance(result, dict) else sentence
            method = result.get("method", "") if isinstance(result, dict) else ""
            justification = result.get("justification", "") if isinstance(result, dict) else ""
            
            # Check which gate blocked (if any)
            if method == "eligibility_gate_block":
                self.blocked_eligibility += 1
                self.rewrite_attempts -= 1  # Don't count as rewrite attempt
                print(f"[{idx+1}] BLOCKED (eligibility): {sentence[:60]}...")
                continue
            
            if method == "justification_gate_block":
                self.blocked_justification += 1
                self.rewrite_attempts -= 1  # Don't count as rewrite attempt
                print(f"[{idx+1}] BLOCKED (justification: {justification}): {sentence[:60]}...")
                continue
            
            # If we reach here, rewrite was attempted
            # Track justification for approved rewrites
            if suggestion != original:
                # Rewrite happened - must have justification
                if justification:
                    if justification in self.justification_histogram:
                        self.justification_histogram[justification] += 1
                    else:
                        # Unknown justification - track as violation
                        self.justification_histogram["(no_justification)"] += 1
                        print(f"[{idx+1}] ⚠️ REWRITE WITHOUT JUSTIFICATION: {sentence[:60]}...")
                else:
                    # No justification provided - VIOLATION
                    self.justification_histogram["(no_justification)"] += 1
                    print(f"[{idx+1}] ⚠️ REWRITE WITHOUT JUSTIFICATION: {sentence[:60]}...")
            
            if suggestion == original:
                # LLM returned unchanged
                print(f"[{idx+1}] UNCHANGED (LLM): {sentence[:60]}...")
                continue
            
            # Check meaning preservation
            meaning_preserved = not change_alters_meaning(original, suggestion, context)
            
            if meaning_preserved:
                self.approved_rewrites += 1
                print(f"[{idx+1}] APPROVED: {original[:50]}... → {suggestion[:50]}...")
            else:
                self.blocked_meaning += 1
                print(f"[{idx+1}] BLOCKED (meaning): {original[:50]}...")
                print(f"     Rejected suggestion: {suggestion[:50]}...")
                
                # This is a false rewrite if LLM broke meaning
                self.false_rewrites += 1
    
    def print_results(self):
        """Print final metrics."""
        print(f"\n{'='*60}")
        print("Section Results:")
        print(f"Total: {self.total_sentences}")
        print(f"Rewrites: {self.rewrite_attempts}")
        print(f"Approved: {self.approved_rewrites}")
        print(f"Blocked (eligibility): {self.blocked_eligibility}")
        print(f"Blocked (justification): {self.blocked_justification}")
        print(f"Blocked (meaning): {self.blocked_meaning}")
        print(f"False rewrites: {self.false_rewrites}")
        print(f"False blocks: {self.false_blocks}")
        print(f"{'='*60}")
        
        # Calculate percentages
        if self.total_sentences > 0:
            rewrite_pct = (self.rewrite_attempts / self.total_sentences) * 100
            approved_pct = (self.approved_rewrites / self.total_sentences) * 100
            print(f"\nRewrite rate: {rewrite_pct:.1f}%")
            print(f"Approval rate: {approved_pct:.1f}%")
        
        # Print justification histogram
        print(f"\n{'='*60}")
        print("Triggers:")
        for trigger, count in self.justification_histogram.items():
            if count > 0 or trigger == "(no_justification)":
                print(f"{trigger}: {count}")


def main():
    validator = SectionValidator()
    
    # Run validation on all sections
    for section_name, text in TEST_SECTIONS.items():
        validator.validate_section(section_name, text)
    
    # Print final results
    validator.print_results()


if __name__ == "__main__":
    main()
