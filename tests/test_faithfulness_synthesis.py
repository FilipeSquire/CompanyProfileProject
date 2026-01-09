"""
Tests for synthesis faithfulness evaluation
"""
import pytest
from tests.deepeval_evaluators import SynthesisFaithfulnessEvaluator

class TestSynthesisFaithfulness:
    """Test faithfulness of synthesized answers"""
    
    @pytest.fixture
    def evaluator(self):
        return SynthesisFaithfulnessEvaluator(model="gpt-4o", threshold=0.7)
    
    @pytest.mark.asyncio
    async def test_faithful_synthesis(self, evaluator):
        """Test synthesis that preserves source information"""
        question = "Summarize the financial performance"
        synthesized = "Revenue was £150m [#1] and margins improved to 25% [#2]."
        sources = [
            "Revenue for the year was £150 million.",
            "Operating margins improved to 25%."
        ]
        expected_citations = [1, 2]
        
        result = await evaluator.evaluate_synthesis(
            question=question,
            synthesized_answer=synthesized,
            source_contexts=sources,
            expected_citations=expected_citations
        )
        
        assert result["overall_passed"] is True
        assert result["citation_preservation"]["preserved"] is True
        assert result["deepeval_faithfulness"]["passed"] is True
    
    @pytest.mark.asyncio
    async def test_lost_citations(self, evaluator):
        """Test synthesis that loses citations"""
        question = "Summarize"
        synthesized = "Revenue was £150m."  # Lost citation!
        sources = ["Revenue was £150m [#1]."]
        expected_citations = [1]
        
        result = await evaluator.evaluate_synthesis(
            question=question,
            synthesized_answer=synthesized,
            source_contexts=sources,
            expected_citations=expected_citations
        )
        
        assert result["citation_preservation"]["preserved"] is False
        assert 1 in result["citation_preservation"]["lost"]
