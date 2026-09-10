import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.services.matching_service import MatchingService
from app.telegram.keyboards import get_start_keyboard, get_action_inline_keyboard

logger = logging.getLogger(__name__)

USER_SESSIONS = {}


def get_user_session(user_id: int) -> dict:
    if user_id not in USER_SESSIONS:
        USER_SESSIONS[user_id] = {
            "jd_filename": None,
            "jd_bytes": None,
            "resumes": [],
            "last_analysis": None
        }
    return USER_SESSIONS[user_id]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_SESSIONS[user_id] = {"jd_filename": None, "jd_bytes": None, "resumes": [], "last_analysis": None}

    message_text = (
        "*ResumeMatch AI — Intelligent Recruitment Assistant*\n\n"
        "Upload your documents and I'll calculate an explainable match score.\n\n"
        "*How to use:*\n"
        "1. Upload your *Job Description* file (PDF/DOCX/TXT)\n"
        "   TIP: Add caption `jd` to the file to mark it as a JD.\n"
        "2. Upload one or more *Resume* files.\n"
        "3. Tap the *Start Analysis* button on the keyboard.\n\n"
        "Type /help for more info."
    )
    await update.message.reply_text(text=message_text, parse_mode="Markdown", reply_markup=get_start_keyboard())


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Help & Instructions*\n\n"
        "JD Upload: Send the Job Description file first, OR add caption `jd` to any file.\n"
        "Resume Upload: Send resume(s) after the JD.\n"
        "Start Analysis: Tap the Start Analysis button on the keyboard.\n"
        "Supported: PDF, DOCX, TXT (max 10MB)\n\n"
        "Commands:\n"
        "/start - Reset session\n"
        "/reset - Clear uploads and start over\n"
        "/status - Check what is uploaded\n"
        "/help - This help message"
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    jd_status = f"Uploaded: `{session['jd_filename']}`" if session["jd_filename"] else "Not uploaded"
    resume_count = len(session["resumes"])
    resume_status = f"{resume_count} resume(s) uploaded" if resume_count else "No resumes uploaded"
    await update.message.reply_text(
        f"*Session Status*\n\nJob Description: {jd_status}\nResumes: {resume_status}",
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )


async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_SESSIONS[user_id] = {"jd_filename": None, "jd_bytes": None, "resumes": [], "last_analysis": None}
    await update.message.reply_text("Session cleared! Upload a new Job Description to begin.", reply_markup=get_start_keyboard())


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_user_session(user_id)

    document = update.message.document
    if not document:
        await update.message.reply_text("Please upload a valid file.")
        return

    filename = document.file_name or "document.pdf"
    ext = filename.lower().split(".")[-1]

    if ext not in ["pdf", "docx", "txt"]:
        await update.message.reply_text("Unsupported format. Please upload PDF, DOCX, or TXT.")
        return

    tg_file = await context.bot.get_file(document.file_id)
    file_bytes = bytes(await tg_file.download_as_bytearray())

    caption = (update.message.caption or "").lower()
    is_jd = ("jd" in caption or "job" in caption or "description" in caption) or (session["jd_bytes"] is None)

    if is_jd:
        session["jd_filename"] = filename
        session["jd_bytes"] = file_bytes
        resume_count = len(session["resumes"])
        next_step = "\n\nNow upload candidate resume(s)." if resume_count == 0 else f"\n\n{resume_count} resume(s) already uploaded. Tap *Start Analysis* when ready."
        await update.message.reply_text(
            f"*Job Description received:* `{filename}`{next_step}",
            parse_mode="Markdown",
            reply_markup=get_start_keyboard()
        )
    else:
        session["resumes"].append({"filename": filename, "bytes": file_bytes})
        count = len(session["resumes"])
        await update.message.reply_text(
            f"*Resume #{count} received:* `{filename}`\n\nTap *Start Analysis* when ready!",
            parse_mode="Markdown",
            reply_markup=get_start_keyboard()
        )


