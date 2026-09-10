from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_start_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["📄 Upload JD", "👤 Upload Resume"],
        ["⚡ Start Analysis", "❓ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_action_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📊 View Full Report", callback_data="view_report"),
            InlineKeyboardButton("📚 Learning Path", callback_data="view_courses")
        ],
        [
            InlineKeyboardButton("🔄 New Session", callback_data="reset_session")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
