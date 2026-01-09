"""
Test async_profile_agent with faithfulness evaluation enabled
"""
import asyncio
import logging
from async_profile_agent import AsyncProfileAgent
from OldCode.prompts4 import system_mod, finance_calculations

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    # Test company
    company = "JAMES_DONALDSON_GROUP_LTD"
    
    # Create agent WITH EVALUATION ENABLED
    agent = AsyncProfileAgent(
        company_name=company,
        k=50,
        max_text_recall_size=35,
        max_chars=10000,
        model='gpt-5',
        profile_prompt=system_mod,
        finance_calculations=finance_calculations,
        enable_faithfulness_eval=True,  # 🔥 ENABLE EVALUATION
        faithfulness_threshold=0.7
    )
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing AsyncProfileAgent with Faithfulness Evaluation")
    print(f"{'='*60}\n")
    
    # Generate profile (this will now run evaluations!)
    # await agent.generate_company_profile()
    # Test just one section
    result = await agent._generate_section('GENERATE BUSINESS OVERVIEW')
    print(f"\n✅ Section completed!")
    print(f"Length: {len(result)} characters")

    
    # Export evaluation report
    report = agent.export_evaluation_report(
        output_path=f"evaluation_reports/{company}_faithfulness_report.json"
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 FAITHFULNESS EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"Company: {report['company_name']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"\nSummary:")
    print(f"  Total Tests: {report['summary']['total_tests']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Failed: {report['summary']['failed']}")
    print(f"  Pass Rate: {report['summary']['pass_rate']:.1%}")
    print(f"  Avg Faithfulness: {report['summary']['average_faithfulness_score']:.2f}")
    print(f"\nTest Breakdown:")
    print(f"  RAG Answer Tests: {report['test_breakdown']['rag_answer_tests']}")
    print(f"  Synthesis Tests: {report['test_breakdown']['synthesis_tests']}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
