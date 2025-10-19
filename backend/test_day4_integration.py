"""
Day 4 Integration Test

Test Agent system and RAG pipeline integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from datetime import datetime

from agents.conversation_agent import ConversationAgent, Message
from agents.rag_pipeline import RAGPipeline
from services.chat_manager import ChatManager
from utils.response_formatter import ResponseFormatter
from prompts.templates import (
    SystemPrompt,
    RAGPrompt,
    ConversationPrompt,
    SummaryPrompt,
    get_template
)
from utils.logger import setup_logger


logger = setup_logger(__name__)


def test_prompt_templates():
    """Test prompt template system"""
    print("\n" + "="*80)
    print("TEST 1: Prompt Templates")
    print("="*80)

    try:
        # Test SystemPrompt
        print("\n[1-1] SystemPrompt")
        system_prompt = SystemPrompt.create_default(
            role="Educational Assistant",
            capabilities="Answer questions, summarize documents"
        )
        print(f"✅ SystemPrompt created: {len(system_prompt)} chars")
        print(f"Preview: {system_prompt[:100]}...")

        # Test RAGPrompt
        print("\n[1-2] RAGPrompt")
        rag_prompt = RAGPrompt.create_with_context(
            query="What is machine learning?",
            context="Machine learning is a subset of AI..."
        )
        print(f"✅ RAGPrompt created: {len(rag_prompt)} chars")

        # Test ConversationPrompt
        print("\n[1-3] ConversationPrompt")
        conv_prompt = ConversationPrompt.create_with_history(
            query="Tell me more",
            history="User: Hello\nAssistant: Hi there!"
        )
        print(f"✅ ConversationPrompt created: {len(conv_prompt)} chars")

        # Test SummaryPrompt
        print("\n[1-4] SummaryPrompt")
        summary_prompt = SummaryPrompt.create_for_conversation(
            conversation="User: Hi\nAssistant: Hello",
            max_sentences=3
        )
        print(f"✅ SummaryPrompt created: {len(summary_prompt)} chars")

        # Test template registry
        print("\n[1-5] Template Registry")
        template = get_template("rag")
        print(f"✅ Template retrieved: {type(template).__name__}")

        print("\n✅ All prompt template tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Prompt template test failed: {e}")
        logger.error(f"Prompt template test error: {e}", exc_info=True)
        return False


def test_conversation_agent():
    """Test ConversationAgent"""
    print("\n" + "="*80)
    print("TEST 2: ConversationAgent")
    print("="*80)

    try:
        # Create agent
        print("\n[2-1] Create ConversationAgent")
        agent = ConversationAgent(model="gpt-4o-mini", temperature=0.7)
        print(f"✅ Agent created: model={agent.model}")

        # Test message management
        print("\n[2-2] Message Management")
        msg = agent.add_message("user", "Hello, who are you?")
        print(f"✅ Message added: {msg.role} - {msg.content[:50]}")

        history = agent.format_history()
        print(f"✅ History formatted: {len(history)} chars")

        # Test conversation (simple, no API call for now)
        print("\n[2-3] Conversation Features")
        print(f"✅ Token estimate: {agent.get_token_estimate()} tokens")
        print(f"✅ Should summarize: {agent.should_summarize(token_threshold=100)}")

        summary = agent.get_conversation_summary()
        print(f"✅ Summary: {summary[:100]}...")

        # Test export/import
        print("\n[2-4] Export/Import")
        exported = agent.export_conversation()
        print(f"✅ Exported: {len(exported)} messages")

        agent.clear_history()
        print(f"✅ History cleared")

        agent.import_conversation(exported)
        print(f"✅ Imported: {len(agent.messages)} messages")

        print("\n✅ All ConversationAgent tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ ConversationAgent test failed: {e}")
        logger.error(f"ConversationAgent test error: {e}", exc_info=True)
        return False


def test_rag_pipeline():
    """Test RAG Pipeline (without actual search)"""
    print("\n" + "="*80)
    print("TEST 3: RAG Pipeline")
    print("="*80)

    try:
        # Create pipeline
        print("\n[3-1] Create RAG Pipeline")
        pipeline = RAGPipeline()
        print(f"✅ Pipeline created")
        print(f"   - Search limit: {pipeline.default_search_limit}")
        print(f"   - Score threshold: {pipeline.default_score_threshold}")
        print(f"   - Max context tokens: {pipeline.max_context_tokens}")

        # Test context building
        print("\n[3-2] Context Building")
        mock_search_results = {
            "success": True,
            "count": 2,
            "results": [
                {
                    "chunk": {
                        "id": 1,
                        "content": "Test content 1",
                        "chunk_index": 0
                    },
                    "document": {
                        "id": 1,
                        "title": "Test Document"
                    },
                    "score": 0.85
                }
            ],
            "has_context": False,
            "context": ""
        }

        context = pipeline.build_context(mock_search_results)
        print(f"✅ Context built: {len(context)} chars")

        # Test source extraction
        print("\n[3-3] Source Extraction")
        sources = pipeline.extract_sources(mock_search_results)
        print(f"✅ Sources extracted: {len(sources)} sources")
        if sources:
            print(f"   - First source: {sources[0]['document_title']}")

        # Test conversation methods
        print("\n[3-4] Conversation Methods")
        history = pipeline.get_conversation_history()
        print(f"✅ Conversation history: {len(history)} messages")

        summary = pipeline.get_conversation_summary()
        print(f"✅ Conversation summary: {summary[:80]}...")

        print("\n✅ All RAG Pipeline tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ RAG Pipeline test failed: {e}")
        logger.error(f"RAG Pipeline test error: {e}", exc_info=True)
        return False


def test_chat_manager():
    """Test Chat Manager"""
    print("\n" + "="*80)
    print("TEST 4: Chat Manager")
    print("="*80)

    try:
        # Create chat manager
        print("\n[4-1] Create Chat Manager")
        manager = ChatManager()
        print(f"✅ Chat Manager created")

        # Create user first
        print("\n[4-2] Create Test User")
        user = manager.db_service.create_user(
            email=f"test_day4_{datetime.now().timestamp()}@example.com",
            name="test_day4_user"
        )
        user_id = user.id
        print(f"✅ User created: user_id={user_id}")

        # Create chat
        print("\n[4-3] Create Chat Session")
        chat_result = manager.create_chat(
            user_id=user_id,
            title="Day 4 Test Chat"
        )
        print(f"✅ Chat created: chat_id={chat_result['chat_id']}")
        chat_id = chat_result['chat_id']

        # Get chat
        print("\n[4-4] Get Chat")
        chat = manager.get_chat(chat_id)
        print(f"✅ Chat retrieved: {chat.title}")

        # Get user chats
        print("\n[4-5] Get User Chats")
        chats = manager.get_user_chats(user_id)
        print(f"✅ User chats: {len(chats)} chats")

        # Update chat title
        print("\n[4-6] Update Chat Title")
        success = manager.update_chat_title(chat_id, "Updated Test Chat")
        print(f"✅ Title updated: {success}")

        # Format chat history
        print("\n[4-7] Format Chat History")
        history = manager.format_chat_history(chat_id)
        print(f"✅ History formatted: {len(history)} chars")

        # Export chat
        print("\n[4-8] Export Chat")
        exported = manager.export_chat(chat_id)
        print(f"✅ Chat exported: {exported['success']}")
        print(f"   - Messages: {len(exported['messages'])}")

        # Get statistics
        print("\n[4-9] Get Statistics")
        stats = manager.get_chat_statistics(chat_id)
        print(f"✅ Statistics:")
        print(f"   - Total messages: {stats['total_messages']}")
        print(f"   - User messages: {stats['user_messages']}")
        print(f"   - Assistant messages: {stats['assistant_messages']}")

        # Clean up
        print("\n[4-10] Cleanup")
        manager.delete_chat(chat_id)
        manager.db_service.delete_user(user_id)
        print(f"✅ Cleanup completed")

        print("\n✅ All Chat Manager tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Chat Manager test failed: {e}")
        logger.error(f"Chat Manager test error: {e}", exc_info=True)
        return False


def test_response_formatter():
    """Test Response Formatter"""
    print("\n" + "="*80)
    print("TEST 5: Response Formatter")
    print("="*80)

    try:
        # Create formatter
        print("\n[5-1] Create Response Formatter")
        formatter = ResponseFormatter()
        print(f"✅ Formatter created")

        # Test data
        content = "This is a test response from the AI."
        sources = [
            {
                "document_id": 1,
                "document_title": "Test Document",
                "chunk_id": 1,
                "chunk_index": 0,
                "score": 0.85,
                "content_preview": "This is a preview of the content"
            }
        ]
        metadata = {
            "usage": {
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50
            },
            "model": "gpt-4o-mini",
            "has_context": True
        }

        # Test text format
        print("\n[5-2] Format Text")
        text = formatter.format_text(content, include_sources=True, sources=sources, metadata=metadata)
        print(f"✅ Text formatted: {len(text)} chars")
        print(f"Preview:\n{text[:200]}...")

        # Test markdown format
        print("\n[5-3] Format Markdown")
        markdown = formatter.format_markdown(
            content,
            include_sources=True,
            sources=sources,
            metadata=metadata,
            title="Test Response"
        )
        print(f"✅ Markdown formatted: {len(markdown)} chars")

        # Test JSON format
        print("\n[5-4] Format JSON")
        json_str = formatter.format_json(content, sources=sources, metadata=metadata)
        print(f"✅ JSON formatted: {len(json_str)} chars")

        # Test chat message format
        print("\n[5-5] Format Chat Message")
        message = formatter.format_chat_message("user", "Hello!", datetime.now())
        print(f"✅ Message formatted: {message}")

        # Test chat history format
        print("\n[5-6] Format Chat History")
        messages = [
            {"role": "user", "content": "Hello", "created_at": datetime.now().isoformat()},
            {"role": "assistant", "content": "Hi there!", "created_at": datetime.now().isoformat()}
        ]
        history = formatter.format_chat_history(messages)
        print(f"✅ History formatted: {len(history)} chars")

        # Test RAG response format
        print("\n[5-7] Format RAG Response")
        rag_text = formatter.format_rag_response("Answer text", sources, format_type="text")
        print(f"✅ RAG (text) formatted: {len(rag_text)} chars")

        rag_md = formatter.format_rag_response("Answer text", sources, format_type="markdown")
        print(f"✅ RAG (markdown) formatted: {len(rag_md)} chars")

        rag_json = formatter.format_rag_response("Answer text", sources, format_type="json")
        print(f"✅ RAG (json) formatted: {len(rag_json)} chars")

        # Test error format
        print("\n[5-8] Format Error")
        error_text = formatter.format_error("Test error", format_type="text")
        print(f"✅ Error (text) formatted: {error_text}")

        error_json = formatter.format_error("Test error", format_type="json")
        print(f"✅ Error (json) formatted: {len(error_json)} chars")

        # Test summary format
        print("\n[5-9] Format Summary")
        stats = {"total_messages": 10, "total_tokens": 500}
        summary = formatter.format_summary("This is a summary", stats, format_type="text")
        print(f"✅ Summary formatted: {len(summary)} chars")

        print("\n✅ All Response Formatter tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Response Formatter test failed: {e}")
        logger.error(f"Response Formatter test error: {e}", exc_info=True)
        return False


def main():
    """Run all Day 4 integration tests"""
    print("\n" + "="*80)
    print("DAY 4 INTEGRATION TESTS - Agent System & RAG Pipeline")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Run all tests
    results['Prompt Templates'] = test_prompt_templates()
    results['ConversationAgent'] = test_conversation_agent()
    results['RAG Pipeline'] = test_rag_pipeline()
    results['Chat Manager'] = test_chat_manager()
    results['Response Formatter'] = test_response_formatter()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    if passed == total:
        print("\n🎉 All Day 4 integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
