# AI Email Generator

A production-oriented desktop web application for generating polished business emails locally with **Python**, **Streamlit**, and **Ollama**.

The app runs on your machine, talks to your local Ollama server, and provides a professional editor, export options, history, and a polished UI designed for practical day-to-day use.

## Features

- Local-first generation through Ollama
- Structured prompts for consistent business writing
- Support for common email scenarios:
  - Job applications
  - Leave requests
  - Business proposals
  - Meeting requests
  - Complaint or escalation emails
  - Thank-you notes
  - Follow-ups
  - Custom emails
- Editable subject and body after generation
- Copy to clipboard support
- Export to TXT, Markdown, DOCX, and PDF
- Session-based history of recent drafts
- Connection and model discovery for local Ollama
- Professional dark UI with custom styling

## Project Structure

```text
AI_Email_Generator/
├─ app.py
├─ email_generator.py
├─ ai_email_generator/
│  ├─ config.py
│  ├─ exports.py
│  ├─ models.py
│  ├─ ollama_service.py
│  ├─ parsing.py
│  ├─ prompts.py
│  ├─ styles.py
│  └─ templates.py
├─ tests/
├─ requirements.txt
├─ .env.example
└─ .streamlit/config.toml
```

## Prerequisites

- Python 3.10 or newer
- Ollama installed and running locally
- At least one Ollama model pulled, for example:

```bash
ollama pull qwen2.5:1.5b
```

## Installation

1. Clone or copy the project to your machine.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Optional: create a `.env` file from `.env.example` and adjust values if needed.

## Run the App

```bash
streamlit run app.py
```

The app will open in your browser as a local desktop-style web application.

## Environment Variables

- `OLLAMA_HOST` - Ollama base URL, usually `http://localhost:11434`
- `OLLAMA_DEFAULT_MODEL` - Default model name, such as `qwen2.5:1.5b`
- `EMAILGEN_TEMPERATURE` - Default creativity level
- `EMAILGEN_TOP_P` - Sampling setting
- `EMAILGEN_MAX_TOKENS` - Maximum output tokens
- `EMAILGEN_HISTORY_LIMIT` - Number of drafts kept in session history
- `EMAILGEN_DEFAULT_LANGUAGE` - Default language for the generator
- `EMAILGEN_CLIPBOARD` - Enable or disable clipboard copy

## How It Works

1. The user fills in the email brief.
2. The app builds a structured prompt tailored to the selected scenario.
3. Ollama returns a JSON response with a subject and full email body.
4. The UI normalizes the response, lets the user edit it, and provides export/download actions.

## Testing

The core logic is covered with lightweight unit tests:

```bash
python -m unittest discover -s tests -v
```

## Notes for GitHub

- The app is modular and ready to be committed as-is.
- `.gitignore` excludes cache, virtual environment, and local secret files.
- `.streamlit/config.toml` provides a consistent visual theme.

## Troubleshooting

- If the model list is empty, confirm Ollama is running.
- If generation fails, verify the exact model tag exists locally.
- If clipboard copy fails, the OS clipboard backend may be unavailable in the current session.

## License

Add your preferred license before publishing publicly.
