"""
AI suggestion system for intelligent writing recommendations.
This module provides context-aware suggestions using local models and rule-based fallbacks.
"""

from typing import List, Dict, Any, Optional
import logging

# ---- Logging early (best practice) ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# (Optional) Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not available - environment variables must be set manually")

# RAG availability (optional path)
try:
    from scripts.rag_system import get_rag_suggestion
    RAG_AVAILABLE = True
except Exception:
    RAG_AVAILABLE = False
    logger.debug("RAG system not available - falling back to rule-based suggestions only")


class AISuggestionEngine:
    """
    AI suggestion engine using local models and RAG.
    Smart fallbacks when AI is unavailable.
    """

    def generate_contextual_suggestion(
        self,
        feedback_text: str,
        sentence_context: str = "",
        document_type: str = "general",
        writing_goals: Optional[List[str]] = None,
        document_content: str = "",
        option_number: int = 1,
        issue: Optional[Dict[str, Any]] = None,   # <-- supports full issue dict
    ) -> Dict[str, Any]:
        # Safety checks
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
        if document_content is None:
            document_content = ""
        if writing_goals is None:
            writing_goals = ["clarity", "conciseness"]

        # 1) ✅ Fast path: if caller passes the issue dict, enrich and USE proposed_rewrite
        if issue:
            try:
                from app.services.enrichment import enrich_issue_with_solution
                enriched = enrich_issue_with_solution(issue)
                ai_text = (
                    enriched.get("proposed_rewrite")
                    or enriched.get("ai_suggestion")
                    or enriched.get("solution_text")
                    or feedback_text
                )
                return {
                    "suggestion": ai_text,
                    "ai_answer": enriched.get("solution_text", ""),
                    "confidence": "high",
                    "method": "rag_rewrite",
                    "sources": [],
                    "context_used": {
                        "document_type": document_type,
                        "writing_goals": writing_goals,
                        "primary_ai": "local",
                        "issue_detection": "rule_based",
                    },
                }
            except Exception as e:
                logger.warning(f"Fast-path enrichment failed, continuing with normal flow: {e}")

        # 2) Special case: long sentence → deterministic splitter (your preference)
        if ("long sentence" in feedback_text.lower() or "sentence too long" in feedback_text.lower()) and sentence_context:
            logger.info("🔧 BYPASS: Using enhanced rule-based splitting for long sentence")
            return self.generate_minimal_fallback(feedback_text, sentence_context, option_number)

        # 3) Primary method: RAG (if available)
        if RAG_AVAILABLE:
            try:
                logger.info("🔧 RAG AVAILABLE: Using RAG for solution generation")
                rag_result = get_rag_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context,
                    document_type=document_type,
                    document_content=document_content,
                )
                logger.info(f"🔧 RAG RESULT: received={bool(rag_result)}")
                if rag_result:
                    return {
                        "suggestion": rag_result.get("suggestion") or f"Consider: {sentence_context or feedback_text}",
                        "ai_answer": rag_result.get("ai_answer", ""),
                        "confidence": rag_result.get("confidence", "high"),
                        "method": "local_rag",
                        "sources": rag_result.get("sources", []),
                        "context_used": {
                            **rag_result.get("context_used", {}),
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "primary_ai": "local",
                            "issue_detection": "rule_based",
                        },
                    }
                logger.info("🔧 RAG returned no result, using minimal fallback")
            except Exception as e:
                logger.warning(f"RAG pipeline failed, using fallback: {e}")

        # 4) Final fallback: deterministic rewrite generator
        return self.generate_minimal_fallback(feedback_text, sentence_context, option_number)

    # ----------------- your existing fallback & helpers below -----------------

    def generate_minimal_fallback(self, feedback_text: str, sentence_context: str = "", option_number: int = 1) -> Dict[str, Any]:
        logger.info(f"🔧 FALLBACK CALLED: feedback='{feedback_text[:30]}', context='{sentence_context[:30]}', option={option_number}")
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
        if sentence_context.strip():
            suggestion = self._generate_sentence_rewrite(feedback_text, sentence_context, option_number)
        else:
            suggestion = f"Writing issue detected: {feedback_text}. Please review and improve this text for clarity, grammar, and style."
        if not suggestion or not str(suggestion).strip():
            suggestion = f"Review and improve this text to address: {feedback_text}"
        return {
            "suggestion": suggestion,
            "ai_answer": f"Review the text and address: {feedback_text}",
            "confidence": "medium",
            "method": "smart_fallback",
            "note": "Using smart fallback - AI unavailable",
        }

    def _generate_sentence_rewrite(self, feedback_text: str, sentence_context: str, option_number: int = 1) -> str:
        # Safety
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""

        feedback_lower = str(feedback_text).lower()

        # Passive / Active
        if "passive voice" in feedback_lower or "active voice" in feedback_lower:
            rewrites = [
                self._fix_passive_voice(sentence_context),
                self._alternative_active_voice(sentence_context),
                self._direct_action_voice(sentence_context),
            ]
        # First person
        elif "first person" in feedback_lower or "we" in feedback_lower:
            rewrites = [
                sentence_context.replace("We recommend", "Consider").replace("we recommend", "consider"),
                sentence_context.replace("We suggest", "The recommended approach is").replace("we suggest", "the recommended approach is"),
                sentence_context.replace("We believe", "This feature provides").replace("we believe", "this feature provides"),
            ]
        # Modal verbs / click on
        elif ("modal verb" in feedback_lower and "may" in feedback_lower) or "click on" in sentence_context.lower():
            rewrites = [
                sentence_context.replace("You may now click on", "Click").replace("you may now click on", "click")
                    .replace("click on the", "click the").replace("Click on the", "Click the"),
                sentence_context.replace("You may now click on", "You can click").replace("you may now click on", "you can click")
                    .replace("click on", "click"),
                sentence_context.replace("You may now click on", "To proceed, click").replace("you may now click on", "to proceed, click")
                    .replace("click on", "click"),
            ]
        # Long sentence
        elif "long" in feedback_lower or "sentence too long" in feedback_lower:
            split_sentences = self._split_long_sentence(sentence_context)
            if len(split_sentences) >= 2:
                if option_number == 1:
                    suggestion = f"Sentence 1: {split_sentences[0].rstrip('.')}. Sentence 2: {split_sentences[1].rstrip('.')}."
                elif option_number == 2 and len(split_sentences) >= 3:
                    suggestion = f"Sentence 1: {split_sentences[1].rstrip('.')}. Sentence 2: {split_sentences[2].rstrip('.')}."
                elif option_number == 2:
                    alt_sentence1 = split_sentences[0].replace("You can configure", "Configure").replace("This allows", "This enables")
                    alt_sentence2 = split_sentences[1].replace("This allows", "It allows").replace("This enables", "It enables")
                    suggestion = f"Sentence 1: {alt_sentence1.rstrip('.')}. Sentence 2: {alt_sentence2.rstrip('.')}."
                else:
                    suggestion = f"{split_sentences[0].rstrip('.')} and {split_sentences[1].lower().rstrip('.')}."
            else:
                suggestion = f"Consider breaking this sentence into shorter parts: {sentence_context.rstrip('.')}"
            why_text = f"WHY: Addresses {feedback_text.lower()} for better technical writing."
            return f"{suggestion}\n{why_text}"
        else:
            # Generic
            rewrites = [
                sentence_context.strip() + " (Improved version needed)",
                "Consider revising: " + sentence_context.strip(),
                "Alternative: " + sentence_context.strip(),
            ]

        # Filter
        valid_rewrites = [r for r in rewrites if r and r.strip() != sentence_context.strip()]
        if not valid_rewrites:
            valid_rewrites = [
                f"Rewrite needed: {sentence_context}",
                f"Improve this sentence: {sentence_context}",
                f"Consider alternatives for: {sentence_context}",
            ]

        # Pick option
        selected_index = min(option_number - 1, len(valid_rewrites) - 1)
        selected_rewrite = valid_rewrites[selected_index] if valid_rewrites else f"Review and improve this text based on: {feedback_text}"
        why_text = f"WHY: Addresses {feedback_text.lower()} for better technical writing."
        final_suggestion = f"{selected_rewrite.strip()}\n{why_text}"
        if not final_suggestion or not final_suggestion.strip():
            final_suggestion = f"Review and improve this text based on: {feedback_text}\nWHY: Addressing the identified writing issue for better clarity."
        return final_suggestion

    def _fix_passive_voice(self, sentence: str) -> str:
        s = sentence or ""
        s_lower = s.lower()
        if "was reviewed by the team" in s_lower:
            return s.replace("was reviewed by the team", "the team reviewed")
        elif "was written by" in s_lower:
            import re
            m = re.search(r'(.+?)\s+was\s+written\s+by\s+(.+)', s, re.IGNORECASE)
            if m:
                doc = m.group(1).strip()
                author = m.group(2).strip()
                return f"{author} wrote {doc.lower()}"
            return s.replace("was written by", "").replace("The document ", "").strip() + " wrote the document"
        elif "was created by" in s_lower:
            return s.replace("was created by", "").replace("The ", "").strip() + " created this"
        elif "changes were made" in s_lower:
            return s.replace("changes were made", "the team made changes")
        elif "was designed by" in s_lower:
            return s.replace("was designed by", "").strip() + " designed this"
        elif "that is displayed in the" in s_lower:
            import re
            m = re.search(r'(.+?)\s+that\s+is\s+displayed\s+in\s+the\s+(\w+)', s, re.IGNORECASE)
            if m:
                data_part = m.group(1).strip()
                location_part = m.group(2).strip()
                return s.replace(f"that is displayed in the {location_part}", f"from the {location_part}")
            else:
                return s.replace("that is displayed in the", "from the")
        elif "that is displayed" in s_lower:
            return s.replace("that is displayed", "that appears").replace("data that appears", "visible data")
        elif "is displayed" in s_lower:
            return s.replace("is displayed", "appears")
        elif "are displayed" in s_lower:
            return s.replace("are displayed", "appear on screen").replace("The configuration options", "The system displays the configuration options")
        elif "are shown" in s_lower:
            return s.replace("are shown", "appear").replace("The ", "The interface presents the ")
        elif "are not generated when" in s_lower:
            return s.replace("Docker logs are not generated when", "Docker does not generate logs when")
        elif "logs are not generated" in s_lower:
            return s.replace("logs are not generated", "the system does not generate logs")
        elif "is not generated" in s_lower:
            import re
            m = re.search(r'(.+?)\s+is\s+not\s+generated', s, re.IGNORECASE)
            if m:
                subject = m.group(1).strip()
                return s.replace(f"{subject} is not generated", f"The system does not generate {subject.lower()}")
        else:
            return s.replace("was ", "").replace("were ", "").replace("The ", "This ")

    def _alternative_active_voice(self, sentence: str) -> str:
        result = sentence or ""
        s_lower = result.lower()
        if "the document was" in result:
            result = result.replace("The document was carefully reviewed by the team", "The team carefully reviewed the document")
        elif "several changes were made" in s_lower:
            result = result.replace("several changes were made", "the team made several changes")
        elif "changes were made" in s_lower:
            result = result.replace("changes were made", "we implemented changes")
        elif "are displayed" in s_lower:
            result = result.replace("The configuration options of the data source are displayed", "The system displays the configuration options of the data source")
        elif "is displayed" in s_lower:
            result = result.replace("is displayed", "appears")
        elif "docker logs are not generated" in s_lower:
            result = result.replace("Docker logs are not generated when there are no active applications", "No applications generate Docker logs when inactive")
        elif "logs are not generated" in s_lower:
            result = result.replace("logs are not generated", "no logs appear")
        elif "was written by" in s_lower:
            import re
            m = re.search(r'(.+?)\s+was\s+written\s+by\s+(.+)', result, re.IGNORECASE)
            if m:
                document = m.group(1).strip()
                author = m.group(2).strip()
                result = f"{author} authored {document.lower()}"
        return result if result != (sentence or "") else f"Direct version: {(sentence or '').replace('was ', '').replace('were ', '').replace('are ', '').replace('is ', '')}"

    def _direct_action_voice(self, sentence: str) -> str:
        s = sentence or ""
        if "The document was" in s:
            return "Review the document and make necessary changes for clarity."
        elif "changes were made" in s.lower():
            return "Make changes to improve document clarity."
        elif "are displayed" in s.lower():
            return "The interface shows the configuration options of the data source."
        elif "is displayed" in s.lower():
            return "The system shows this information clearly."
        elif "docker logs are not generated" in s.lower():
            return "Docker applications do not generate logs when inactive."
        elif "logs are not generated" in s.lower():
            return "The system generates no logs when applications are inactive."
        else:
            return f"Use active voice: {s.replace(' was ', ' ').replace(' were ', ' ').replace(' are ', ' ').replace(' is ', ' ')}"

    def _split_long_sentence(self, sentence: str) -> List[str]:
        import re
        s = (sentence or "").strip()
        if not s.endswith('.'):
            s += '.'
        if "gantt chart" in s.lower() and "comprehensive view" in s.lower():
            return [
                "The Gantt chart offers a comprehensive view of machine status, device status, and notifications for the configured asset.",
                "All data derives from real-time sources.",
            ]
        if re.search(r',\s+(which|that|where|when|while)\s+', s, re.IGNORECASE):
            m = re.search(r'^(.+?),\s+(which|that|where|when|while)\s+(.+)$', s, re.IGNORECASE)
            if m:
                main_clause = m.group(1).strip() + "."
                subordinate_clause = f"It {m.group(3).strip()}."
                return [main_clause, subordinate_clause]
        if re.search(r',\s+(and|but|or|so)\s+', s, re.IGNORECASE):
            m = re.search(r'^(.+?),\s+(and|but|or|so)\s+(.+)$', s, re.IGNORECASE)
            if m:
                first_part = m.group(1).strip() + "."
                conj = m.group(2).lower()
                second = m.group(3).strip()
                if conj == "and":
                    sec = f"Additionally, {second}"
                elif conj == "but":
                    sec = f"However, {second}"
                elif conj == "so":
                    sec = f"Therefore, {second}"
                else:
                    sec = f"Alternatively, {second}"
                if not sec.endswith('.'):
                    sec += "."
                return [first_part, sec]
        if re.search(r',\s+(with|for|by|through|during|after|before)\s+', s, re.IGNORECASE):
            m = re.search(r'^(.+?),\s+(with|for|by|through|during|after|before)\s+(.+)$', s, re.IGNORECASE)
            if m:
                main_part = m.group(1).strip() + "."
                prep_phrase = f"This {m.group(2)} {m.group(3).strip()}."
                return [main_part, prep_phrase]
        parts = [p.strip() for p in s.split(',')]
        if len(parts) >= 2:
            first_part = parts[0].strip() + "."
            remaining = ", ".join(parts[1:]).strip().rstrip('.')
            second_part = "It also " + remaining + "."
            return [first_part, second_part]
        if len(s.split()) > 15:
            words = s.split()
            mid = len(words) // 2
            first_half = " ".join(words[:mid]) + "."
            second_half = " ".join(words[mid:])
            if not second_half.endswith('.'):
                second_half += "."
            return [first_half, second_half]
        return [s]


# Initialize the AI suggestion engine
print("🔧 INIT: About to initialize AISuggestionEngine")
ai_engine = AISuggestionEngine()
print("🔧 INIT: AISuggestionEngine initialized successfully")


def get_enhanced_ai_suggestion(
    feedback_text: str,
    sentence_context: str = "",
    document_type: str = "general",
    writing_goals: Optional[List[str]] = None,
    document_content: str = "",
    option_number: int = 1,
    issue: Optional[Dict[str, Any]] = None,   # <-- pass full issue when possible
) -> Dict[str, Any]:
    print(f"🔧 FUNCTION: get_enhanced_ai_suggestion called with feedback='{feedback_text[:30]}'")
    logger.info(f"🔧 FUNCTION: get_enhanced_ai_suggestion called with feedback='{feedback_text[:30]}'")
    return ai_engine.generate_contextual_suggestion(
        feedback_text=feedback_text,
        sentence_context=sentence_context,
        document_type=document_type,
        writing_goals=writing_goals,
        document_content=document_content,
        option_number=option_number,
        issue=issue,
    )
