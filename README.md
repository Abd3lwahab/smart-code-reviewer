# Smart Code Reviewer

AI-powered code review assistant that analyzes code for readability, structure, maintainability, security, and performance.

**[Try it live](https://smart-code-reviewer.streamlit.app/)**

## What It Does

Paste any code snippet and get an instant structured review:

- **Overall score** (1-10) with color-coded badge
- **Category breakdown** — scores across multiple quality dimensions
- **Specific issues** sorted by severity (Critical / Warning / Suggestion)
- **Side-by-side diff** — see the original problematic code next to the suggested fix
- **Positive highlights** — what the code does well

## Features

| Feature | Description |
|---------|-------------|
| **Auto language detection** | Detects Python, JavaScript, TypeScript, Java, Go, C++, and Rust from code syntax |
| **Comprehensive mode** | When no focus area is selected, reviews against 10 quality checks (naming, structure, error handling, DRY, type safety, complexity, security, performance, docs, testability) |
| **Focused mode** | Select specific areas (Readability, Structure, Maintainability, Security, Performance) to deep-dive |
| **Demo samples** | 4 pre-loaded code snippets with intentional flaws for quick testing |
| **Retry logic** | Auto-retries on transient LLM failures (JSON parse errors, missing keys) |

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM**: [Llama 3.3 70B](https://groq.com/) via Groq (free tier, ultra-fast inference)
- **Hosting**: [Streamlit Community Cloud](https://share.streamlit.io/) (free)

## Run Locally

```bash
# Clone the repo
git clone https://github.com/Abd3lwahab/smart-code-reviewer.git
cd smart-code-reviewer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key (free at https://console.groq.com/keys)
mkdir -p .streamlit
echo 'GROQ_API_KEY = "your-key-here"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
```

## Project Structure

```
smart-code-reviewer/
├── app.py              # Streamlit UI — input, sidebar, results display
├── reviewer.py         # Prompt engineering, Groq API, language detection
├── sample_code.py      # 4 demo snippets (Python, JS, Java, Go)
├── requirements.txt    # streamlit + groq
├── PLAN.md             # Implementation plan and progress tracking
└── .streamlit/
    └── config.toml     # Dark theme configuration
```

## How It Works

1. User pastes code (or loads a demo sample)
2. Language is auto-detected via regex heuristics
3. A structured prompt is sent to Llama 3.3 70B via Groq, requesting JSON output with scores, issues, and fixes
4. The prompt adapts based on whether focus areas are selected (deep-dive) or not (comprehensive 10-point checklist)
5. Response is parsed, validated, and rendered with color-coded scores, severity badges, and side-by-side code diffs

## License

MIT
