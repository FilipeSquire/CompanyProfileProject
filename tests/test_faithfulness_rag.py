"""
Integration tests for RAG answer faithfulness
"""
import pytest
from tests.deepeval_evaluators import RAGFaithfulnessEvaluator

class TestRAGFaithfulnesss:
    """Test faithfulness of RAG-generated answers"""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        return RAGFaithfulnessEvaluator(model="gpt-4o", threshold=0.7)
    
    @pytest.mark.asyncio
    async def test_faithful_answer(self, evaluator):
        """Test answer that is faithful to context"""
        question = "What was the company's revenue in 2024?"
        answer = "The company's revenue in 2024 was £150 million [#1]."
        context = "[1] Annual Report 2024\nRevenue for 2024 was £150 million."
        citations = [1]
        chunks = [{"i": 1, "text": "Revenue for 2024 was £150 million."}]
        
        result = await evaluator.evaluate_rag_answer(
            question=question,
            answer=answer,
            retrieval_context=context,
            citations=citations,
            all_chunks=chunks
        )
        
        assert result["overall_passed"] is True
        assert result["citation_validation"]["all_valid"] is True
        assert result["value_verification"]["faithfulness_score"] >= 0.8
        assert result["deepeval_faithfulness"]["passed"] is True
    
    @pytest.mark.asyncio
    async def test_hallucinated_value(self, evaluator):
        """Test answer with hallucinated financial value"""
        question = "What was the company's revenue?"
        answer = "The company's revenue was £500 million [#1]."  # Wrong value!
        context = "[1] Annual Report\nRevenue for 2024 was £150 million."
        citations = [1]
        chunks = [{"i": 1, "text": "Revenue for 2024 was £150 million."}]
        
        result = await evaluator.evaluate_rag_answer(
            question=question,
            answer=answer,
            retrieval_context=context,
            citations=citations,
            all_chunks=chunks
        )
        
        # Should fail because £500m is not in context
        assert result["value_verification"]["faithfulness_score"] < 0.8
        assert "£500 million" in result["value_verification"]["missing"]
    
    @pytest.mark.asyncio
    async def test_missing_citation(self, evaluator):
        """Test answer with missing citation"""
        question = "What was the revenue?"
        answer = "Revenue was £150m [#5]."  # Citation #5 doesn't exist
        context = "[1] Revenue was £150m."
        citations = [5]
        chunks = [{"i": 1, "text": "Revenue was £150m."}]
        
        result = await evaluator.evaluate_rag_answer(
            question=question,
            answer=answer,
            retrieval_context=context,
            citations=citations,
            all_chunks=chunks
        )
        
        assert result["overall_passed"] is False
        assert result["citation_validation"]["all_valid"] is False
        assert 5 in result["citation_validation"]["missing_citations"]
    
    @pytest.mark.asyncio
    async def test_multiple_values_mixed_faithfulness(self, evaluator):
        """Test answer with mix of correct and incorrect values"""
        question = "What are the key financial metrics?"
        answer = "Revenue was £150m [#1] and EBITDA was £999m [#1]."  # £999m is wrong
        context = "[1] Revenue was £150m. EBITDA was £25m."
        citations = [1]
        chunks = [{"i": 1, "text": "Revenue was £150m. EBITDA was £25m."}]
        
        result = await evaluator.evaluate_rag_answer(
            question=question,
            answer=answer,
            retrieval_context=context,
            citations=citations,
            all_chunks=chunks
        )
        
        # Should have partial faithfulness
        assert result["value_verification"]["total_values"] == 2
        assert len(result["value_verification"]["verified"]) == 1
        assert result["value_verification"]["faithfulness_score"] == 0.5
