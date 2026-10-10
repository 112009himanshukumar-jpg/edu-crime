# Publish EDU-cRIME online (Render + Groq AI)

This deployment keeps the existing Flask app and its built-in cases. In the hosted version, `AI_PROVIDER=groq` uses the Groq OpenAI-compatible API; locally, the default remains Ollama. Never put an API key in source code or commit it to GitHub.

## What you need
- A GitHub account.
- A Render account.
- A Groq account and API key for AI-generated cases. Check the provider's current terms, account limits, and pricing before using it.

## 1. Upload the project to GitHub
1. Download and extract `EDU-cRIME-Online-Ready.zip`.
2. On GitHub, create a **private** repository named `edu-crime`.
3. Upload the *contents* of the extracted `edu-crime` folder to the repository root. Make sure `app.py`, `requirements.txt`, `render.yaml`, `templates/`, and `static/` are at the top level (not inside another nested `edu-crime` folder).
4. Do not upload `.env`, `.venv`, API keys, or personal data.

## 2. Get a Groq API key
1. Visit https://console.groq.com/ and sign in.
2. Create an API key in the Groq console.
3. Copy it somewhere private temporarily. Never paste it into `app.py`, GitHub, or a public chat.

## 3. Deploy with Render Blueprint
1. Visit https://render.com/ and sign in.
2. Choose **New + → Blueprint** (the wording may vary) and connect your GitHub account.
3. Select the private `edu-crime` repository and its main branch.
4. Review the service configuration read from `render.yaml`.
5. When prompted for `GROQ_API_KEY`, enter the key in Render's secret/environment variable field.
6. Deploy the Blueprint and wait for the build and deploy to finish.
7. Open the `https://edu-crime-....onrender.com` URL shown on the service page. That is your public shareable link.

If Render doesn't prompt for `GROQ_API_KEY`, open the service's **Environment** settings and add:
- `AI_PROVIDER` = `groq`
- `AI_BASE_URL` = `https://api.groq.com/openai/v1`
- `AI_MODEL` = `openai/gpt-oss-20b`
- `GROQ_API_KEY` = your secret key
- `FLASK_SECRET_KEY` = a long random secret (if not already generated)
- `SESSION_COOKIE_SECURE` = `1`
Save changes and redeploy.

## 4. Test before sharing
- Open the public HTTPS link in a private/incognito window.
- Log in using a **fictional demo name**, not a real student's personal information.
- Complete one built-in case.
- Try one AI-generated case. If it fails, check Render → Logs and verify the `GROQ_API_KEY`, model ID, and account limits.
- Check `https://YOUR-RENDER-URL/healthz`; it should return a small JSON status response.

## Important limits for an exhibition
- Free hosting may sleep after inactivity, so the first request can be slow. Open the site before judges arrive.
- The starter stores profile statistics in a local JSON file. Free ephemeral hosting may reset this file after restarts/redeploys; it is not durable multi-user storage.
- This starter has not had a full security audit. Do not use it to collect real sensitive student data or passwords. Use fictional demo profiles for the exhibition. For a larger public launch, add database-backed storage, CSRF protection, rate limiting, and a privacy notice.
- AI generation requires internet access and a valid provider key. Built-in fixed cases remain available without the AI provider.

## Local Windows use
The local setup scripts continue to use Ollama by default. To use local AI, install/run Ollama and download the configured model (`ollama pull gemma3:270m`).
