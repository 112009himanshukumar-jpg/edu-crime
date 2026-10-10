# EDU-cRIME — Detective-style learning app

A responsive Flask learning website with a dark detective theme, subject streams, built-in detective cases, quizzes, scores, explanations, profile statistics, and optional AI-generated cases.

## Publish online
Read [DEPLOY-ONLINE.md](DEPLOY-ONLINE.md) for step-by-step publishing using Render and Groq-hosted AI. Keep API keys in the hosting provider's secret/environment settings, never in source code or GitHub.

## Run locally on Windows
1. Install Python 3.10+.
2. Double-click `SETUP-EDU-cRIME.bat`.
3. When setup finishes, double-click `Start-EDU-cRIME.bat`.
4. Open http://127.0.0.1:5000.

Local AI uses Ollama by default. Install/run Ollama and download the model with `ollama pull gemma3:270m`.

## Hosted AI configuration
The hosted deployment uses these environment variables on Render:
- `AI_PROVIDER=groq`
- `AI_BASE_URL=https://api.groq.com/openai/v1`
- `AI_MODEL=openai/gpt-oss-20b`
- `GROQ_API_KEY` (secret)
- `FLASK_SECRET_KEY` (long random secret)
- `SESSION_COOKIE_SECURE=1`

## Important notes
The starter stores profiles in `data/users.json`; on free ephemeral hosting, these statistics can reset after restarts or redeploys. This is a school exhibition starter, not a security-audited public service. Use fictional demo profiles, not real sensitive student information.
