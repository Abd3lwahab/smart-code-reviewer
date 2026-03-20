# Smart Code Reviewer — Implementation Plan

## Context
Build a prototype AI assistant that reviews code for readability, structure, and maintainability. Must be 100% usable without entering any API keys or setup — just visit a URL and use it.

## Architecture

**Streamlit app** deployed on **Streamlit Community Cloud** (free hosting) using **Groq** (Llama 3.3 70B) as the LLM backend. The API key is stored as a Streamlit secret — invisible to the end user.

### Why Groq + Llama 3.3 70B?
- Truly free tier — no credit card, no regional restrictions (Gemini blocked in Egypt)
- 30 requests/minute, 6000 tokens/min — more than enough for a demo
- Ultra-fast responses (~1-2s) thanks to Groq LPU hardware
- High quality code analysis from Llama 3.3 70B
- API key stored server-side as a Streamlit secret → interviewer just visits the URL

## Files

```
smart-code-reviewer/
├── app.py                    # Main Streamlit application
├── reviewer.py               # LLM review logic + prompt engineering (Groq)
├── sample_code.py            # Pre-loaded code samples for quick demo
├── requirements.txt          # streamlit + groq
├── .streamlit/
│   ├── config.toml           # Theme configuration
│   └── secrets.toml          # GROQ_API_KEY (gitignored)
└── PLAN.md                   # This plan
```

## Detailed Design

### 1. `app.py` — Main UI
- **Header**: Title, subtitle, green accent
- **Sidebar**: Language selector (Python, JavaScript, Java, Go, TypeScript, C++, Rust), **optional** review focus multi-select (Readability, Structure, Maintainability, Security, Performance)
- **When focus areas are empty (default)**: Comprehensive review against 10 quality checks
- **When specific focus areas are selected**: Deep-dive only those categories
- **Main area**: Code input, quick demo buttons, review button
- **Results**: Overall score badge, category breakdown, severity-tagged issues with code fixes, positive highlights

### 2. `reviewer.py` — Core Review Logic
- Groq client with Llama 3.3 70B model
- Structured prompt returning JSON (overall_score, categories, issues, positive_notes)
- Adaptive prompt: full checklist vs focused review
- JSON parsing with markdown fence stripping

### 3. `sample_code.py` — Demo Samples
- 4 samples: Python (god function), JavaScript (callback hell), Java (SOLID violations), Go (error handling)

## Deployment Steps
1. Push to GitHub repo
2. Connect to Streamlit Community Cloud (free)
3. Add Groq API key as a Streamlit secret (`GROQ_API_KEY`)
4. Share the public URL

## Deliverables for Submission
- **Public link**: Streamlit Cloud URL
- **Dataset**: N/A (uses user-provided or sample code)
- **100-word summary**: (will draft after building)

---

## TODO List

### Phase 1: Core Build ✅ COMPLETE
- [x] Create project directory and `requirements.txt`
- [x] Create `.streamlit/config.toml` with green theme
- [x] Build `sample_code.py` with 4 intentionally flawed code snippets
- [x] Build `reviewer.py` — prompt engineering + Groq API integration
- [x] Implement default comprehensive checklist (when no focus areas selected)
- [x] Implement focused review mode (when specific areas selected)
- [x] Build `app.py` — full Streamlit UI (sidebar, input, results display)
- [x] Switch from Gemini (blocked in Egypt) to Groq (works globally)
- [x] Verify locally — app runs, reviews work end-to-end

### Phase 2: Polish ✅ COMPLETE
- [x] Add loading progress bar with step messages during review
- [x] Add color-coded circular score badges (green/orange/red)
- [x] Add styled category cards with progress bars
- [x] Add severity pill badges (critical/warning/suggestion)
- [x] Add code diff display for suggested fixes
- [x] Handle edge cases (empty input, rate limits, API config errors)
- [x] Add retry logic (3 attempts) for JSON parse / missing key failures
- [x] Improve UI layout — category card grid, issue summary chips, responsive columns
- [x] Add "Clear Results" button
- [x] Sort issues by severity (critical first)
- [x] Move footer/branding to sidebar + bottom of results
- [x] Side-by-side diff view (original code vs suggested fix) in issues
- [x] Simplified demo buttons (paste only, no auto-review)
- [x] CSS Grid category cards (equal width/height)
- [x] Auto-detect language from code (removed manual selector)
- [x] Heuristic language detection for 7 languages (Python, JS, TS, Java, Go, C++, Rust)

### Phase 3: Deploy & Submit ← CURRENT
- [ ] Create .gitignore (exclude venv, secrets, pycache)
- [ ] Initialize git repo and push to GitHub
- [ ] Deploy on Streamlit Community Cloud
- [ ] Add Groq API key as Streamlit secret
- [ ] Verify public URL works without any login/keys
- [ ] Draft 100-word summary for submission
