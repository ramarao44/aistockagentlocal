from src.reasoning.llm_reasoner import generate_llm_report

def test_llm():
    ticker = "AAPL"
    print(generate_llm_report(ticker, mode="local"))

if __name__ == "__main__":
    test_llm()
