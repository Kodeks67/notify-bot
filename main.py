import datetime
import logging
import time

import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
# 8x#v2pMV!BfJ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <HH:MM> to set a notification")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f'Коллеги, Дейли Подключиться к DION\n'
                                                     'https://dion.vc/event/petechel\n'
                                                     'Номер для звонка с телефона\n'
                                                     '+7(495)280-03-34, доб. 2592254')


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        moscow_tz = pytz.timezone("Europe/Moscow")
        due = str(context.args[0]).split(':')
        now_ = datetime.datetime.now(moscow_tz).replace(hour=int(due[0]), minute=int(due[1]), second=00000)
        print(f'{moscow_tz} - {now_}')
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_daily(alarm, now_, chat_id=chat_id, name=str(chat_id),
                                    days=(0, 1, 2, 3, 4, 5, 6))

        text = "Notification successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <HH:MM>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Notification successfully cancelled!" if job_removed else "You have no active notification."
    await update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5419642427:AAEj2l3wqElnyFTAPApNo3RaPQsqpcZ-Hsg").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_notification))
    application.add_handler(CommandHandler("unset", unset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