GREETINGS = {"hi", "hello", "hey", "hii", "helo", "howdy", "good morning", "good afternoon", "good evening", "sup", "yo", "greetings"}

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    text_lower = text.lower()

    # Greeting detection
    if text_lower in GREETINGS or any(text_lower.startswith(g) for g in GREETINGS):
        first_name = update.effective_user.first_name or "there"
        await update.message.reply_text(
            f"Hi {first_name}! I'm ResumeMatch AI, your intelligent recruitment assistant.\n\n"
            "I can:\n"
            "- Extract skills, experience, and education from resumes\n"
            "- Compare resumes with job descriptions\n"
            "- Calculate an explainable match score\n"
            "- Identify skill gaps and eligibility\n"
            "- Recommend courses to improve your match\n\n"
            "Please upload your Resume and Job Description files to get started.\n"
            "After both files are uploaded, tap the Start Analysis button.",
            reply_markup=get_start_keyboard()
        )
        return

    if "upload jd" in text_lower:
        await update.message.reply_text("Upload your Job Description file now. Add caption `jd` to mark it.", parse_mode="Markdown")
    elif "upload resume" in text_lower:
        await update.message.reply_text("Upload your candidate resume file(s) now.")
    elif "help" in text_lower:
        await help_handler(update, context)
    elif "start analysis" in text_lower:
        await run_analysis_flow(update, context)
    elif text_lower in ["/reset", "reset"]:
        await reset_handler(update, context)
    elif text_lower in ["/status", "status"]:
        await status_handler(update, context)
    else:
        user_id = update.effective_user.id
        session = get_user_session(user_id)
        if len(text) > 80:
            if session["jd_bytes"] is None:
                session["jd_filename"] = "pasted_jd.txt"
                session["jd_bytes"] = text.encode("utf-8")
                await update.message.reply_text("Job Description text received! Now upload candidate resume(s).", reply_markup=get_start_keyboard())
            elif not session["resumes"]:
                session["resumes"].append({"filename": "pasted_resume.txt", "bytes": text.encode("utf-8")})
                await update.message.reply_text("Resume text received! Tap *Start Analysis* to proceed.", parse_mode="Markdown", reply_markup=get_start_keyboard())
            else:
                await update.message.reply_text("Files uploaded. Tap *Start Analysis* to run, or /reset to start fresh.", parse_mode="Markdown", reply_markup=get_start_keyboard())
        else:
            await update.message.reply_text("Use the keyboard buttons below, or upload your PDF/DOCX files. Type /help for instructions.", reply_markup=get_start_keyboard())


