# enhanced_rag/advanced_prompts.py
"""
Advanced prompt templates implementing structured prompting with style guide conditioning
and few-shot examples. Prevents hallucinations and ensures consistent outputs.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class StyleGuideRule:
    """Style guide rule for conditioning prompts."""
    rule_id: str
    category: str
    description: str
    examples: List[Tuple[str, str]]  # (before, after) pairs
    priority: str  # 'high', 'medium', 'low'


@dataclass
class PromptTemplate:
    """Structured prompt template with examples and constraints."""
    name: str
    system_prompt: str
    user_template: str
    examples: List[Dict[str, str]]
    constraints: List[str]
    output_format: str


class AdvancedPromptManager:
    """
    Advanced prompt manager implementing structured prompting with style guide conditioning.
    Includes few-shot examples and constraint enforcement.
    """
    
    def __init__(self, style_guide_path: Optional[str] = None):
        """
        Initialize advanced prompt manager.
        
        Args:
            style_guide_path: Path to style guide rules file
        """
        self.style_guide_rules = self._load_style_guide(style_guide_path)
        self.prompt_templates = self._initialize_templates()
        self.few_shot_examples = self._load_few_shot_examples()
        
        logger.info(f"✅ Advanced prompt manager initialized with {len(self.style_guide_rules)} style rules")
    
    def _load_style_guide(self, style_guide_path: Optional[str]) -> List[StyleGuideRule]:
        """Load style guide rules from file or use defaults."""
        # Default Siemens Technical Writing Guidelines
        default_rules = [
            StyleGuideRule(
                rule_id="passive_voice",
                category="voice",
                description="Use active voice for clarity and directness",
                examples=[
                    ("The file was created by the system.", "The system created the file."),
                    ("Errors are detected by the validator.", "The validator detects errors."),
                    ("The configuration can be changed by users.", "Users can change the configuration.")
                ],
                priority="high"
            ),
            StyleGuideRule(
                rule_id="conciseness",
                category="clarity",
                description="Use concise language and avoid unnecessary words",
                examples=[
                    ("In order to configure the system, you need to...", "To configure the system,..."),
                    ("It is important to note that...", "Note that..."),
                    ("Please be aware that you should...", "You should...")
                ],
                priority="high"
            ),
            StyleGuideRule(
                rule_id="imperative_mood",
                category="voice",
                description="Use imperative mood for instructions",
                examples=[
                    ("You should click the button.", "Click the button."),
                    ("The user needs to enter the password.", "Enter the password."),
                    ("It is necessary to save the file.", "Save the file.")
                ],
                priority="medium"
            ),
            StyleGuideRule(
                rule_id="specific_language",
                category="clarity",
                description="Use specific, precise language instead of vague terms",
                examples=[
                    ("The system performs some operations.", "The system validates user input and updates the database."),
                    ("Click on the appropriate button.", "Click the Save button."),
                    ("Configure the settings as needed.", "Configure the timeout to 30 seconds.")
                ],
                priority="high"
            ),
            StyleGuideRule(
                rule_id="parallel_structure",
                category="structure",
                description="Use parallel structure in lists and series",
                examples=[
                    ("Save, validate, and updating the file.", "Save, validate, and update the file."),
                    ("The system can create, edit, or deletion of files.", "The system can create, edit, or delete files."),
                    ("Configure settings, test the connection, and then deployment.", "Configure settings, test the connection, and then deploy.")
                ],
                priority="medium"
            )
        ]
        
        if style_guide_path:
            try:
                # Load from file if provided
                with open(style_guide_path, 'r', encoding='utf-8') as f:
                    loaded_rules = json.load(f)
                # Convert to StyleGuideRule objects
                # Implementation would parse the JSON structure
                return default_rules  # For now, return defaults
            except Exception as e:
                logger.warning(f"Failed to load style guide from {style_guide_path}: {e}")
                return default_rules
        
        return default_rules
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize structured prompt templates."""
        templates = {}
        
        # Style-aware rewriting template
        templates['style_rewrite'] = PromptTemplate(
            name="style_rewrite",
            system_prompt=self._build_style_system_prompt(),
            user_template="""Original sentence: "{sentence}"
Issue detected: {issue}
Context: {context}

Provide a rewrite that follows the style guidelines.""",
            examples=self._get_style_examples(),
            constraints=[
                "Must preserve the original meaning",
                "Must follow Siemens Technical Writing Guidelines",
                "Must be more concise than the original",
                "Must use active voice when possible"
            ],
            output_format="JSON with 'rewrite' and 'explanation' fields"
        )
        
        # Context-aware suggestion template
        templates['context_suggestion'] = PromptTemplate(
            name="context_suggestion",
            system_prompt=self._build_context_system_prompt(),
            user_template="""Sentence: "{sentence}"
Writing issue: {issue}
Document context: {document_context}
Retrieved guidance: {retrieved_context}

Provide a specific improvement suggestion.""",
            examples=self._get_context_examples(),
            constraints=[
                "Must reference the retrieved guidance",
                "Must be specific and actionable",
                "Must consider the document context",
                "Must not hallucinate information"
            ],
            output_format="JSON with 'suggestion', 'reasoning', and 'sources' fields"
        )
        
        # Technical accuracy template
        templates['technical_accuracy'] = PromptTemplate(
            name="technical_accuracy",
            system_prompt=self._build_technical_system_prompt(),
            user_template="""Technical sentence: "{sentence}"
Product: {product}
Issue: {issue}
Technical context: {technical_context}

Provide a technically accurate rewrite.""",
            examples=self._get_technical_examples(),
            constraints=[
                "Must maintain technical accuracy",
                "Must use correct technical terminology",
                "Must be appropriate for the target audience",
                "Must follow product-specific conventions"
            ],
            output_format="JSON with 'rewrite', 'technical_notes', and 'terminology' fields"
        )
        
        return templates
    
    def _build_style_system_prompt(self) -> str:
        """Build system prompt with style guide conditioning."""
        style_rules_text = "\n".join([
            f"- {rule.description}" for rule in self.style_guide_rules
            if rule.priority in ['high', 'medium']
        ])
        
        return f"""You are a technical writing assistant specializing in Siemens documentation.

STYLE GUIDELINES:
{style_rules_text}

INSTRUCTIONS:
1. Always preserve the original meaning and technical accuracy
2. Make the text more concise and clear
3. Use active voice whenever possible
4. Follow the style guidelines above
5. Provide specific, actionable improvements

OUTPUT FORMAT:
Always respond with valid JSON containing:
- "rewrite": The improved sentence
- "explanation": Brief explanation of changes made
- "style_rules_applied": List of style rules that were applied

Never hallucinate information or change technical facts."""
    
    def _build_context_system_prompt(self) -> str:
        """Build system prompt for context-aware suggestions."""
        return f"""You are a technical writing assistant that provides suggestions based on retrieved context.

CORE PRINCIPLES:
- Only use information from the provided context
- If context doesn't contain relevant guidance, state this clearly
- Provide specific, actionable suggestions
- Reference which part of the context supports your suggestion

STYLE GUIDELINES:
{self._get_condensed_style_rules()}

OUTPUT FORMAT:
Always respond with valid JSON containing:
- "suggestion": Specific improvement suggestion
- "reasoning": Why this improvement is needed
- "sources": Which retrieved context supports this suggestion
- "confidence": High/Medium/Low based on context quality

If the retrieved context doesn't contain relevant guidance, respond with:
{{"suggestion": "No specific guidance found", "reasoning": "Retrieved context doesn't address this issue", "sources": [], "confidence": "Low"}}"""
    
    def _build_technical_system_prompt(self) -> str:
        """Build system prompt for technical accuracy."""
        return f"""You are a technical writing assistant specializing in software documentation.

TECHNICAL ACCURACY REQUIREMENTS:
- Preserve all technical details and specifications
- Use correct technical terminology for the specific product
- Maintain accuracy of procedures and configurations
- Ensure compatibility with technical context

STYLE GUIDELINES:
{self._get_condensed_style_rules()}

OUTPUT FORMAT:
Always respond with valid JSON containing:
- "rewrite": Technically accurate improved sentence
- "technical_notes": Any technical considerations
- "terminology": Key technical terms used
- "accuracy_confidence": High/Medium/Low

Never change technical facts, procedures, or specifications."""
    
    def _get_condensed_style_rules(self) -> str:
        """Get condensed style rules for prompts."""
        return "\n".join([
            f"- {rule.description}" for rule in self.style_guide_rules[:5]
        ])
    
    def _load_few_shot_examples(self) -> Dict[str, List[Dict[str, str]]]:
        """Load few-shot examples for different prompt types."""
        return {
            'passive_voice': [
                {
                    "input": "The configuration file was updated by the administrator.",
                    "output": '{"rewrite": "The administrator updated the configuration file.", "explanation": "Changed from passive to active voice for clarity", "style_rules_applied": ["passive_voice"]}',
                    "context": "Technical documentation"
                },
                {
                    "input": "Errors are displayed by the system when validation fails.",
                    "output": '{"rewrite": "The system displays errors when validation fails.", "explanation": "Converted passive voice to active voice", "style_rules_applied": ["passive_voice"]}',
                    "context": "User interface documentation"
                }
            ],
            'conciseness': [
                {
                    "input": "In order to configure the application, it is necessary for you to access the settings menu.",
                    "output": '{"rewrite": "To configure the application, access the settings menu.", "explanation": "Removed unnecessary phrases for conciseness", "style_rules_applied": ["conciseness", "imperative_mood"]}',
                    "context": "User instructions"
                },
                {
                    "input": "Please be aware that you should make sure to save your work before proceeding.",
                    "output": '{"rewrite": "Save your work before proceeding.", "explanation": "Simplified wordy instruction to direct imperative", "style_rules_applied": ["conciseness", "imperative_mood"]}',
                    "context": "Procedure documentation"
                }
            ],
            'technical_accuracy': [
                {
                    "input": "The TCP/IP protocol is configured by accessing network settings.",
                    "output": '{"rewrite": "Configure the TCP/IP protocol through network settings.", "technical_notes": "Preserved TCP/IP protocol reference", "terminology": ["TCP/IP", "network settings"], "accuracy_confidence": "High"}',
                    "context": "Network configuration guide"
                }
            ]
        }
    
    def _get_style_examples(self) -> List[Dict[str, str]]:
        """Get examples for style rewriting."""
        examples = []
        for rule in self.style_guide_rules:
            for before, after in rule.examples[:2]:  # Limit to 2 examples per rule
                examples.append({
                    "input": before,
                    "output": f'{{"rewrite": "{after}", "explanation": "{rule.description}", "style_rules_applied": ["{rule.rule_id}"]}}',
                    "rule": rule.rule_id
                })
        return examples[:6]  # Limit total examples
    
    def _get_context_examples(self) -> List[Dict[str, str]]:
        """Get examples for context-aware suggestions."""
        return [
            {
                "input": 'Sentence: "Click on the save button." Issue: Use "click" instead of "click on"',
                "output": '{"suggestion": "Change \\"click on\\" to \\"click\\"", "reasoning": "More concise and direct", "sources": ["Style guide: Use concise language"], "confidence": "High"}',
                "context": "UI documentation"
            },
            {
                "input": 'Sentence: "The file was processed." Issue: Passive voice detected',
                "output": '{"suggestion": "Specify who or what processed the file", "reasoning": "Active voice is clearer and more direct", "sources": ["Style guide: Use active voice"], "confidence": "High"}',
                "context": "Technical procedures"
            }
        ]
    
    def _get_technical_examples(self) -> List[Dict[str, str]]:
        """Get examples for technical accuracy."""
        return [
            {
                "input": 'Technical sentence: "Configure the IP address." Product: "Network Router" Issue: Too vague',
                "output": '{"rewrite": "Configure the router IP address in the Network Settings panel.", "technical_notes": "Added specificity about where to configure", "terminology": ["IP address", "Network Settings"], "accuracy_confidence": "High"}',
                "context": "Network configuration"
            }
        ]
    
    def build_constrained_prompt(self,
                                sentence: str,
                                issue: str,
                                context: Dict[str, Any],
                                retrieved_chunks: List[Dict[str, Any]],
                                template_name: str = "style_rewrite") -> str:
        """
        Build a constrained prompt with style conditioning and examples.
        
        Args:
            sentence: The problematic sentence
            issue: Description of the writing issue
            context: Document context (product, type, etc.)
            retrieved_chunks: Retrieved context from RAG
            template_name: Which template to use
            
        Returns:
            Formatted prompt string
        """
        if template_name not in self.prompt_templates:
            template_name = "style_rewrite"
        
        template = self.prompt_templates[template_name]
        
        # Build context sections
        document_context = self._format_document_context(context)
        retrieved_context = self._format_retrieved_context(retrieved_chunks)
        
        # Select relevant examples
        relevant_examples = self._select_relevant_examples(issue, template_name)
        examples_text = self._format_examples(relevant_examples)
        
        # Build the full prompt
        system_prompt = template.system_prompt
        
        # Add examples to system prompt
        if examples_text:
            system_prompt += f"\n\nEXAMPLES:\n{examples_text}"
        
        # Add constraints
        constraints_text = "\n".join([f"- {constraint}" for constraint in template.constraints])
        system_prompt += f"\n\nCONSTRAINTS:\n{constraints_text}"
        
        # Format user message
        if template_name == "style_rewrite":
            user_message = template.user_template.format(
                sentence=sentence,
                issue=issue,
                context=document_context
            )
        elif template_name == "context_suggestion":
            user_message = template.user_template.format(
                sentence=sentence,
                issue=issue,
                document_context=document_context,
                retrieved_context=retrieved_context
            )
        elif template_name == "technical_accuracy":
            user_message = template.user_template.format(
                sentence=sentence,
                product=context.get('product', 'Unknown'),
                issue=issue,
                technical_context=retrieved_context
            )
        else:
            user_message = f"Sentence: {sentence}\nIssue: {issue}\nContext: {document_context}"
        
        # Combine into full prompt
        full_prompt = f"{system_prompt}\n\nUSER REQUEST:\n{user_message}"
        
        return full_prompt
    
    def _format_document_context(self, context: Dict[str, Any]) -> str:
        """Format document context for inclusion in prompts."""
        context_parts = []
        
        if context.get('product'):
            context_parts.append(f"Product: {context['product']}")
        
        if context.get('document_type'):
            context_parts.append(f"Document type: {context['document_type']}")
        
        if context.get('section'):
            context_parts.append(f"Section: {context['section']}")
        
        if context.get('audience'):
            context_parts.append(f"Audience: {context['audience']}")
        
        return "; ".join(context_parts) if context_parts else "General documentation"
    
    def _format_retrieved_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved context chunks for inclusion in prompts."""
        if not retrieved_chunks:
            return "No relevant context retrieved."
        
        context_sections = []
        for i, chunk in enumerate(retrieved_chunks[:3], 1):  # Limit to 3 chunks
            metadata = chunk.get('metadata', {})
            source_info = f"Source: {metadata.get('source_doc_id', 'unknown')}"
            
            context_sections.append(f"[{i}] {source_info}\n{chunk.get('text', '')[:200]}...")
        
        return "\n\n".join(context_sections)
    
    def _select_relevant_examples(self, issue: str, template_name: str) -> List[Dict[str, str]]:
        """Select most relevant examples based on the issue type."""
        issue_lower = issue.lower()
        
        # Map issue types to example categories
        if "passive voice" in issue_lower:
            return self.few_shot_examples.get('passive_voice', [])[:2]
        elif "concise" in issue_lower or "wordy" in issue_lower:
            return self.few_shot_examples.get('conciseness', [])[:2]
        elif "technical" in issue_lower:
            return self.few_shot_examples.get('technical_accuracy', [])[:2]
        else:
            # Return mixed examples
            all_examples = []
            for category, examples in self.few_shot_examples.items():
                all_examples.extend(examples[:1])  # 1 from each category
            return all_examples[:3]
    
    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """Format examples for inclusion in prompts."""
        if not examples:
            return ""
        
        formatted_examples = []
        for i, example in enumerate(examples, 1):
            formatted_examples.append(f"Example {i}:\nInput: {example['input']}\nOutput: {example['output']}")
        
        return "\n\n".join(formatted_examples)
    
    def validate_output_format(self, response: str, template_name: str) -> bool:
        """
        Validate that the LLM response follows the expected format.
        
        Args:
            response: LLM response text
            template_name: Template that was used
            
        Returns:
            True if format is valid
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            
            # Check required fields based on template
            if template_name == "style_rewrite":
                return all(key in parsed for key in ['rewrite', 'explanation'])
            elif template_name == "context_suggestion":
                return all(key in parsed for key in ['suggestion', 'reasoning', 'sources'])
            elif template_name == "technical_accuracy":
                return all(key in parsed for key in ['rewrite', 'technical_notes'])
            
            return True
            
        except json.JSONDecodeError:
            return False
    
    def get_style_guide_summary(self) -> str:
        """Get a summary of loaded style guide rules."""
        high_priority = [r for r in self.style_guide_rules if r.priority == 'high']
        return f"Loaded {len(self.style_guide_rules)} style rules ({len(high_priority)} high priority)"


# Global instance for easy access
_global_prompt_manager = None

def get_prompt_manager(style_guide_path: Optional[str] = None) -> AdvancedPromptManager:
    """
    Get global prompt manager instance.
    
    Args:
        style_guide_path: Path to style guide file
        
    Returns:
        Global prompt manager instance
    """
    global _global_prompt_manager
    
    if _global_prompt_manager is None:
        _global_prompt_manager = AdvancedPromptManager(style_guide_path)
    
    return _global_prompt_manager
