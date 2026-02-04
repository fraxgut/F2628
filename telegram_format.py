import re


def sanitize_telegram_html(message):
    """
    Converts common Markdown emphasis into Telegram-safe HTML and strips
    remaining Markdown markers. This is a defensive guardrail because LLMs
    occasionally ignore formatting constraints.
    """
    if not message:
        return message

    text = message.replace("\r\n", "\n")

    # Bold+italic (***text*** or ___text___) first.
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"___(.+?)___", r"<b><i>\1</i></b>", text)

    # Bold.
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)

    # Italic.
    text = re.sub(r"(?<!\\)\*(?!\s)(.+?)(?<!\s)\*", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\\)_(?!\s)(.+?)(?<!\s)_", r"<i>\1</i>", text)

    # Strip common Markdown line prefixes.
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*•]+\s+", "", text)

    # Remove code fences/backticks and any remaining emphasis markers.
    text = text.replace("```", "")
    text = text.replace("`", "")
    text = text.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    text = text.replace("#", "")

    return text.strip()
