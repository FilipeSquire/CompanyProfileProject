from typing import List, Dict, Optional, Tuple
import re
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from langfuse import observe, get_client
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

class CitationValidator:

    @staticmethod
    def extract_citations(text:str) -> List[int]:
        """
        Extract citation indices
        """

        return sorted(set(int(n) for n in re.findall(r"\[#?(\d+)\]", text)))
    
    @staticmethod
    def validate_citation_existence(citations: List[int], available_chunks: List[Dict]) -> Tuple[bool, List[int]]:
        """
        verify all citations map
        """

        chunk_indices = {chunk["i"] for chunk in available_chunks}
        missing = [c for c in citations if c not in chunk_indices]
        return len(missing) == 0, missing
    
    @staticmethod
    def extract_financial_values(text: str)-> List[str]:
        """
        Extract financial figures including £500 million format
        """

        patterns = [
            r'[£$€][\d,]+\.?\d*\s*(?:million|billion|thousand|m|bn|k)?',  # Currency: £100m, £500 million
            r'\d+\.?\d*%',  # Percentages: 45.2%
            r'\b[\d,]+\.?\d*\s+(?:million|billion|thousand)\b',  # Standalone: 100 million
        ]

        values = []

        for pattern in patterns:
            values.extend(re.findall(pattern, text, re.IGNORECASE))

        return values
    
    @staticmethod
    def verify_value_in_context(value: str, context: str, tolerance: float = 0.1) -> bool:
        """  
        Check if finance values are in the context
        """

        #Normalizing values
        normalized = value.replace(',','').replace(' ','').lower()
        normalized_context = context.replace(',','').replace(' ','').lower()

        if normalized in normalized_context:
            return True
        
        # extracts numeric value
        try:
            num_match = re.search(r'[\d.]+', value) #extract number from value
            if num_match:
                num = float(num_match.group())
                context_nums = re.findall(r'[\d.]+', context) #checks similar number exists
                for ctx_num in context_nums:
                    try:
                        ctx_val = float(ctx_num)
                        if abs(ctx_val - num) / max(num, ctx_val) < tolerance:
                            return True
                    except ValueError:
                        continue
        except (ValueError, ZeroDivisionError):
            pass

        return False
    

class RAGFaithfulnessEvaluator:
    """
    Evaluates faithfulness of RAG
    """

    def __init__(self, model: str = "gpt-4o", threshold: float = 0.7):

        """
        LLM judge
        """

        self.faithfulness_metric = FaithfulnessMetric(
            model=model,
            threshold=threshold,
            include_reason=True
        )
        self.citation_validator = CitationValidator()


    @traceable(run_type="chain", name="Evaluate RAG Faithfulness")
    @observe(as_type="evaluator", name="RAG Faithfulness Evaluation")
    async def evaluate_rag_answer(self, question: str, answer: str, retrieval_context: str, citations: List[int], all_chunks: List[Dict]) -> Dict:
        """
        RAG evaluator with LangSmith/LangFuse monitoring
        """

        logger.info(f"Evaluating RAG answer faithfulness...")

        #Test 1 - citation existence
        citations_valid, missing = self.citation_validator.validate_citation_existence(citations, all_chunks)

        #Test 2 - financial value verifier
        values = self.citation_validator.extract_financial_values(answer)
        values_verified = []
        values_missing = []

        for value in values:
            if self.citation_validator.verify_value_in_context(value, retrieval_context):
                values_verified.append(value)
            else:
                values_missing.append(value)

        value_faithfulness = len(values_verified) / len(values) if len(values) > 0 else 1.0

        #Test 3 - deepeval faithfulness
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=[retrieval_context]
        )

        try:
            self.faithfulness_metric.measure(test_case)
            deepeval_score = self.faithfulness_metric.score
            deepeval_reason = self.faithfulness_metric.reason
            deepeval_passed = self.faithfulness_metric.is_successful()
        except Exception as e:
            logger.error(f'DeepEval Metric failed: {e}')
            deepeval_score = 0.0
            deepeval_reason = f'Error: {str(e)}'
            deepeval_passed = False

        overall_passed = (
            citations_valid and value_faithfulness >= 0.8 and deepeval_passed
        )

        result = {
            "overall_passed": overall_passed,
            "citation_validation": {
                "all_valid": citations_valid,
                "total_citations": len(citations),
                "missing_citations": missing
            },
            "value_verification": {
                "total_values": len(values),
                "verified": values_verified,
                "missing": values_missing,
                "faithfulness_score": value_faithfulness
            },
            "deepeval_faithfulness": {
                "score": deepeval_score,
                "reason": deepeval_reason,
                "passed": deepeval_passed,
                "threshold": self.faithfulness_metric.threshold
            },
            "test_case": {
                "question": question,
                "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                "context_length": len(retrieval_context)
            }
        }

        # ============ SEND METRICS TO LANGFUSE/LANGSMITH ============
        # LangFuse
        try:
            langfuse = get_client()
            langfuse.update_current_trace(
                metadata={
                    "evaluation_type": "rag_faithfulness",
                    "overall_passed": overall_passed,
                    "deepeval_score": deepeval_score,
                    "citation_accuracy": citations_valid,
                    "value_accuracy": value_faithfulness,
                    "total_values": len(values),
                    "verified_values": len(values_verified),
                    "missing_values": len(values_missing)
                },
                tags=["evaluation", "faithfulness", "deepeval", "rag"]
            )
        except Exception as e:
            logger.warning(f"Failed to update LangFuse trace: {e}")

        # LangSmith
        try:
            from langsmith import run_helpers
            run_tree = run_helpers.get_current_run_tree()
            if run_tree:
                run_tree.add_metadata({
                    "evaluation": {
                        "type": "rag_faithfulness",
                        "overall_passed": overall_passed,
                        "deepeval_score": deepeval_score,
                        "deepeval_threshold": self.faithfulness_metric.threshold,
                        "deepeval_passed": deepeval_passed,
                        "deepeval_reason": deepeval_reason[:200] if deepeval_reason else None,
                        "citation_accuracy": citations_valid,
                        "total_citations": len(citations),
                        "missing_citations": missing,
                        "value_accuracy": value_faithfulness,
                        "total_values": len(values),
                        "verified_values": len(values_verified),
                        "missing_values": values_missing
                    }
                })
        except Exception as e:
            logger.warning(f"Failed to update LangSmith run tree: {e}")
        # ============================================================

        return result
    

