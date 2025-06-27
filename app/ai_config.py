"""
Configuration file for AI suggestion system.
Allows customization of models, parameters, and behavior.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"

@dataclass
class ModelConfig:
    """Configuration for AI model settings."""
    provider: ModelProvider
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 400
    top_p: float = 0.85
    repeat_penalty: float = 1.1
    timeout: int = 30

@dataclass
class SuggestionConfig:
    """Configuration for suggestion behavior."""
    min_confidence_threshold: float = 0.7
    max_suggestions_per_issue: int = 3
    include_alternatives: bool = True
    include_explanations: bool = True
    personalize_to_user: bool = False

class AIConfigurationManager:
    """Manages AI configuration and model selection."""
    
    def __init__(self):
        self.default_models = {
            ModelProvider.OLLAMA: [
                ModelConfig(ModelProvider.OLLAMA, "mistral-7b-instruct", 0.2, 400),
                ModelConfig(ModelProvider.OLLAMA, "llama3.1", 0.15, 350),
                ModelConfig(ModelProvider.OLLAMA, "codellama", 0.1, 300),  # For technical docs
            ],
            ModelProvider.OPENAI: [
                ModelConfig(ModelProvider.OPENAI, "gpt-4", 0.2, 400),
                ModelConfig(ModelProvider.OPENAI, "gpt-3.5-turbo", 0.3, 350),
            ],
            ModelProvider.ANTHROPIC: [
                ModelConfig(ModelProvider.ANTHROPIC, "claude-3-haiku", 0.2, 400),
                ModelConfig(ModelProvider.ANTHROPIC, "claude-3-sonnet", 0.15, 500),
            ]
        }
        
        self.document_specific_models = {
            "technical": ModelConfig(ModelProvider.OLLAMA, "codellama", 0.1, 350),
            "academic": ModelConfig(ModelProvider.OLLAMA, "mistral-7b-instruct", 0.15, 450),
            "business": ModelConfig(ModelProvider.OLLAMA, "mistral-7b-instruct", 0.2, 300),
            "creative": ModelConfig(ModelProvider.OLLAMA, "llama3.1", 0.4, 500),
            "general": ModelConfig(ModelProvider.OLLAMA, "mistral-7b-instruct", 0.2, 400),
        }
        
        self.suggestion_config = SuggestionConfig()
        
    def get_model_config(self, document_type: str = "general", 
                        provider_preference: Optional[ModelProvider] = None) -> ModelConfig:
        """Get the best model configuration for a document type."""
        
        # Check for document-specific model first
        if document_type in self.document_specific_models:
            return self.document_specific_models[document_type]
        
        # Fall back to provider preference or default
        preferred_provider = provider_preference or ModelProvider.OLLAMA
        
        if preferred_provider in self.default_models:
            return self.default_models[preferred_provider][0]
        
        # Ultimate fallback
        return self.default_models[ModelProvider.OLLAMA][0]
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider."""
        available = {}
        for provider, configs in self.default_models.items():
            available[provider.value] = [config.model_name for config in configs]
        return available
    
    def update_model_config(self, document_type: str, config: ModelConfig):
        """Update model configuration for a specific document type."""
        self.document_specific_models[document_type] = config
    
    def get_suggestion_config(self) -> SuggestionConfig:
        """Get current suggestion configuration."""
        return self.suggestion_config
    
    def update_suggestion_config(self, **kwargs):
        """Update suggestion configuration."""
        for key, value in kwargs.items():
            if hasattr(self.suggestion_config, key):
                setattr(self.suggestion_config, key, value)

# Global configuration instance
config_manager = AIConfigurationManager()

# Domain-specific writing guidelines
DOMAIN_GUIDELINES = {
    "technical": {
        "priorities": ["accuracy", "clarity", "completeness"],
        "avoid": ["ambiguity", "jargon without explanation", "overly casual tone"],
        "encourage": ["step-by-step instructions", "examples", "clear definitions"],
        "tone": "professional and helpful",
        "typical_issues": ["passive voice in instructions", "undefined acronyms", "missing context"]
    },
    
    "academic": {
        "priorities": ["precision", "evidence", "formal tone"],
        "avoid": ["informal language", "unsupported claims", "bias"],
        "encourage": ["citations", "clear arguments", "objective language"],
        "tone": "formal and scholarly",
        "typical_issues": ["weak thesis statements", "poor transitions", "informal tone"]
    },
    
    "business": {
        "priorities": ["professionalism", "conciseness", "action-oriented"],
        "avoid": ["jargon", "unnecessary complexity", "vague language"],
        "encourage": ["clear action items", "specific deadlines", "measurable goals"],
        "tone": "professional and direct",
        "typical_issues": ["too much jargon", "unclear calls to action", "overly long sentences"]
    },
    
    "marketing": {
        "priorities": ["engagement", "persuasion", "brand consistency"],
        "avoid": ["passive voice", "weak calls to action", "boring language"],
        "encourage": ["active voice", "compelling benefits", "emotional connection"],
        "tone": "engaging and persuasive",
        "typical_issues": ["weak headlines", "feature-focused vs benefit-focused", "unclear value propositions"]
    },
    
    "creative": {
        "priorities": ["voice", "flow", "engagement"],
        "avoid": ["repetitive structure", "clichés", "telling instead of showing"],
        "encourage": ["vivid imagery", "varied sentence structure", "strong voice"],
        "tone": "expressive and engaging",
        "typical_issues": ["flat characters", "weak dialogue", "telling instead of showing"]
    }
}

def get_domain_guidelines(document_type: str) -> Dict[str, Any]:
    """Get writing guidelines for a specific domain."""
    return DOMAIN_GUIDELINES.get(document_type, DOMAIN_GUIDELINES.get("general", {}))

# Performance monitoring configuration
PERFORMANCE_CONFIG = {
    "track_response_times": True,
    "track_user_satisfaction": True,
    "log_failed_suggestions": True,
    "collect_feedback": True,
    "improvement_suggestions": True
}

# Feature flags for experimental features
FEATURE_FLAGS = {
    "use_advanced_prompts": True,
    "enable_context_awareness": True,
    "provide_alternatives": True,
    "explain_suggestions": True,
    "personalize_responses": False,  # Future feature
    "multi_model_comparison": False,  # Future feature
    "real_time_learning": False  # Future feature
}

def get_feature_flag(flag_name: str) -> bool:
    """Check if a feature flag is enabled."""
    return FEATURE_FLAGS.get(flag_name, False)

def enable_feature(flag_name: str):
    """Enable a feature flag."""
    if flag_name in FEATURE_FLAGS:
        FEATURE_FLAGS[flag_name] = True

def disable_feature(flag_name: str):
    """Disable a feature flag."""
    if flag_name in FEATURE_FLAGS:
        FEATURE_FLAGS[flag_name] = False
