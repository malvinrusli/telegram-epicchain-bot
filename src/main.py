import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from rag_engine import search_kb, init_collection, ingest_knowledge_base
from agent import EpicAgent

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Agent
agent = EpicAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am the EpicChain FAQ Agent. Ask me anything in the group!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main message handler for group chats."""
    # Only process if it's a text message
    if not update.message.text:
        return

    message_text = update.message.text
    username = update.message.from_user.username or update.message.from_user.first_name
    
    # Mention-Only Logic: Only reply if tagged or if it's a reply to the bot
    bot_user = await context.bot.get_me()
    is_mention = f"@{bot_user.username}" in message_text
    is_reply_to_me = (
        update.message.reply_to_message 
        and update.message.reply_to_message.from_user.id == bot_user.id
    )

    if not (is_mention or is_reply_to_me):
        return

    logger.info(f"Processing mentioned message from {username}: {message_text}")

    # Clean the message text from the mention for cleaner KB search
    clean_text = message_text.replace(f"@{bot_user.username}", "").strip()

    # 1. Search Knowledge Base for context
    kb_context = search_kb(clean_text)
    
    # 2. Process with Agent
    response_text = agent.process_message(username, clean_text, kb_context)
    
    if response_text:
        # Tagging is already handled in agent.py
        await update.message.reply_text(response_text)
    else:
        logger.info(f"Message from {username} ignored (not a question).")

def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env!")
        return

    # Initialize KB on startup
    init_collection()
    kb_path = os.path.join(os.path.dirname(__file__), "../knowledge-base.md")
    ingest_knowledge_base(kb_path)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non-command messages - check if it's a question
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
