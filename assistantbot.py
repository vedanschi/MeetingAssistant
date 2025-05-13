import os
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from modules.transcribe import transcribe
from modules.summarize import summarize
from modules.search import query_faiss
from datetime import date
from pathlib import Path
import logging
from modules.search import build_faiss_index

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# --- Configuration placeholders ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler: greet the user.
    """
    await update.message.reply_text(
        "🤖 Welcome to the MeetingAssistant Bot!\n\n"
        "Key features:\n"
        "🎙 Send audio/video files for automatic transcription\n"
        "📝 Get AI-powered summaries of your meetings\n"
        "🔍 Search through past meeting notes\n\n"
        "Use /help for detailed instructions"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 *Bot Commands*\n\n"
        "📁 Send any audio message or file to:\n"
        "   1. Automatically transcribe it\n"
        "   2. Generate a summary\n"
        "   3. Add to search archive\n\n"
        "🔍 Search existing meetings by typing natural language queries\n"
        "   Example: 'What was decided about marketing last month?'\n\n"
        "⚙️ Technical notes:\n"
        "   - Supports MP3, WAV, MP4 files\n"
        "   - Processing takes 1-3 minutes depending on length"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for incoming audio or video files:
    - Downloads the file.
    - Transcribes it via whisper.cpp (transcribe).
    - "Summarizes the transcript using AI" (summarize).
    - Stores results under meetings/YYYY/MM/DD-title/.
    - Replies with the transcript and summary.
    """
    logging.info("Media file received.")
    try:
        # Show a 'typing' action while processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        # Determine the incoming media and get its File object
        file = None
        file_name = None
        caption_title = update.message.caption

        if update.message.audio:
            file = await context.bot.get_file(update.message.audio.file_id)
            file_name = update.message.audio.file_name
        elif update.message.voice:
            file = await context.bot.get_file(update.message.voice.file_id)
            file_name = None
        elif update.message.video:
            file = await context.bot.get_file(update.message.video.file_id)
            file_name = update.message.video.file_name
        else:
            await update.message.reply_text("❗ Unsupported file type. Please send an audio or video file.")
            return

        # Generate a temporary filename for the downloaded file
        temp_filename = f"temp_{file.file_id}"
        await file.download_to_drive(custom_path=temp_filename)
        logging.info(f"File downloaded to {temp_filename}.")

        # Notify the user that the file is being processed
        await update.message.reply_text("📥 File received. Processing...")


        # Compute storage paths
        # Replace in handle_media():
        slug = caption_title or file_name or "untitled"
        slug = Path(slug).stem  # Remove file extension
        slug = slug.replace(" ", "_").strip()  # Force underscores and trim
        today = date.today()
        # In handle_media():
        base = Path("meetings") / str(today.year) / f"{today:%m}" / f"{today:%d}-{slug}"
        base.mkdir(parents=True, exist_ok=True)  # This creates nested folders
        raw_dst = base / f"{slug}.raw"
        txt_dst = base / "transcript.txt"
        summ_dst = base / "summary.txt"

        # Debugging logs for paths
        logging.debug(f"Base directory: {base}")
        logging.debug(f"Raw file path: {raw_dst}")
        logging.debug(f"Transcript path: {txt_dst}")
        logging.debug(f"Summary path: {summ_dst}")

        # Ensure the base directory exists
        os.makedirs(base, exist_ok=True)
        logging.debug(f"Directory created successfully: {base}")

        # Check if the destination file exists
        if os.path.exists(raw_dst):
            os.remove(raw_dst)  # Delete the existing file

        # Rename the file
        os.rename(temp_filename, raw_dst)

        # Transcribe the file
        await update.message.reply_text("📝 Transcribing the file...")
        try:
            transcribe(str(raw_dst), str(txt_dst))
            await update.message.reply_text("📄 Summarizing the transcript...")

            # Summarize the transcript
            summarize(str(txt_dst), str(summ_dst))

            # Notify the user of success
            await update.message.reply_text(
                "✅ Processing complete! The transcript and summary have been saved."
            )
            build_faiss_index() 
            await update.message.reply_text("🔍 Search index updated.")

        except Exception as e:
            logging.error(f"Error during processing: {e}")
            await update.message.reply_text(f"❗ An error occurred: {e}")
    except Exception as e:
        logging.error(f"Error handling media: {e}")
        await update.message.reply_text(f"❗ An error occurred while processing the file: {e}")

        
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith('/'):
        return
    try:
        results = query_faiss(text, k=5)
        if results:
            # Use correct metadata fields from search.py
            reply = "\n\n".join(
                f"📅 {r['date']} - {r['slug'].replace('-', ' ').title()}\n"
                f"📝 {r['content'][:300].strip().replace(chr(10), ' ')}..."  # chr(10) is \n
                for r in results
            )
        else:
            reply = "No past meetings matched."
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Search error: {e}")
        await update.message.reply_text("❗ Search failed. Please try again.")
    except Exception as e:
        logging.error(f"Search error: {e}")
        await update.message.reply_text("❗ Search failed. Please try again.")

# Initialize the bot application
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))        

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# Add media handler
media_filter = filters.AUDIO | filters.VOICE | filters.VIDEO
application.add_handler(MessageHandler(media_filter, handle_media))

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is running...")
    application.run_polling(
        poll_interval=3,
        timeout=15
    )