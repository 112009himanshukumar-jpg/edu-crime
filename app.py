import json
import os
import random
import re
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

try:
    from ollama import chat as ollama_chat
except ImportError:
    ollama_chat = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


# The fixed cases below are adapted from the original EDU-cRIME program.
# Each case uses the same format so the UI can display every subject consistently.
FIXED_CASES = {
    "Physics": {
        "title": "The Mystery of the Disappearing Image",
        "story": "A student investigating a convex lens notices that the image changes position as the object is moved. Your task is to identify the optical condition.",
        "clues": ["The object is moved closer to the principal focus.", "The object remains outside the principal focus.", "The image changes position and apparent size as the object moves."],
        "questions": [{
            "question": "What happens as an object approaches the principal focus from outside a convex lens?",
            "options": ["The image moves farther away and becomes larger", "The image always becomes smaller", "The image disappears at every position", "The image remains at the same position"],
            "answer": "A",
            "explanation": "As the object approaches the principal focus from outside, the real image moves farther from the lens and becomes larger."
        }, {
            "question": "Where is the image formed when an object is at the principal focus of a convex lens?",
            "options": ["At infinity", "At the optical centre", "At the principal focus", "On the same side as the object"],
            "answer": "A",
            "explanation": "For an object at the principal focus, refracted rays emerge parallel and the image is considered to be at infinity."
        }, {
            "question": "What is the nature of the image when an object is placed between a convex lens and its principal focus?",
            "options": ["Virtual, erect and magnified", "Real, inverted and diminished", "Real, erect and same size", "No image can form"],
            "answer": "A",
            "explanation": "Within the focal length, a convex lens forms a virtual, erect, magnified image on the object's side."
        }]
    },
    "Chemistry": {
        "title": "The Silent Poison",
        "story": "In a fictional mystery, a suspicious white powder is found near an office scene. Forensic testing points to a chemical compound containing cyanide. Investigators must interpret the evidence carefully.",
        "clues": ["Forensic testing indicates a compound containing cyanide.", "A beverage was consumed shortly before the incident.", "An unverified sample container was brought into the office by the miner."],
        "questions": [
            {"question": "Which chemical group is specifically mentioned in the forensic clue?", "options": ["Cyanide", "Carbonate", "Nitrate", "Sulphate"], "answer": "A", "explanation": "The clue explicitly identifies a compound containing cyanide."},
            {"question": "Which detail establishes a possible route by which a substance was consumed?", "options": ["A beverage was consumed", "A window was open", "A clock had stopped", "A notebook was missing"], "answer": "A", "explanation": "The beverage detail is relevant to possible consumption; it does not by itself prove what happened."},
            {"question": "Which person is most directly linked to the unverified sample container in the clues?", "options": ["The maid", "The manager", "The miner", "No one is mentioned"], "answer": "C", "explanation": "The third clue says the miner brought an unverified sample container."}
        ]
    },
    "Mathematics": {
        "title": "The Missing Graph",
        "story": "A detective finds a mathematical graph with an important point missing. The function's first derivative is zero at the point under investigation.",
        "clues": ["The first derivative becomes zero at the point.", "The graph changes direction near the point.", "The point is being investigated using differential calculus."],
        "questions": [
            {"question": "What type of point could have a first derivative equal to zero?", "options": ["Stationary point", "Random point", "Endpoint only", "Undefined point only"], "answer": "A", "explanation": "A stationary point is a point where the derivative is zero, provided the derivative exists."},
            {"question": "Which mathematical tool is most directly used to examine the rate of change?", "options": ["Differentiation", "Matrix addition", "Simple counting", "Set union"], "answer": "A", "explanation": "Differentiation gives the derivative, which describes instantaneous rate of change."},
            {"question": "Does a zero first derivative alone guarantee a local maximum or minimum?", "options": ["Yes, always", "No, not by itself", "Only for every straight line", "Only when the function is constant"], "answer": "B", "explanation": "A stationary point can be a maximum, minimum, or neither; further analysis is needed."}
        ]
    },
    "Biology": {
        "title": "The Missing Energy",
        "story": "A cell is producing very little usable energy. Investigators examine the organelles to identify the likely source of the problem.",
        "clues": ["The cell is producing little usable energy.", "Most ATP production in many eukaryotic cells occurs in a particular organelle.", "The organelle's function is impaired."],
        "questions": [
            {"question": "Which organelle is most directly associated with most cellular ATP production?", "options": ["Nucleus", "Mitochondrion", "Ribosome", "Golgi apparatus"], "answer": "B", "explanation": "Mitochondria are the main site of oxidative phosphorylation in eukaryotic cells."},
            {"question": "What is ATP commonly described as in cells?", "options": ["A genetic code", "An energy-carrying molecule", "A cell wall", "A digestive organ"], "answer": "B", "explanation": "ATP transfers usable chemical energy for many cellular processes."},
            {"question": "Which process is strongly associated with mitochondria?", "options": ["Cellular respiration", "Photosynthesis in chloroplasts", "Protein storage in the Golgi only", "DNA translation"], "answer": "A", "explanation": "Mitochondria play a central role in aerobic cellular respiration."}
        ]
    },
    "Accountancy": {
        "title": "The Missing Balance",
        "story": "A business record is not balancing. The statement shows total assets of ₹50,000 and liabilities of ₹20,000. Find the owner's capital.",
        "clues": ["Total assets are ₹50,000.", "Total liabilities are ₹20,000.", "Use the accounting equation: Assets = Liabilities + Capital."],
        "questions": [
            {"question": "What should the owner's capital be?", "options": ["₹20,000", "₹30,000", "₹50,000", "₹70,000"], "answer": "B", "explanation": "Capital = Assets − Liabilities = ₹50,000 − ₹20,000 = ₹30,000."},
            {"question": "Which equation is the basis of this calculation?", "options": ["Assets = Liabilities + Capital", "Assets = Income − Expenses", "Capital = Liabilities − Assets", "Assets = Capital × Liabilities"], "answer": "A", "explanation": "The accounting equation states that assets equal liabilities plus owner's equity."},
            {"question": "If liabilities increased while assets stayed the same, what would happen to capital?", "options": ["It would increase", "It would decrease", "It would always double", "It would stay unchanged"], "answer": "B", "explanation": "With assets fixed, a rise in liabilities means capital must fall to keep the equation balanced."}
        ]
    },
    "Business Studies": {
        "title": "The Falling Sales",
        "story": "A company notices that its sales are falling. The manager gathers information about customers, competitors, and market trends before deciding what to do.",
        "clues": ["Sales have fallen.", "The manager collects information about customers and competitors.", "The information is gathered before choosing a course of action."],
        "questions": [
            {"question": "Which management function is most closely associated with deciding in advance what to do?", "options": ["Planning", "Controlling", "Recruitment", "Staffing"], "answer": "A", "explanation": "Planning involves setting objectives and deciding in advance how to achieve them."},
            {"question": "Why might the manager study competitors and customers?", "options": ["To inform decisions", "To avoid all planning", "To remove accounting records", "To guarantee sales instantly"], "answer": "A", "explanation": "Market information helps managers make informed plans and decisions."},
            {"question": "Which function checks actual performance against standards?", "options": ["Controlling", "Recruitment", "Directing only", "Packaging"], "answer": "A", "explanation": "Controlling compares actual results with standards and supports corrective action."}
        ]
    },
    "Economics": {
        "title": "The Rising Price",
        "story": "The price of a product increases and consumers buy less of it. Other factors are assumed to remain unchanged.",
        "clues": ["The product's price increased.", "Consumers bought less of the product.", "Other factors remained unchanged."],
        "questions": [
            {"question": "Which economic relationship is illustrated?", "options": ["Law of demand", "Law of supply", "National income identity", "Law of diminishing returns only"], "answer": "A", "explanation": "Ceteris paribus, quantity demanded generally falls when price rises."},
            {"question": "What does 'other factors remain unchanged' mean in this context?", "options": ["Ceteris paribus", "Inflation targeting", "Fiscal deficit", "Opportunity cost is zero"], "answer": "A", "explanation": "Ceteris paribus means other relevant factors are held constant."},
            {"question": "In the usual demand curve, price and quantity demanded are generally:", "options": ["Directly related", "Inversely related", "Always equal", "Unrelated in every case"], "answer": "B", "explanation": "The law of demand describes an inverse relationship, other things equal."}
        ]
    },
    "History": {
        "title": "The Missing Document",
        "story": "A historical document refers to a major uprising against colonial rule that began in 1857. The detective must identify the event.",
        "clues": ["The document mentions the year 1857.", "It describes resistance against colonial rule.", "The event is also known as the Indian Rebellion of 1857."],
        "questions": [
            {"question": "Which event is being investigated?", "options": ["Revolt of 1857", "Quit India Movement", "Non-Cooperation Movement", "Civil Disobedience Movement"], "answer": "A", "explanation": "The year and description point to the Revolt of 1857."},
            {"question": "Which century did the event take place in?", "options": ["17th century", "18th century", "19th century", "20th century"], "answer": "C", "explanation": "The year 1857 falls in the nineteenth century."},
            {"question": "Which source would be a primary source for studying the event?", "options": ["A letter written during the event", "A modern fictional film", "A recent textbook summary only", "An unrelated advertisement"], "answer": "A", "explanation": "A contemporary letter can be a primary source from the period."}
        ]
    },
    "Political Science": {
        "title": "The Missing Power",
        "story": "A government decision is being investigated. The constitution divides powers between different levels of government.",
        "clues": ["The constitution distributes governmental powers.", "More than one level of government has authority.", "The arrangement is constitutionally defined."],
        "questions": [
            {"question": "What type of system is described?", "options": ["Federal system", "Dictatorship", "Monarchy", "Military rule"], "answer": "A", "explanation": "Federal systems constitutionally divide powers between levels of government."},
            {"question": "What is one purpose of a written constitution in a federal system?", "options": ["To define powers and responsibilities", "To remove all courts", "To abolish regional government", "To make elections unnecessary"], "answer": "A", "explanation": "A constitution can specify how authority is divided among governments."},
            {"question": "Which level may exist alongside a national government in a federation?", "options": ["State or provincial government", "No other government", "Only a private company", "Only an international court"], "answer": "A", "explanation": "Federations commonly have national and state/provincial levels of government."}
        ]
    },
    "Geography": {
        "title": "The Changing Land",
        "story": "A village notices that soil is being removed from farmland during heavy rainfall. Vegetation has been cleared from a nearby slope.",
        "clues": ["Soil is removed during heavy rainfall.", "Vegetation has been removed from the slope.", "The exposed soil is vulnerable to runoff."],
        "questions": [
            {"question": "What process is being investigated?", "options": ["Soil erosion", "Earthquake", "Volcanism", "Tidal action"], "answer": "A", "explanation": "Soil erosion is the removal of topsoil by water, wind, or other agents."},
            {"question": "How can vegetation help reduce soil erosion?", "options": ["Roots help hold soil in place", "It increases runoff in every case", "It removes all minerals", "It prevents all rainfall"], "answer": "A", "explanation": "Plant roots bind soil and vegetation can reduce the impact of runoff."},
            {"question": "Which practice can help limit erosion on slopes?", "options": ["Terracing", "Removing all ground cover", "Increasing bare soil", "Channeling all water downhill"], "answer": "A", "explanation": "Terracing slows runoff and helps reduce soil loss on slopes."}
        ]
    },
}

