"""
Pytest fixtures for DeepEval testing
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import async_profile_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from async_profile_agent import AsyncProfileAgent

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_search_hits():
    """Mock Azure Search results"""
    return [
        {
            "title": "Annual Report 2024",
            "chunk_id": "chunk_001",
            "chunk_text": "Revenue for 2024 was £150 million, up from £120 million in 2023. EBITDA margin improved to 25%.",
            "score": 0.95,
            "page_number": 15,
            "doc_type": "annual_report",
            "metadata_storage_path": "/reports/annual_2024.pdf"
        },
        {
            "title": "Financial Highlights Q4",
            "chunk_id": "chunk_002",
            "chunk_text": "Operating costs decreased by 10% year-over-year. Gross profit margin stands at 45%.",
            "score": 0.87,
            "page_number": 3,
            "doc_type": "quarterly_report",
            "metadata_storage_path": "/reports/q4_2024.pdf"
        }
    ]

@pytest.fixture
def mock_agent(mocker):
    """Mock AsyncProfileAgent with test configuration"""
    # Mock Azure Search client
    mock_search = mocker.AsyncMock()
    mock_search.search = AsyncMock(return_value=[])
    
    # Create agent with evaluation enabled
    agent = AsyncProfileAgent(
        company_name="Test Company Ltd",
        k=10,
        max_text_recall_size=800,
        max_chars=10000,
        model="gpt-4o",
        enable_faithfulness_eval=True,
        faithfulness_threshold=0.7
    )
    
    # Override search client with mock
    agent.search_client = mock_search
    
    return agent

@pytest.fixture
def sample_rag_result():
    """Sample RAG answer result with citations"""
    return {
        "answer": "The company's revenue for 2024 was £150 million [#1], representing growth from £120 million in the prior year [#1]. The EBITDA margin improved to 25% [#1], while operating costs decreased by 10% [#2].",
        "citations": [1, 2],
        "used_chunks": [
            {
                "i": 1,
                "title": "Annual Report 2024",
                "chunk_id": "chunk_001",
                "text": "Revenue for 2024 was £150 million, up from £120 million in 2023. EBITDA margin improved to 25%.",
                "score": 0.95
            },
            {
                "i": 2,
                "title": "Financial Highlights Q4",
                "chunk_id": "chunk_002",
                "text": "Operating costs decreased by 10% year-over-year.",
                "score": 0.87
            }
        ],
        "all_chunks": [
            {
                "i": 1,
                "title": "Annual Report 2024",
                "chunk_id": "chunk_001",
                "text": "Revenue for 2024 was £150 million, up from £120 million in 2023. EBITDA margin improved to 25%.",
                "score": 0.95
            },
            {
                "i": 2,
                "title": "Financial Highlights Q4",
                "chunk_id": "chunk_002",
                "text": "Operating costs decreased by 10% year-over-year.",
                "score": 0.87
            }
        ],
        "mode": "hybrid + semantic"
    }
