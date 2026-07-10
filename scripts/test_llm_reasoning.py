import os
import subprocess
import sys
import time
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.reasoning import llm_reasoner

MOCK_MARKET_DATA = {
    "success": True,
    "ticker": "RELIANCE.NS",
    "exchange": "NSE",
    "current_price": 2920.5,
    "rsi": 58.2,
    "ma50": 2860.1,
    "ma200": 2712.9,
    "bollinger_upper": 2998.4,
    "bollinger_lower": 2808.6,
    "last_updated": "2026-07-10",
}


def test_local_standard_mode():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.main_reasoning", return_value="Standard summary"
    ), patch("src.reasoning.llm_reasoner.fast_reasoning", return_value="Bullish"), patch(
        "src.reasoning.llm_reasoner.logic_reasoning", return_value="Trend logic"
    ):
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="local")
        assert "AI Stock Report (Standard)" in report
        assert "Standard summary" in report
        assert "Bullish" in report


def test_optimized_mode_uses_fast_path_for_summary():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.fast_reasoning", return_value="Compact output"
    ) as fast_mock, patch("src.reasoning.llm_reasoner.logic_reasoning", return_value="Compact logic"):
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="optimized")
        assert "AI Stock Report (Optimized)" in report
        assert "Compact output" in report
        assert fast_mock.call_count >= 2


def test_local_failure_falls_back_to_cloud():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch(
        "src.reasoning.llm_reasoner.main_reasoning", return_value="[Local LLM Error] model unavailable"
    ), patch("src.reasoning.llm_reasoner.run_cloud_llm", return_value="Cloud fallback report") as cloud_mock:
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="local")
        assert "Cloud fallback report" in report
        assert cloud_mock.called


def test_cloud_mode_missing_key_error():
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), patch.dict(
        "os.environ", {"OPENAI_API_KEY": ""}, clear=False
    ):
        # Temporarily remove OPENAI_API_KEY
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="cloud")
            assert "Missing OPENAI_API_KEY" in report
        finally:
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key


# ============================================================================
# Robust Server Connectivity Tests
# ============================================================================

def check_ollama_server_available():
    """Verify Ollama server/CLI is available and responsive."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print(f"WARN: Ollama CLI returned non-zero: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        print("SKIP: Ollama CLI not installed")
        return None
    except subprocess.TimeoutExpired:
        print("FAIL: Ollama CLI timed out - server may be unresponsive")
        return False
    except Exception as e:
        print(f"FAIL: Ollama check error: {e}")
        return False


def check_required_models_installed():
    """Verify all required models are available locally."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return False
        
        installed = [line.split()[0] for line in result.stdout.strip().split('\n')[1:] if line.strip()]
        required_models = ["qwen2.5:3b", "llama3.2:3b", "phi3:3.8b"]
        
        missing = [m for m in required_models if m not in installed]
        if missing:
            print(f"WARN: Missing models: {missing}")
            return False
        return True
    except Exception:
        return False


def test_llm_error_response_format():
    """Test that LLM errors are properly formatted and caught."""
    test_data = {
        "ticker": "TEST.NS",
        "exchange": "NSE",
        "current_price": 100,
        "rsi": 50,
        "ma50": 100,
        "ma200": 100,
        "bollinger_upper": 105,
        "bollinger_lower": 95,
        "last_updated": "2026-07-10",
    }
    
    # Test error response format detection
    error_text = "[Local LLM Error] model=qwen2.5:3b detail=connection refused"
    assert llm_reasoner._is_error_response(error_text) is True
    
    # Test successful response format detection
    success_text = "This is a valid response"
    assert llm_reasoner._is_error_response(success_text) is False


def test_llm_timeout_handling():
    """Test that LLM timeouts are handled gracefully."""
    with patch("src.reasoning.llm_reasoner.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ollama", timeout=120)
        
        result = llm_reasoner.run_model("qwen2.5:3b", "test prompt")
        assert "timed out" in result.lower()
        assert "[Local LLM Error]" in result