class SynthesisFaithfulnessEvaluator:
    """  
    Evaluates the summaries 
    """

    def __init__(self, model: str = "gpt-4o", threshold: float = 0.7):
        self.faithfulness_metric = FaithfulnessMetric(
            model=model,
            threshold=threshold,
            include_reason=True
        )
        self.citation_validator = CitationValidator()


    @traceable(run_type="chain", name="Evaluate Synthesis Faithfulness")
    @observe(as_type="evaluator", name="Synthesis Faithfulness Evaluation")
    async def evaluate_synthesis(self, question: str, synthesized_answer: str, source_contexts: List[str], expected_citations: Optional[List[int]] = None) -> Dict:

        """
        Evaluates the synthesized answers with LangSmith/LangFuse monitoring
        """

        logger.info("Evaluating synthesis faithfulness...")

        # Combine all source contexts
        combined_context = "\n\n---\n\n".join(source_contexts)
        
        # Extract citations from synthesized answer
        actual_citations = self.citation_validator.extract_citations(synthesized_answer)
        
        # Test 1 - citation preservation
        if expected_citations:
            preserved = set(actual_citations) >= set(expected_citations)
            lost_citations = set(expected_citations) - set(actual_citations)
        else:
            preserved = True
            lost_citations = set()

        # Test 2 -  DeepEval Faithfulness
        test_case = LLMTestCase(
            input=question,
            actual_output=synthesized_answer,
            retrieval_context=[combined_context]
        )
        
        try:
            self.faithfulness_metric.measure(test_case)
            deepeval_score = self.faithfulness_metric.score
            deepeval_reason = self.faithfulness_metric.reason
            deepeval_passed = self.faithfulness_metric.is_successful()
        except Exception as e:
            logger.error(f"DeepEval metric failed: {e}")
            deepeval_score = 0.0
            deepeval_reason = f"Error: {str(e)}"
            deepeval_passed = False
        
        overall_passed = preserved and deepeval_passed

        result = {
            "overall_passed": overall_passed,
            "citation_preservation": {
                "preserved": preserved,
                "expected": expected_citations or [],
                "actual": actual_citations,
                "lost": list(lost_citations)
            },
            "deepeval_faithfulness": {
                "score": deepeval_score,
                "reason": deepeval_reason,
                "passed": deepeval_passed
            },
            "context_summary": {
                "num_sources": len(source_contexts),
                "total_context_length": len(combined_context)
            }
        }

        # ============ SEND METRICS TO LANGFUSE/LANGSMITH ============
        # LangFuse
        try:
            langfuse = get_client()
            langfuse.update_current_trace(
                metadata={
                    "evaluation_type": "synthesis_faithfulness",
                    "overall_passed": overall_passed,
                    "deepeval_score": deepeval_score,
                    "citations_preserved": preserved,
                    "num_sources": len(source_contexts),
                    "expected_citations": len(expected_citations) if expected_citations else 0,
                    "actual_citations": len(actual_citations),
                    "lost_citations": len(lost_citations)
                },
                tags=["evaluation", "faithfulness", "deepeval", "synthesis"]
            )
        except Exception as e:
            logger.warning(f"Failed to update LangFuse trace: {e}")

        # LangSmith
        try:
            from langsmith import run_helpers
            run_tree = run_helpers.get_current_run_tree()
            if run_tree:
                run_tree.add_metadata({
                    "evaluation": {
                        "type": "synthesis_faithfulness",
                        "overall_passed": overall_passed,
                        "deepeval_score": deepeval_score,
                        "deepeval_threshold": self.faithfulness_metric.threshold,
                        "deepeval_passed": deepeval_passed,
                        "deepeval_reason": deepeval_reason[:200] if deepeval_reason else None,
                        "citation_preservation": {
                            "preserved": preserved,
                            "expected_count": len(expected_citations) if expected_citations else 0,
                            "actual_count": len(actual_citations),
                            "expected": expected_citations or [],
                            "actual": actual_citations,
                            "lost": list(lost_citations)
                        },
                        "context_info": {
                            "num_sources": len(source_contexts),
                            "total_context_length": len(combined_context)
                        }
                    }
                })
        except Exception as e:
            logger.warning(f"Failed to update LangSmith run tree: {e}")
        # ============================================================

        return result