STREAMS = {
    "PCM": ["Physics", "Chemistry", "Mathematics"],
    "PCB": ["Physics", "Chemistry", "Biology"],
    "COMMERCE": ["Accountancy", "Business Studies", "Economics", "Mathematics"],
    "HUMANITIES": ["History", "Political Science", "Geography", "Economics"],
}
ALL_SUBJECTS = list(FIXED_CASES.keys())


def load_users():
    if not USERS_FILE.exists():
        return {}
    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_users(users):
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def current_user():
    name = session.get("username")
    if not name:
        return None
    return load_users().get(name)


def subjects_for_user(user):
    if not user:
        return ALL_SUBJECTS
    return STREAMS.get(user.get("stream"), ALL_SUBJECTS)


def make_ai_prompt(subject):
    return f"""Create one original, short, fictional detective case for the school subject {subject}, suitable for Class 11–12.
Return a JSON object with exactly these keys: title, story, clues, questions.
clues: exactly 3 useful strings.
questions: exactly 3 objects, each with question, options, answer, explanation.
options: exactly 4 meaningful strings per question.
answer: A, B, C, or D, matching options positions 1–4.
Keep the story and learning content safe, accurate, concise, and educational. Avoid placeholder text."""


def generate_ai_case(subject):
    """Generate and validate a case with local Ollama or a hosted OpenAI-compatible API."""
    provider = os.environ.get("AI_PROVIDER", "ollama").strip().lower()
    prompt = make_ai_prompt(subject)
    try:
        if provider == "groq":
            if OpenAI is None:
                raise RuntimeError("Hosted AI support is missing. Install the requirements.txt packages.")
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("GROQ_API_KEY is not configured on the hosting service.")
            client = OpenAI(
                api_key=api_key,
                base_url=os.environ.get("AI_BASE_URL", "https://api.groq.com/openai/v1"),
                timeout=45.0,
                max_retries=1,
            )
            response = client.chat.completions.create(
                model=os.environ.get("AI_MODEL", "openai/gpt-oss-20b"),
                messages=[
                    {"role": "system", "content": "Return only a valid JSON object. Follow the requested case schema exactly."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=1800,
            )
            content = response.choices[0].message.content
        elif provider == "ollama":
            if ollama_chat is None:
                raise RuntimeError("The Ollama Python package is missing. Install requirements.txt.")
            response = ollama_chat(
                model=os.environ.get("OLLAMA_MODEL", "gemma3:270m"),
                messages=[{"role": "user", "content": prompt}],
                format={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "story": {"type": "string"},
                        "clues": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3},
                        "questions": {
                            "type": "array", "minItems": 3, "maxItems": 3,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "options": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
                                    "answer": {"type": "string", "enum": ["A", "B", "C", "D"]},
                                    "explanation": {"type": "string"},
                                },
                                "required": ["question", "options", "answer", "explanation"],
                            },
                        },
                    },
                    "required": ["title", "story", "clues", "questions"],
                },
                options={"num_ctx": 4096, "num_predict": 1200, "temperature": 0.4},
            )
            content = response.message.content
        else:
            raise RuntimeError(f"Unknown AI_PROVIDER '{provider}'. Use 'ollama' or 'groq'.")

        case = json.loads(content or "{}")
        validate_case(case)
        return case
    except Exception as exc:
        raise RuntimeError(
            f"{provider.title()} could not generate a valid case: {exc}. "
            "You can still use the built-in fixed cases, or check the AI provider settings."
        ) from exc


