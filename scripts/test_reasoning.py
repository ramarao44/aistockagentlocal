from src.reasoning.reasoning_node import generate_combined_report

def test_reasoning():
    ticker = "AAPL"
    report = generate_combined_report(ticker)
    print(report)

if __name__ == "__main__":
    test_reasoning()
