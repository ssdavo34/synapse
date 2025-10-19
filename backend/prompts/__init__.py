"""
Prompt Templates Package

Centralized prompt management for SynapseSimple v2.0 agents
"""

from prompts.templates import (
    PromptTemplate,
    SystemPrompt,
    RAGPrompt,
    ConversationPrompt,
    SummaryPrompt,
    QuizPrompt,
    DiagnosisPrompt,
    PlanningPrompt,
    TEMPLATE_REGISTRY,
    get_template
)

__all__ = [
    "PromptTemplate",
    "SystemPrompt",
    "RAGPrompt",
    "ConversationPrompt",
    "SummaryPrompt",
    "QuizPrompt",
    "DiagnosisPrompt",
    "PlanningPrompt",
    "TEMPLATE_REGISTRY",
    "get_template"
]
