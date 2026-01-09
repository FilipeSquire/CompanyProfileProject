"""
Test citation accuracy and validation
"""
import pytest
from tests.deepeval_evaluators import CitationValidator

class TestCitationValidator:
    """Test citation extraction and validation"""
    
    def test_extract_citations_basic(self):
        """Test basic citation extraction"""
        validator = CitationValidator()
        
        text = "Revenue was £100m [#1] and EBITDA was £25m [#2]."
        citations = validator.extract_citations(text)
        assert citations == [1, 2]
    
    def test_extract_citations_mixed_formats(self):
        """Test extraction with mixed citation formats"""
        validator = CitationValidator()
        
        text = "Data from [#1], [2], and [#5] shows growth."
        citations = validator.extract_citations(text)
        assert citations == [1, 2, 5]
    
    def test_extract_citations_no_citations(self):
        """Test text without citations"""
        validator = CitationValidator()
        
        text = "This text has no citations."
        citations = validator.extract_citations(text)
        assert citations == []
    
    def test_validate_citation_existence_all_valid(self):
        """Test when all citations are valid"""
        validator = CitationValidator()
        
        chunks = [
            {"i": 1, "text": "chunk 1"},
            {"i": 2, "text": "chunk 2"},
            {"i": 3, "text": "chunk 3"}
        ]
        
        all_valid, missing = validator.validate_citation_existence([1, 2], chunks)
        assert all_valid is True
        assert missing == []
    
    def test_validate_citation_existence_missing(self):
        """Test when citations are missing"""
        validator = CitationValidator()
        
        chunks = [
            {"i": 1, "text": "chunk 1"},
            {"i": 2, "text": "chunk 2"}
        ]
        
        all_valid, missing = validator.validate_citation_existence([1, 2, 5], chunks)
        assert all_valid is False
        assert missing == [5]
    
    def test_extract_financial_values_currency(self):
        """Test extracting currency values"""
        validator = CitationValidator()
        
        text = "Revenue was £150m and profit was $2.5M."
        values = validator.extract_financial_values(text)
        assert "£150m" in values
        assert "$2.5M" in values
    
    def test_extract_financial_values_percentages(self):
        """Test extracting percentage values"""
        validator = CitationValidator()
        
        text = "Margin improved to 25.5% from 20%."
        values = validator.extract_financial_values(text)
        assert "25.5%" in values
        assert "20%" in values
    
    def test_verify_value_in_context_exact_match(self):
        """Test exact value matching"""
        validator = CitationValidator()
        
        context = "The company reported revenue of £150m in 2024."
        assert validator.verify_value_in_context("£150m", context) is True
    
    def test_verify_value_in_context_formatting_difference(self):
        """Test matching with formatting differences"""
        validator = CitationValidator()

        context = "Revenue: £150,000,000"
        # The numeric matching logic should detect £150m ≈ £150,000,000
        # 150m = 150 million = 150,000,000
        assert validator.verify_value_in_context("£150m", context) is True
    
    def test_verify_value_not_in_context(self):
        """Test when value is not in context"""
        validator = CitationValidator()
        
        context = "The company reported revenue of £100m."
        assert validator.verify_value_in_context("£200m", context) is False