def validate_case(case):
    if not isinstance(case, dict):
        raise ValueError("The AI response was not a JSON object.")
    if not isinstance(case.get("title"), str) or not case["title"].strip():
        raise ValueError("The case title is missing.")
    if not isinstance(case.get("story"), str) or not case["story"].strip():
        raise ValueError("The case story is missing.")
    if not isinstance(case.get("clues"), list) or len(case["clues"]) != 3:
        raise ValueError("The case must contain exactly three clues.")
    if not isinstance(case.get("questions"), list) or len(case["questions"]) != 3:
        raise ValueError("The case must contain exactly three questions.")
    for clue in case["clues"]:
        if not isinstance(clue, str) or not clue.strip():
            raise ValueError("One of the clues is empty.")
    for q in case["questions"]:
        if not isinstance(q, dict) or not isinstance(q.get("question"), str) or not q["question"].strip():
            raise ValueError("A question is missing.")
        if not isinstance(q.get("options"), list) or len(q["options"]) != 4 or not all(isinstance(x, str) and x.strip() for x in q["options"]):
            raise ValueError("Each question must have four non-empty options.")
        if q.get("answer") not in ["A", "B", "C", "D"]:
            raise ValueError("A question has an invalid answer key.")
        if not isinstance(q.get("explanation"), str) or not q["explanation"].strip():
            raise ValueError("A question explanation is missing.")


