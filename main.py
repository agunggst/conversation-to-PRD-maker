import re
import os
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================
INPUT_HTML = "claude_page.html"   # hasil Ctrl+S dari browser
OUTPUT_CONV = "conversation.txt"
OUTPUT_PRD = "prd.md"

# init OpenAI client
client = OpenAI(api_key="")

# =========================
# LOAD & EXTRACT TEXT
# =========================
def load_html_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # remove script/style/noscript
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return text


# =========================
# PARSER (HEURISTIC)
# =========================
def parse_claude_text(text: str):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    messages = []
    current = None

    def push_current():
        nonlocal current
        if current and current["content"].strip():
            messages.append(current)
        current = None

    for line in lines:
        low = line.lower()

        is_user = low.startswith(("human", "user"))
        is_assistant = low.startswith(("assistant", "claude"))

        if is_user:
            push_current()
            current = {"role": "user", "content": line}
            continue

        if is_assistant:
            push_current()
            current = {"role": "assistant", "content": line}
            continue

        # fallback: lanjutkan konten
        if current is None:
            current = {"role": "user", "content": line}
        else:
            current["content"] += " " + line

    push_current()
    return messages


# =========================
# CLEANER
# =========================
def clean_conversation(messages):
    cleaned = []

    for msg in messages:
        content = clean_text(msg.get("content", ""))
        role = normalize_role(msg.get("role", ""))

        if content:
            cleaned.append({
                "role": role,
                "content": content
            })

    return cleaned


def normalize_role(role: str):
    role = role.lower()

    if "assistant" in role:
        return "assistant"
    if "user" in role:
        return "user"

    return "user"


def clean_text(text: str):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"```[\s\S]*?```", "", text)

    noise_patterns = [
        r"copy",
        r"share",
        r"regenerate",
        r"privacy",
        r"terms",
        r"cloudflare",
        r"ray id",
        r"performance and security"
    ]

    for p in noise_patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    return text.strip()


# =========================
# FORMATTER
# =========================
def to_prompt_format(messages):
    return "\n\n".join([
        f"{m['role'].upper()}:\n{m['content']}"
        for m in messages
    ])


# =========================
# PROMPT BUILDER
# =========================
def build_prompts(conversation_text: str):
    system_prompt = """
You are a senior Product Manager responsible for creating high-quality Product Requirement Documents (PRDs).

Your task is to convert a conversation transcript into a clear, structured, and actionable PRD in Markdown format.

## OUTPUT FORMAT

# Product Requirement Document (PRD)

## 1. Overview
## 2. Goals & Success Metrics
## 3. Users & Problem Statement
## 4. Solution Overview
## 5. Features & Functional Requirements
## 6. Acceptance Criteria
## 7. Out of Scope
## 8. Assumptions & Risks
## 9. Dependencies

## RULES
- Output only Markdown
- No explanation outside PRD
- Keep concise and structured
"""

    user_prompt = f"""
Convert this conversation into PRD:

{conversation_text}
"""

    return system_prompt, user_prompt


# =========================
# GENERATE PRD
# =========================
def generate_prd(conversation_text: str):
    system_prompt, user_prompt = build_prompts(conversation_text)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.responses.create(
        model="gpt-5-mini",
        input=messages,
        # temperature=0.3
    )

    return response.output_text


# =========================
# MAIN
# =========================
def run():
    print("📄 Loading HTML...")
    raw_text = load_html_text(INPUT_HTML)

    print("🧠 Parsing...")
    messages = parse_claude_text(raw_text)

    print("🧹 Cleaning...")
    cleaned = clean_conversation(messages)

    print("🧩 Formatting...")
    formatted = to_prompt_format(cleaned)

    # save conversation
    with open(OUTPUT_CONV, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"💾 Saved conversation to {OUTPUT_CONV}")

    print("🤖 Generating PRD...")
    prd = generate_prd(formatted)

    with open(OUTPUT_PRD, "w", encoding="utf-8") as f:
        f.write(prd)

    print(f"📄 PRD saved to {OUTPUT_PRD}")


if __name__ == "__main__":
    run()