# Conversation to PRD Generator

Tool sederhana berbasis Python dan LLM untuk mengubah hasil conversation (misalnya dari Claude AI) menjadi Product Requirement Document (PRD) dalam format Markdown.

---

## 📦 Requirements

- Python 3.9+
- OpenAI API Key

Install dependencies:

```bash
pip install beautifulsoup4 openai python-dotenv
````

---

## 🔑 Setup API Key

Buat file `.env` di root project:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

---

## 📄 Input

1. Buka link Claude di browser
2. Tekan **Ctrl + S** → Save as HTML
3. Rename file menjadi:

```
claude_page.html
```

4. Letakkan di folder project

---

## ▶️ How to Run

```bash
python main.py
```

---

## 📤 Output

* `conversation.txt` → hasil parsing conversation
* `prd.md` → hasil PRD dalam Markdown