def start_case(subject, mode):
    if subject not in FIXED_CASES:
        flash("Please choose a valid subject.", "error")
        return redirect(url_for("dashboard"))
    if mode == "ai":
        try:
            case = generate_ai_case(subject)
        except RuntimeError as exc:
            app.logger.warning("AI case generation failed: %s", exc)
            flash("AI case generation is temporarily unavailable. Please try a built-in case or check the hosted AI settings.", "error")
            return redirect(url_for("dashboard"))
    else:
        case = json.loads(json.dumps(FIXED_CASES[subject]))
        # Keep fixed cases interesting while preserving the original case content.
        random.shuffle(case["questions"])
    session["active_case"] = {"subject": subject, "mode": mode, "case": case, "index": 0, "answers": []}
    return redirect(url_for("play_case"))


@app.route("/healthz")
def health_check():
    return {"status": "ok", "app": "EDU-cRIME"}, 200


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")


@app.route("/login", methods=["POST"])
def login():
    name = re.sub(r"\s+", " ", request.form.get("name", "").strip())
    age_text = request.form.get("age", "").strip()
    stream = request.form.get("stream", "").strip()
    if not name:
        flash("Please enter your name.", "error")
        return redirect(url_for("index"))
    if len(name) > 60:
        flash("Please use a name under 60 characters.", "error")
        return redirect(url_for("index"))
    if stream not in STREAMS:
        flash("Please choose a valid academic stream.", "error")
        return redirect(url_for("index"))
    age = None
    if age_text:
        try:
            age = int(age_text)
            if not 5 <= age <= 100:
                raise ValueError
        except ValueError:
            flash("Please enter an age between 5 and 100, or leave it blank.", "error")
            return redirect(url_for("index"))
    key = name.casefold()
    users = load_users()
    user = users.get(key, {"name": name, "age": age, "stream": stream, "cases_solved": 0, "correct_answers": 0, "total_answers": 0, "best_score": 0})
    user.update({"name": name, "age": age, "stream": stream})
    users[key] = user
    save_users(users)
    session["username"] = key
    session.pop("active_case", None)
    flash(f"Welcome to EDU-cRIME, {name}!", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    subjects = subjects_for_user(user)
    return render_template("dashboard.html", user=user, subjects=subjects, all_subjects=ALL_SUBJECTS)


@app.route("/case/<mode>/<path:subject>")
def choose_case(mode, subject):
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    if mode not in ("fixed", "ai"):
        flash("Unknown case type.", "error")
        return redirect(url_for("dashboard"))
    if subject not in subjects_for_user(user):
        flash("That subject is not in your selected stream.", "error")
        return redirect(url_for("dashboard"))
    try:
        return start_case(subject, mode)
    except Exception as exc:
        flash(str(exc), "error")
        return redirect(url_for("dashboard"))


@app.route("/play", methods=["GET", "POST"])
def play_case():
    user = current_user()
    active = session.get("active_case")
    if not user:
        return redirect(url_for("index"))
    if not active:
        return redirect(url_for("dashboard"))
    case = active["case"]
    index = active["index"]
    if request.method == "POST":
        choice = request.form.get("answer", "")
        if choice not in ["A", "B", "C", "D"]:
            flash("Choose one of the four answers before continuing.", "error")
            return redirect(url_for("play_case"))
        question = case["questions"][index]
        active["answers"].append({
            "choice": choice,
            "correct": choice == question["answer"],
            "question": question["question"],
            "correct_answer": question["answer"],
            "options": question["options"],
            "explanation": question["explanation"],
        })
        active["index"] += 1
        session["active_case"] = active
        if active["index"] >= len(case["questions"]):
            return redirect(url_for("results"))
        return redirect(url_for("play_case"))
    question = case["questions"][index]
    return render_template(
        "play.html", user=user, active=active, case=case, question=question,
        question_number=index + 1, total=len(case["questions"]),
        option_letters=["A", "B", "C", "D"],
    )


@app.route("/results")
def results():
    user = current_user()
    active = session.get("active_case")
    if not user:
        return redirect(url_for("index"))
    if not active or active["index"] < len(active["case"]["questions"]):
        return redirect(url_for("dashboard"))
    answers = active["answers"]
    score = sum(1 for item in answers if item["correct"])
    total = len(answers)
    if score == 3:
        rank, rank_icon = "Master Detective", "✦"
    elif score == 2:
        rank, rank_icon = "Expert Detective", "★"
    elif score == 1:
        rank, rank_icon = "Junior Detective", "◆"
    else:
        rank, rank_icon = "Rookie Detective", "◇"
    users = load_users()
    key = session.get("username")
    profile = users.get(key, {})
    # Refreshing the results page must not count the same investigation twice.
    if not active.get("recorded"):
        profile["cases_solved"] = profile.get("cases_solved", 0) + 1
        profile["correct_answers"] = profile.get("correct_answers", 0) + score
        profile["total_answers"] = profile.get("total_answers", 0) + total
        profile["best_score"] = max(profile.get("best_score", 0), score)
        users[key] = profile
        save_users(users)
        active["recorded"] = True
        session["active_case"] = active
    return render_template("results.html", user=profile, active=active, answers=answers, score=score, total=total, rank=rank, rank_icon=rank_icon)


@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    accuracy = round(100 * user.get("correct_answers", 0) / user.get("total_answers", 1)) if user.get("total_answers", 0) else 0
    return render_template("profile.html", user=user, accuracy=accuracy)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="This case file could not be found."), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html", code=500, message="Something went wrong. Please return to the dashboard and try again."), 500


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "5000")))