def test_llm_file_not_found_handling():
    """Test that missing ollama CLI is handled gracefully."""
    with patch("src.reasoning.llm_reasoner.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("ollama not found")
        
        result = llm_reasoner.run_model("qwen2.5:3b", "test prompt")
        assert "command not found" in result.lower() or "not found" in result.lower()


def test_llm_subprocess_error_handling():
    """Test that subprocess errors are properly formatted."""
    with patch("src.reasoning.llm_reasoner.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ollama", "run", "qwen2.5:3b"],
            returncode=1,
            stdout="",
            stderr="connection refused"
        )
        
        result = llm_reasoner.run_model("qwen2.5:3b", "test prompt")
        assert "[Local LLM Error]" in result
        assert "connection refused" in result


def test_empty_output_handling():
    """Test that empty LLM output is handled gracefully."""
    with patch("src.reasoning.llm_reasoner.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ollama", "run", "qwen2.5:3b"],
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = llm_reasoner.run_model("qwen2.5:3b", "test prompt")
        assert "[Local LLM Error]" in result or "empty" in result.lower()


def test_subprocess_timeout_value():
    """Verify subprocess timeout is configured correctly (120 seconds)."""
    with patch("src.reasoning.llm_reasoner.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ollama", "run", "qwen2.5:3b"],
            returncode=0,
            stdout="test output",
            stderr=""
        )
        
        prompt = "test prompt"
        llm_reasoner.run_model("qwen2.5:3b", prompt)
        
        # Verify timeout parameter is passed
        call_kwargs = mock_run.call_args[1]
        assert "timeout" in call_kwargs, "Timeout not configured in subprocess.run"
        assert call_kwargs["timeout"] == 120, f"Expected timeout=120, got {call_kwargs['timeout']}"


def test_report_generation_timing():
    """Test that report generation completes within reasonable time bounds."""
    start_time = time.time()
    
    with patch("src.reasoning.llm_reasoner.fetch_indian_stock_data", return_value=MOCK_MARKET_DATA), \
         patch("src.reasoning.llm_reasoner.main_reasoning", return_value="Summary"), \
         patch("src.reasoning.llm_reasoner.fast_reasoning", return_value="Sentiment"), \
         patch("src.reasoning.llm_reasoner.logic_reasoning", return_value="Logic"):
        
        report = llm_reasoner.generate_llm_report("RELIANCE.NS", mode="local")
        elapsed = time.time() - start_time
        
        # Should complete quickly with mocked calls
        assert elapsed < 5.0, f"Report generation took {elapsed}s, should be < 5s with mocks"
        assert "Summary" in report


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Health checks (informational)
    print("=== LLM Subsystem Health Checks ===")
    
    ollama_status = check_ollama_server_available()
    if ollama_status is None:
        print("- [SKIP] Ollama server check (not installed)")
    elif ollama_status:
        print("- [PASS] Ollama server is available")
    else:
        print("- [FAIL] Ollama server is not available")
    
    model_status = check_required_models_installed()
    if model_status:
        print("- [PASS] All required models installed")
    else:
        print("- [WARN] Some models missing")
    
    print("\n=== Unit Tests ===")
    
    # Core tests
    test_local_standard_mode()
    print("- [PASS] test_local_standard_mode")
    
    test_optimized_mode_uses_fast_path_for_summary()
    print("- [PASS] test_optimized_mode_uses_fast_path_for_summary")
    
    test_local_failure_falls_back_to_cloud()
    print("- [PASS] test_local_failure_falls_back_to_cloud")
    
    test_cloud_mode_missing_key_error()
    print("- [PASS] test_cloud_mode_missing_key_error")
    
    # Robust tests
    test_llm_error_response_format()
    print("- [PASS] test_llm_error_response_format")
    
    test_llm_timeout_handling()
    print("- [PASS] test_llm_timeout_handling")
    
    test_llm_file_not_found_handling()
    print("- [PASS] test_llm_file_not_found_handling")
    
    test_llm_subprocess_error_handling()
    print("- [PASS] test_llm_subprocess_error_handling")
    
    test_empty_output_handling()
    print("- [PASS] test_empty_output_handling")
    
    test_subprocess_timeout_value()
    print("- [PASS] test_subprocess_timeout_value")
    
    test_report_generation_timing()
    print("- [PASS] test_report_generation_timing")
    
    print("\ntest_llm_reasoning.py: all tests passed")