import requests
import os

# -----------------------------
# CONFIGURATION
# -----------------------------

#LOCAL_MODEL = "phi4"
LOCAL_MODEL = "llama3.2:3b"
#LOCAL_MODEL = "phi3.5-mini"
CLOUD_MODEL = "gpt-4o-mini"

# Correct endpoint for phi4
OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------
# LOCAL LLM (OLLAMA)
# -----------------------------

def run_local_llama(prompt: str) -> str:
    print("DEBUG: Using model:", LOCAL_MODEL)

    try:
        print("DEBUG: Sending request to Ollama...")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LOCAL_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        print("DEBUG: Ollama POST returned status:", response.status_code)

        data = response.json()
        print("DEBUG: Ollama response:", data)

        if "response" in data:
            return data["response"]

        if "output" in data:
            return data["output"]

        if "error" in data:
            return f"[Local LLM Error] {data['error']}"

        return str(data)

    except Exception as e:
        return f"[Local LLM Exception] {str(e)}"


# -----------------------------
# CLOUD LLM (OPENAI / AZURE)
# -----------------------------

def run_cloud_llm(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[Cloud LLM Error] Missing OPENAI_API_KEY"

    try:
        import openai
        openai.api_key = api_key

        completion = openai.ChatCompletion.create(
            model=CLOUD_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message["content"]

    except Exception as e:
        return f"[Cloud LLM Exception] {str(e)}"


# -----------------------------
# MAIN ENTRYPOINT
# -----------------------------

def generate_llm_report(ticker: str, mode: str = "local") -> str:
    print("DEBUG: generate_llm_report called with mode =", mode)

    prompt = (
        f"You are an AI financial analyst. Generate a structured, concise stock analysis "
        f"report for {ticker}. Include:\n"
        "- Price trend summary\n"
        "- Technical indicators\n"
        "- Market sentiment\n"
        "- Risks\n"
        "- Opportunities\n"
        "- Final recommendation\n"
        "- Next steps\n\n"
        "Keep the tone professional and analytical."
    )

    if mode == "cloud":
        print("DEBUG: Calling run_cloud_llm() now...")
        return run_cloud_llm(prompt)

    print("DEBUG: Calling run_local_llama() now...")
    result = run_local_llama(prompt)

    if result.startswith("[Local LLM Error]") or result.startswith("[Local LLM Exception]"):
        return f"{result}\n\nFalling back to cloud...\n\n" + run_cloud_llm(prompt)

    return result
