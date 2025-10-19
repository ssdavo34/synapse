"""
Prompt Templates for SynapseSimple v2.0

Template system with variable substitution for different agent types
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import setup_logger


class PromptTemplate:
    """Base prompt template with variable substitution"""

    def __init__(self, template: str):
        self.template = template
        self.logger = setup_logger(__name__)

    def format(self, **kwargs) -> str:
        """
        Format template with variables

        Args:
            **kwargs: Template variables

        Returns:
            Formatted prompt string
        """
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing required template variable: {e}")

    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render template with variables dict

        Args:
            variables: Dictionary of template variables

        Returns:
            Formatted prompt string
        """
        return self.format(**variables)


class SystemPrompt(PromptTemplate):
    """System role definition prompt"""

    DEFAULT_TEMPLATE = """You are a helpful AI assistant for educational purposes.

Role: {role}
Capabilities: {capabilities}
Guidelines:
{guidelines}

Current Date: {current_date}

Remember to:
- Be helpful and accurate
- Provide clear explanations
- Use evidence from provided context
- Admit when you don't know something
"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_default(
        role: str = "Educational AI Assistant",
        capabilities: str = "Answer questions, summarize documents, create quizzes",
        guidelines: str = "- Always be respectful\n- Provide accurate information\n- Cite sources when possible"
    ) -> str:
        """Create default system prompt with common values"""
        prompt = SystemPrompt()
        return prompt.format(
            role=role,
            capabilities=capabilities,
            guidelines=guidelines,
            current_date=datetime.now().strftime("%Y-%m-%d")
        )


class RAGPrompt(PromptTemplate):
    """RAG (Retrieval-Augmented Generation) prompt for document-based answers"""

    DEFAULT_TEMPLATE = """Answer the following question based on the provided context.

Context from documents:
{context}

Question: {query}

Instructions:
- Use ONLY information from the context above
- If the context doesn't contain enough information, say "I don't have enough information to answer this question based on the provided documents."
- Cite specific parts of the context when possible
- Be concise and accurate
- If multiple documents are referenced, synthesize information appropriately

Answer:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_with_context(
        query: str,
        context: str,
        max_length: Optional[int] = None
    ) -> str:
        """
        Create RAG prompt with query and context

        Args:
            query: User question
            context: Retrieved document context
            max_length: Maximum answer length (optional)

        Returns:
            Formatted RAG prompt
        """
        prompt = RAGPrompt()

        # Add length constraint if specified
        if max_length:
            template = prompt.template.replace(
                "Answer:",
                f"Answer (maximum {max_length} words):"
            )
            prompt = RAGPrompt(template)

        return prompt.format(query=query, context=context)


class ConversationPrompt(PromptTemplate):
    """General conversation prompt with history"""

    DEFAULT_TEMPLATE = """You are having a conversation with a user about their learning materials.

Conversation History:
{history}

Current Question: {query}

Instructions:
- Maintain context from the conversation history
- Be helpful and engaging
- If the user asks about documents, use the RAG system
- For general questions, provide thoughtful responses
- Keep answers concise unless detail is requested

Response:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_with_history(
        query: str,
        history: str,
        include_documents: bool = False
    ) -> str:
        """
        Create conversation prompt with history

        Args:
            query: Current user query
            history: Formatted conversation history
            include_documents: Whether to mention document context

        Returns:
            Formatted conversation prompt
        """
        prompt = ConversationPrompt()

        if include_documents:
            template = prompt.template.replace(
                "Instructions:",
                "Available Documents: Yes\n\nInstructions:"
            )
            prompt = ConversationPrompt(template)

        return prompt.format(query=query, history=history)


class SummaryPrompt(PromptTemplate):
    """Conversation summary prompt"""

    DEFAULT_TEMPLATE = """Summarize the following conversation in a concise way.

Conversation:
{conversation}

Summary Requirements:
- Capture main topics discussed
- Highlight key questions and answers
- Note any important decisions or conclusions
- Keep it brief ({max_sentences} sentences maximum)
- Use bullet points if appropriate

