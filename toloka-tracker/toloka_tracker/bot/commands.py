import re

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from toloka_tracker.toloka_api.api import get_all_messages, list_projects, number_of_unread_messages, mark_as_read, \
    get_assignment_info, accept, reply_text

a_href_pattern = r'<(a|/a).*?>'


def unread_count_command(update: Update, context: CallbackContext) -> None:
    try:
        update.message.reply_text(f'{number_of_unread_messages(None)}')
    except Exception as e:
        update.message.reply_text(f'Unable to query toloka messages! Crashed with {e}\ntg: @hotckisss')


def read_last_message_command(update: Update, context: CallbackContext) -> None:
    messages, _ = get_all_messages()
    projects_list = list_projects()
    if len(messages) == 0:
        context.bot.send_message(update.effective_chat.id, 'No messages left!')
        return

    project_id = None
    if context.args is not None and len(context.args) > 0:
        try:
            project_id = int(context.args[0])
        except:
            context.bot.send_message(update.effective_chat.id, 'Invalid project id!')
            return

    first_unread_message = messages[0]

    all_ids = []
    all_names = []
    if project_id == "OTHER":
        for project_description in projects_list:
            all_ids.append(str(project_description["id"]).lower())
            all_names.append(project_description["public_name"].lower())

            found = False
            for msg in messages:
                if not (any(project_name in msg.topic.lower() for project_name in all_names) or (
                    msg.appeal_meta is not None and msg.appeal_meta.project_id is not None and any(str(
                    msg.appeal_meta.project_id).lower() == pid for pid in all_ids))):
                    first_unread_message = msg
                    found = True
                    break

            if not found:
                update.message.reply_text('No other messages left!')
                return
    elif project_id is not None:
        project_name = ""
        for project_description in projects_list:
            if str(project_description["id"]) == str(project_id):
                project_name = project_description["public_name"].lower()

        found = False
        for msg in messages:
            if (project_name in msg.topic.lower()) or (msg.appeal_meta is not None and msg.appeal_meta.project_id is not None and str(msg.appeal_meta.project_id) == str(project_id)):
                first_unread_message = msg
                found = True
                break

        if not found:
            update.message.reply_text('No messages for proposed project left!')
            return

    show_messages_thread(first_unread_message, update, context)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Твое решение?',
        reply_markup=telegram.InlineKeyboardMarkup([
            [
                telegram.InlineKeyboardButton(
                    text=f'ОТКЛОНИТЬ И ПРОДОЛЖИТЬ!',
                    callback_data=f'REJECT_AND_CONTINUE:read_last'
                )
            ],
            [
                telegram.InlineKeyboardButton(
                    text=f'ПРИНЯТЬ И ПРОДОЛЖИТЬ!',
                    callback_data=f'ACCEPT_AND_CONTINUE:read_last'
                )
            ],
            [
                telegram.InlineKeyboardButton(
                    text=f'ИГНОРИРОВАТЬ И ПРОДОЛЖИТЬ!',
                    callback_data=f'IGNORE_AND_CONTINUE:read_last'
                )
            ]
        ]),
    )


def show_messages_thread(first_unread_message, update, context: CallbackContext):
    try:
        context.bot.send_message(update.effective_chat.id, str(first_unread_message), parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
    except:
        reply_text = first_unread_message.raw_text()
        reply_text = re.sub(a_href_pattern, "", reply_text)
        context.bot.send_message(update.effective_chat.id, reply_text)
    mark_as_read(first_unread_message.messages_thread_id)

    detected_assignment_ids = first_unread_message.extract_all_assignment_ids()
    context.bot.send_message(update.effective_chat.id, f'Detected assignments ids: {detected_assignment_ids}')

    for assignment_id in detected_assignment_ids:
        try:
            assignment_info = get_assignment_info(assignment_id)
            task_status = assignment_info.get('status')
            if task_status is None:
                task_status = "UNKNOWN"

            context.bot.send_message(update.effective_chat.id, f'Assignment: {assignment_id}, status: {task_status}')

        except Exception as e:
            print(e)


def accept_command(update: Update, context: CallbackContext) -> None:
    args = context.args

    assignment_id = args[0].split(":")[-1]
    args = args[1:]

    accept_text = " ".join(context.args[1:])

    accept(assignment_id, accept_text)
    context.bot.send_message(update.effective_chat.id, f'Success!')


def reply_text_command(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(context.args) == 0:
            update.message.reply_text("No message text provided!")
            return
        explicit_args_num = 0
        thread_id = update.effective_chat.id
        if args[0].startswith("TID:"):
            try:
                thread_id = args[0].split(":")[-1]
                if len(thread_id) == 0:
                    update.message.reply_text(f'Thread id is empty!')
                    return
                args = args[1:]
                explicit_args_num += 1
            except Exception as e:
                update.message.reply_text(f'Unable to parse thread id: {e}')
                return

        if len(args) == 0:
            update.message.reply_text("No message text provided!")
            return

        lang_code = 'RU'
        if args[0].startswith("LANG:"):
            try:
                lang_code = args[0].split(":")[-1]
                args = args[1:]
                explicit_args_num += 1
            except Exception as e:
                update.message.reply_text(f'Unable to parse lang code: {e}')
                return

        if len(args) == 0:
            update.message.reply_text("No message text provided!")
            return

        raw_text = update.effective_message.text
        raw_text_parts = raw_text.split(" ")
        raw_reply_text = " ".join(raw_text_parts[(explicit_args_num + 1):])
        lines = raw_reply_text.split("\n")
        lines = list(map(lambda l: f'<div>{l}</div>' if len(l) > 0 else "<div><br/></div>", lines))

        reply_text(thread_id, lang_code, "".join(lines))
        update.message.reply_text("Success!")
    except Exception as e:
        update.message.reply_text(f'Unable to reply! Crashed with {e}\ntg: @hotckisss')
    pass