async def run_analysis_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_user_session(user_id)

    if not session["jd_bytes"]:
        await update.message.reply_text("No Job Description uploaded yet. Upload a JD file first.", reply_markup=get_start_keyboard())
        return
    if not session["resumes"]:
        await update.message.reply_text("No resumes uploaded yet. Upload at least one resume.", reply_markup=get_start_keyboard())
        return

    progress_msg = await update.message.reply_text(
        "*Analyzing candidate(s)...*\n\n"
        "Parsing documents...\n"
        "Extracting requirements...\n"
        "Matching skills and experience...\n"
        "Computing score and eligibility...",
        parse_mode="Markdown"
    )

    try:
        results = []
        for res_item in session["resumes"]:
            res = await MatchingService.analyze_candidate_against_jd(
                resume_filename=res_item["filename"],
                resume_bytes=res_item["bytes"],
                jd_filename=session["jd_filename"],
                jd_bytes=session["jd_bytes"]
            )
            results.append(res)

        results.sort(key=lambda x: x["overall_score"], reverse=True)
        session["last_analysis"] = results

        try:
            await progress_msg.delete()
        except Exception:
            pass

        for res in results:
            if res["decision"] == "SUITABLE":
                decision_icon = "GREEN CIRCLE - SUITABLE"
            elif res["decision"] == "BORDERLINE":
                decision_icon = "YELLOW CIRCLE - BORDERLINE"
            else:
                decision_icon = "RED CIRCLE - REJECT"

            matched = res.get("matched_requirements", [])
            partial = res.get("partial_requirements", [])
            missing = res.get("missing_requirements", [])
            failures = res.get("mandatory_failures", [])

            matched_text = "\n".join([f"  [YES] {m}" for m in matched]) if matched else "  None"
            partial_text = "\n".join([f"  [~] {p}" for p in partial]) if partial else "  None"
            missing_text = "\n".join([f"  [NO] {m}" for m in missing]) if missing else "  None"
            failures_text = "\n".join([f"  [FAIL] {f}" for f in failures]) if failures else "  None"

            courses = res.get("course_recommendations", [])
            if courses:
                courses_text = "\n".join([
                    f"  Gap: {c.get('gap_skill', c['skill'])}\n"
                    f"    Learning link {i+1}: {c['title']}\n"
                    f"      Platform: {c['platform']} | Level: {c['level']} | {c['duration']}\n"
                    f"      Link: {c['url']}"
                    for i, c in enumerate(courses)
                ])
            else:
                courses_text = "  No courses required"

            # -- Message 1: Score Summary --
            msg1 = (
                f"RESUME MATCH REPORT\n"
                f"====================\n\n"
                f"Candidate: {res['candidate']['name']}\n"
                f"Position:  {res['job_title']}\n\n"
                f"Role Match Score: {res['overall_score']}%\n"
                f"Decision: {decision_icon}\n\n"
                f"Score Breakdown:\n"
                f"  Skills:           {res['category_scores']['skills']}%\n"
                f"  Experience:       {res['category_scores']['experience']}%\n"
                f"  Responsibilities: {res['category_scores']['responsibilities']}%\n"
                f"  Education:        {res['category_scores']['education']}%\n\n"
                f"Mandatory Failures:\n{failures_text}"
            )
            await update.message.reply_text(text=msg1)

            # -- Message 2: Requirements Breakdown --
            msg2 = (
                f"REQUIREMENTS BREAKDOWN\n"
                f"====================\n\n"
                f"MATCHED REQUIREMENTS:\n{matched_text}\n\n"
                f"PARTIAL MATCHES:\n{partial_text}\n\n"
                f"MISSING REQUIREMENTS:\n{missing_text}"
            )
            await update.message.reply_text(text=msg2)

            # -- Message 3: Courses + Explanation --
            exp_text = res.get("explanation", "")
            msg3 = (
                f"LEARNING RECOMMENDATIONS\n"
                f"====================\n\n"
                f"{courses_text}\n\n"
                f"====================\n"
                f"Why this decision?\n\n"
                f"{exp_text}"
            )
            await update.message.reply_text(
                text=msg3,
                reply_markup=get_action_inline_keyboard()
            )

        # Keep JD loaded but clear resumes for next candidate
        session["resumes"] = []

    except Exception as e:
        logger.error(f"Analysis flow error: {e}")
        try:
            await progress_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(
            f"Analysis failed: {str(e)}\n\nTry again or type /reset to restart.",
            reply_markup=get_start_keyboard()
        )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    session = get_user_session(user_id)

    if query.data == "reset_session":
        USER_SESSIONS[user_id] = {"jd_filename": None, "jd_bytes": None, "resumes": [], "last_analysis": None}
        await query.edit_message_text("Session reset. Upload a new Job Description to begin.")

    elif query.data == "view_courses":
        if session.get("last_analysis"):
            res = session["last_analysis"][0]
            courses = res.get("course_recommendations", [])
            if courses:
                courses_text = "LEARNING PATHS FOR SKILL GAPS\n\n" + "\n\n".join(
                    [f"Gap: {c.get('gap_skill', c['skill'])}\n"
                     f"{i+1}. {c['title']}\n"
                     f"   Platform: {c['platform']}\n"
                     f"   Level: {c['level']}\n"
                     f"   Duration: {c['duration']}\n"
                     f"   Learning link: {c['url']}"
                     for i, c in enumerate(courses)]
                )
                await query.message.reply_text(courses_text, disable_web_page_preview=True)
            else:
                await query.message.reply_text("No specific courses needed for this candidate.")
