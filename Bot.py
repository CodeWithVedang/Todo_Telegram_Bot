from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

tasks = {}  # Dictionary to store tasks {user_id: [{'task': '...', 'time': '...'}]}
scheduler = BackgroundScheduler()
scheduler.start()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to To-Do Bot! Use the commands to manage your tasks:\n"
        "/add <task> <time in HH:MM format>\n"
        "/view - View tasks\n"
        "/delete <task number>\n"
        "/help - Show commands"
        "for help visit - https://github.com/CodeWithVedang/Todo_Telegram_Bot"
    )

def add_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /add <task> <time in HH:MM format>")
        return

    task = " ".join(args[:-1])
    time_str = args[-1]

    try:
        task_time = datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        update.message.reply_text("Invalid time format! Use HH:MM (24-hour).")
        return

    task_entry = {'task': task, 'time': task_time}
    tasks.setdefault(user_id, []).append(task_entry)

    update.message.reply_text(f"Task added: '{task}' at {time_str}")

    # Schedule reminder
    schedule_reminder(update.message.chat_id, task, task_time)

def view_tasks(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    user_tasks = tasks.get(user_id, [])
    if not user_tasks:
        update.message.reply_text("No tasks added yet!")
        return

    task_list = "\n".join(
        [f"{idx + 1}. {t['task']} at {t['time']}" for idx, t in enumerate(user_tasks)]
    )
    update.message.reply_text(f"Your Tasks:\n{task_list}")

def delete_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    args = context.args
    if not args:
        update.message.reply_text("Usage: /delete <task number>")
        return

    try:
        task_num = int(args[0]) - 1
        user_tasks = tasks.get(user_id, [])
        if 0 <= task_num < len(user_tasks):
            removed_task = user_tasks.pop(task_num)
            update.message.reply_text(f"Removed task: '{removed_task['task']}'")
            if not user_tasks:
                tasks.pop(user_id)
        else:
            update.message.reply_text("Invalid task number.")
    except ValueError:
        update.message.reply_text("Please provide a valid task number.")

def schedule_reminder(chat_id, task, task_time):
    now = datetime.datetime.now()
    remind_time = datetime.datetime.combine(now.date(), task_time)
    if remind_time < now:
        remind_time += datetime.timedelta(days=1)

    scheduler.add_job(
        send_reminder,
        "date",
        run_date=remind_time,
        args=[chat_id, task],
        id=f"{chat_id}_{task}"
    )

def send_reminder(chat_id, task):
    updater.bot.send_message(chat_id, text=f"Reminder: '{task}' is due!")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Commands:\n"
        "/add <task> <time in HH:MM format> - Add a task with a reminder\n"
        "/view - View all tasks\n"
        "/delete <task number> - Delete a task\n"
        "/help - Show this help message"
    )

def main():
    updater = Updater("7914084203:AAESEbbFOiJRUN0afojgXrIuxBt2_rqBe_0", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_task))
    dispatcher.add_handler(CommandHandler("view", view_tasks))
    dispatcher.add_handler(CommandHandler("delete", delete_task))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
