# EDU-cRIME School IT Exhibition Guide

## One-sentence pitch
EDU-cRIME is a detective-themed learning website that turns school subjects into short fictional investigations, where visitors inspect clues, answer questions, and learn from explanations.

## Exhibition-day reliability plan
- Bring the laptop charger, mouse, and a phone hotspot if permitted.
- Test the website on the actual laptop and browser before exhibition day.
- Run `SETUP-EDU-cRIME.bat` once on Windows. Thereafter, launch with `Start-EDU-cRIME.bat`.
- The fixed/prepared cases are the dependable offline demo path. If AI generation is unavailable, the app now opens a prepared backup case and clearly tells the visitor.
- If showing live AI generation, verify the configured provider/model and internet connection before visitors arrive. Never show or share API keys.
- Use a fictional visitor name; do not enter sensitive personal information.
- Keep one prepared subject/case ready and use it if the live AI service is slow.

## 3-minute live demo
1. Welcome screen (20 seconds): introduce EDU-cRIME and the problem it addresses.
2. Sign in with a fictional name and select a stream (20 seconds).
3. Open one fixed case (20 seconds); point out the story and three clues (30 seconds).
4. Answer the three questions (45 seconds).
5. Review score and explanations (25 seconds).
6. If internet and hosted AI are working, generate one AI case; otherwise demonstrate the transparent fallback (20 seconds).
7. Close with the technology stack and educational value (20 seconds).

## Judge-facing explanation
- Frontend: responsive HTML templates, CSS, and JavaScript.
- Backend: Python Flask routes and session-based case flow.
- Learning loop: fictional story → clues → multiple-choice questions → score and explanations.
- AI: optional server-side generation through local Ollama or a configured hosted OpenAI-compatible API. AI is not required for prepared cases.
- Reliability design: prepared cases and an explicit fallback allow the exhibition to continue if the AI service or internet fails.

## Suggested judging questions
**Why did you build this?** To make revision more active by asking learners to apply subject knowledge to a fictional investigation.

**Where is AI used?** In the optional case generator, which requests a structured story, clues, and questions. The website validates the response before using it.

**What happens if the internet fails?** Prepared cases remain available. Live hosted AI may not work, so the app switches to a prepared case and displays a message.

**What would you improve next?** Add a persistent database, teacher dashboard, privacy controls, rate limits, and stronger production security before a school-wide rollout.

## Honest limitations to mention
- Live AI generation needs a working local Ollama setup or a configured hosted API key and internet access.
- Profiles in this prototype use a local JSON file; ephemeral online hosting can reset this data.
- This is an educational prototype, not a forensic tool. Cases are fictional and should not be used to accuse real people.
