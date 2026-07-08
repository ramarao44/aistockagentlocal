"""
Test script for DeepSeek API integration.
"""

from src.reasoning.llm_reasoner import run_deepseek, generate_llm_report

# Test 1: Direct DeepSeek call
print("\n=== Test 1: Direct DeepSeek Call ===")
result = run_deepseek("What is the stock market analysis for RELIANCE?")
print("Result:", result[:100] if len(result) > 100 else result)

# Test 2: Full report with DeepSeek
print("\n=== Test 2: Full Report with DeepSeek ===")
report = generate_llm_report("RELIANCE", mode="deepseek")
print("Report:", report[:200] if len(report) > 200 else report)