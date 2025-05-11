

import os
import re
import datetime
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Import modules from the MeetingAssistant project
from modules.transcription import transcribe
from modules.summarization import summarize
from modules.search import search

# --- Configuration placeholders ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # <-- Set your bot token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler: greet the user.
    """
    await update.message.reply_text(
        "🤖 Welcome to the MeetingAssistant Bot!\n\n"
        "Send me an audio or video file to transcribe and summarize the meeting. "
        "You can also ask me questions about past meetings by typing your query."
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for incoming audio or video files:
    - Downloads the file.
    - Transcribes it via whisper.cpp (transcribe).
    - Summarizes via orca-mini-3b (summarize).
    - Stores results under meetings/YYYY/MM/DD-title/.
    - Replies with the transcript and summary.
    """
    # Show a 'recording audio' action while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_AUDIO)

    # Determine the incoming media and get its File object
    file = None
    file_name = None
    caption_title = update.message.caption

    if update.message.audio:
        file = await context.bot.get_file(update.message.audio.file_id)
        file_name = update.message.audio.file_name  # may be None if not provided
    elif update.message.voice:
        file = await context.bot.get_file(update.message.voice.file_id)
        file_name = None  # Voice messages typically lack a filename
    elif update.message.video:
        file = await context.bot.get_file(update.message.video.file_id)
        file_name = update.message.video.file_name  # may be None
    else:
        await update.message.reply_text("❗ Unsupported file type. Please send an audio or video file.")
        return

    # Download the file to a temporary location
    temp_filename = f"temp_{file.file_id}"
    await file.download_to_drive(custom_path=temp_filename)

    # Transcribe the file (using the external transcription module)
    transcript_text = transcribe(temp_filename)

    # Summarize the transcript (using the external summarization module)
    summary_text = summarize(transcript_text)

    # Determine the meeting title from caption or filename, or use a default
    if caption_title:
        title = caption_title
    elif file_name:
        title = os.path.splitext(file_name)[0]
    else:
        title = "meeting"

    # Sanitize title to make a safe folder name (alphanumeric, underscores)
    title = re.sub(r'[^\w\s-]', '', title).strip().replace(" ", "_")

    # Build the folder path: meetings/YYYY/MM/DD-title/
    now = datetime.datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    dir_path = os.path.join("meetings", str(year), month, f"{day}-{title}")
    os.makedirs(dir_path, exist_ok=True)

    # Save transcript and summary to text files
    transcript_path = os.path.join(dir_path, "transcript.txt")
    summary_path = os.path.join(dir_path, "summary.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    # Remove the temporary downloaded file
    try:
        os.remove(temp_filename)
    except OSError:
        pass

    # Reply with the transcript and summary.
    # Split into chunks if messages exceed Telegram's limit (~4096 chars).
    transcript_message = "Transcript:\n" + transcript_text
    for i in range(0, len(transcript_message), 4000):
        await update.message.reply_text(transcript_message[i:i+4000])

    summary_message = "Summary:\n" + summary_text
    for i in range(0, len(summary_message), 4000):
        await update.message.reply_text(summary_message[i:i+4000])

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for text queries:
    - Performs a semantic search (FAISS) over past summaries using search().
    - Replies with the top matching summaries.
    """
    query = update.message.text.strip()
    if not query:
        return

    # Show typing action while searching
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Perform the semantic search on past summaries
    results = search(query)  # Expected to return a list of summary strings

    if results:
        response = "🔎 Top matching meeting summaries:\n"
        for idx, res in enumerate(results, start=1):
            snippet = res.strip()
            # Truncate long summaries for the reply
            if len(snippet) > 500:
                snippet = snippet[:500].rsplit(" ", 1)[0] + "..."
            response += f"\n{idx}. {snippet}\n"
    else:
        response = "No matching summaries found for your query."

    await update.message.reply_text(response)

def main():
    # Initialize the Telegram bot application
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))

    # Handler for media files: audio, voice, video
    media_filter = filters.AUDIO | filters.VOICE | filters.VIDEO
    app.add_handler(MessageHandler(media_filter, handle_media))

    # Handler for text queries (ignore bot commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