Summary:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_for_conversation(
        conversation: str,
        max_sentences: int = 5,
        focus: Optional[str] = None
    ) -> str:
        """
        Create summary prompt for conversation

        Args:
            conversation: Full conversation text
            max_sentences: Maximum sentences in summary
            focus: Optional focus area (e.g., "learning progress")

        Returns:
            Formatted summary prompt
        """
        prompt = SummaryPrompt()

        if focus:
            template = prompt.template.replace(
                "Summary Requirements:",
                f"Focus Area: {focus}\n\nSummary Requirements:"
            )
            prompt = SummaryPrompt(template)

        return prompt.format(
            conversation=conversation,
            max_sentences=max_sentences
        )


class QuizPrompt(PromptTemplate):
    """Quiz generation prompt"""

    DEFAULT_TEMPLATE = """Generate a quiz based on the following content.

Content:
{content}

Quiz Requirements:
- Number of questions: {num_questions}
- Question type: {question_type}
- Difficulty level: {difficulty}
- Include answer key

Format each question as:
Question N: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Correct Answer: [letter]

Generate the quiz:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_quiz(
        content: str,
        num_questions: int = 5,
        question_type: str = "multiple choice",
        difficulty: str = "medium"
    ) -> str:
        """
        Create quiz generation prompt

        Args:
            content: Source content for quiz
            num_questions: Number of questions to generate
            question_type: Type of questions
            difficulty: Difficulty level

        Returns:
            Formatted quiz prompt
        """
        prompt = QuizPrompt()
        return prompt.format(
            content=content,
            num_questions=num_questions,
            question_type=question_type,
            difficulty=difficulty
        )


class DiagnosisPrompt(PromptTemplate):
    """Learning diagnosis prompt"""

    DEFAULT_TEMPLATE = """Analyze the following quiz results to diagnose learning gaps.

Quiz Results:
{quiz_results}

Student Answers:
{student_answers}

Analysis Requirements:
- Identify weak areas
- Suggest topics to review
- Provide specific recommendations
- Rate overall understanding (1-10)

Diagnosis:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_diagnosis(
        quiz_results: str,
        student_answers: str
    ) -> str:
        """
        Create learning diagnosis prompt

        Args:
            quiz_results: Quiz questions and correct answers
            student_answers: Student's submitted answers

        Returns:
            Formatted diagnosis prompt
        """
        prompt = DiagnosisPrompt()
        return prompt.format(
            quiz_results=quiz_results,
            student_answers=student_answers
        )


class PlanningPrompt(PromptTemplate):
    """Learning plan generation prompt"""

    DEFAULT_TEMPLATE = """Create a personalized learning plan based on the diagnosis.

Diagnosis:
{diagnosis}

Available Resources:
{resources}

Plan Requirements:
- Duration: {duration}
- Focus on weak areas
- Include specific study materials
- Set measurable goals
- Provide timeline

Learning Plan:"""

    def __init__(self, template: Optional[str] = None):
        super().__init__(template or self.DEFAULT_TEMPLATE)

    @staticmethod
    def create_plan(
        diagnosis: str,
        resources: str,
        duration: str = "2 weeks"
    ) -> str:
        """
        Create learning plan prompt

        Args:
            diagnosis: Learning diagnosis results
            resources: Available learning resources
            duration: Plan duration

        Returns:
            Formatted planning prompt
        """
        prompt = PlanningPrompt()
        return prompt.format(
            diagnosis=diagnosis,
            resources=resources,
            duration=duration
        )


# Template registry for easy access
TEMPLATE_REGISTRY = {
    "system": SystemPrompt,
    "rag": RAGPrompt,
    "conversation": ConversationPrompt,
    "summary": SummaryPrompt,
    "quiz": QuizPrompt,
    "diagnosis": DiagnosisPrompt,
    "planning": PlanningPrompt
}


def get_template(template_type: str, custom_template: Optional[str] = None) -> PromptTemplate:
    """
    Get template by type

    Args:
        template_type: Type of template (system, rag, conversation, etc.)
        custom_template: Optional custom template string

    Returns:
        PromptTemplate instance

    Raises:
        ValueError: If template_type not found
    """
    if template_type not in TEMPLATE_REGISTRY:
        raise ValueError(
            f"Unknown template type: {template_type}. "
            f"Available: {list(TEMPLATE_REGISTRY.keys())}"
        )

    template_class = TEMPLATE_REGISTRY[template_type]
    return template_class(custom_template)
