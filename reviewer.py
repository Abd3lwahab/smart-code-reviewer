"""Core review logic — prompt engineering + Groq API integration."""

import json
import re
import time
from groq import Groq
import streamlit as st


def detect_language(code: str) -> str:
    """Detect programming language from code using syntax heuristics."""
    code_stripped = code.strip()

    # Order matters — check most distinctive patterns first
    patterns = [
        # Go: package, func, := , fmt.
        ("Go", [r'\bpackage\s+\w+', r'\bfunc\s+\w+', r':=', r'\bfmt\.\w+']),
        # Rust: fn main, let mut, ::, ->
        ("Rust", [r'\bfn\s+\w+', r'\blet\s+mut\b', r'::\w+', r'\bmatch\b.*\{', r'impl\s+']),
        # Java: public class, System.out, void main, @Override
        ("Java", [r'\bpublic\s+class\b', r'System\.out', r'void\s+main', r'@Override', r'\bimport\s+java\.']),
        # TypeScript: specific TS patterns (before JS since TS is superset)
        ("TypeScript", [r':\s*(string|number|boolean|any|void)\b', r'\binterface\s+\w+', r'<\w+>', r'\bas\s+\w+']),
        # C++: #include, std::, cout, nullptr
        ("C++", [r'#include\s*<', r'\bstd::', r'\bcout\b', r'\bnullptr\b', r'\btemplate\s*<']),
        # Python: def, import, self, elif, __init__
        ("Python", [r'\bdef\s+\w+\s*\(', r'\bimport\s+\w+', r'\bself\b', r'\belif\b', r'__init__']),
        # JavaScript: function, =>, const/let, require, console.log
        ("JavaScript", [r'\bfunction\s+\w+', r'=>', r'\b(const|let)\s+\w+', r'\brequire\s*\(', r'console\.\w+']),
    ]

    scores = {}
    for lang, lang_patterns in patterns:
        score = sum(1 for p in lang_patterns if re.search(p, code_stripped))
        if score > 0:
            scores[lang] = score

    if not scores:
        return "Python"  # Default fallback

    return max(scores, key=scores.get)

# ---------- Default comprehensive checklist ----------
DEFAULT_CHECKLIST = [
    "Naming conventions & clarity",
    "Code structure & modularity",
    "Error handling & edge cases",
    "DRY principle & code duplication",
    "Type safety & input validation",
    "Complexity & readability",
    "Security best practices",
    "Performance considerations",
    "Documentation & comments",
    "Testability",
]

# ---------- Category descriptions for focused mode ----------
FOCUS_DESCRIPTIONS = {
    "Readability": "naming conventions, code clarity, formatting, comments, self-documenting code",
    "Structure": "modularity, design patterns, SOLID principles, separation of concerns, class/function organization",
    "Maintainability": "DRY, complexity, coupling, cohesion, testability, extensibility",
    "Security": "injection vulnerabilities, input validation, secrets exposure, auth issues, data sanitization",
    "Performance": "algorithmic complexity, memory usage, unnecessary allocations, N+1 queries, caching opportunities",
}


def _build_prompt(code: str, language: str, focus_areas: list[str]) -> str:
    """Build the review prompt based on whether focus areas are selected."""

    if focus_areas:
        focus_section = "Focus your review ONLY on these areas (deep-dive each):\n"
        for area in focus_areas:
            desc = FOCUS_DESCRIPTIONS.get(area, area)
            focus_section += f"- **{area}**: {desc}\n"
    else:
        focus_section = "Perform a comprehensive review using this checklist:\n"
        for item in DEFAULT_CHECKLIST:
            focus_section += f"- {item}\n"

    return f"""You are a senior software engineer performing a code review. Analyze the following {language} code and provide a structured review.

{focus_section}

Return your review as a valid JSON object with this EXACT structure (no markdown, no code fences, ONLY raw JSON):

{{
  "overall_score": <number 1-10>,
  "summary": "<1-2 sentence overall assessment>",
  "categories": [
    {{
      "name": "<category name>",
      "score": <number 1-10>
    }}
  ],
  "issues": [
    {{
      "severity": "<critical|warning|suggestion>",
      "category": "<which category this belongs to>",
      "line_ref": "<line number or range, e.g. '5' or '12-18'>",
      "title": "<short issue title>",
      "description": "<explain the problem>",
      "suggestion": "<how to fix it>",
      "original_code": "<the exact original code snippet that has the issue, properly formatted with newlines>",
      "fixed_code": "<the corrected version of that same snippet, properly formatted with newlines>"
    }}
  ],
  "positive_notes": [
    "<something the code does well — always include at least one>"
  ]
}}

Important rules:
- Be specific: reference actual variable names, line numbers, and code patterns
- For each issue, include BOTH original_code (the problematic snippet from the input) and fixed_code (the corrected version). These must be properly formatted multi-line code, NOT compressed into a single line.
- Always find at least one positive thing to say
- Return between 3-8 issues, prioritized by severity
- Scores: 1-3 = poor, 4-5 = needs work, 6-7 = acceptable, 8-9 = good, 10 = excellent
- Return ONLY valid JSON, no other text
- IMPORTANT: All code in original_code and fixed_code must use \\n for newlines so it is valid JSON but renders as multi-line code

CODE TO REVIEW:
```{language.lower()}
{code}
```"""


def _parse_response(text: str) -> dict:
    """Parse the LLM response, handling potential markdown fences."""
    cleaned = text.strip()
    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


def review_code(code: str, language: str, focus_areas: list[str]) -> dict:
    """
    Send code to Groq (Llama 3.3 70B) for review and return structured results.

    Args:
        code: The source code to review
        language: Programming language
        focus_areas: List of focus areas, or empty for comprehensive review

    Returns:
        dict with keys: overall_score, summary, categories, issues, positive_notes
    """
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not configured. Add it to .streamlit/secrets.toml\n"
            "Get a free key at: https://console.groq.com/keys"
        )

    client = Groq(api_key=api_key)
    prompt = _build_prompt(code, language, focus_areas)

    # Retry up to 3 times for transient failures
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer. You return ONLY valid JSON, no markdown fences, no extra text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_completion_tokens=4096,
            )

            result = _parse_response(response.choices[0].message.content)

            # Validate required keys
            required = ["overall_score", "summary", "categories", "issues", "positive_notes"]
            for key in required:
                if key not in result:
                    raise ValueError(f"Missing key in response: {key}")

            return result

        except json.JSONDecodeError as e:
            # LLM returned invalid JSON — retry with same prompt
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
        except ValueError as e:
            # Missing keys — retry
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
        except Exception as e:
            # API errors — raise immediately (don't retry auth/rate issues)
            raise

    raise last_error  # type: ignore[misc]
