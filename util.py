from telegram import (BotCommand, BotCommandScopeChat, InlineKeyboardButton,
                      InlineKeyboardMarkup, MenuButtonCommands,
                      MenuButtonDefault, Message, Update)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def dialog_user_info_to_str(user_data: dict) -> str:
    """
    Конвертирует объект user в строку.

    :param user_data: Словарь с данными пользователя.
    :return: Строка, представляющая информацию о пользователе.
    """
    mapper = {
        'language_from': 'Язык оригинала', 'language_to': 'Язык перевода',
        'text_to_translate': 'Текст для перевода'}
    return '\n'.join(map(lambda k, v: (mapper[k], v), user_data.items()))


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    """
    Посылает в чат текстовое сообщение.

    :param update: Объект Update, содержащий информацию о полученном
                   сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    :param text: Текст сообщения для отправки.
    :return: Объект Message, представляющий отправленное сообщение.
    """
    if text.count('_') % 2 != 0:
        message = (f"Строка '{text}' является невалидной с точки зрения "
                   "markdown. Воспользуйтесь методом send_html()")
        print(message)
        return await update.message.reply_text(message)

    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text,
                                          parse_mode=ParseMode.MARKDOWN)


async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    """
    Посылает в чат HTML сообщение.

    :param update: Объект Update, содержащий информацию о полученном
                   сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    :param text: Текст сообщения для отправки.
    :return: Объект Message, представляющий отправленное сообщение.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text, parse_mode=ParseMode.HTML)


async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            text: str, buttons: dict) -> Message:
    """
    Посылает в чат текстовое сообщение с кнопками.

    :param update: Объект Update, содержащий информацию о полученном
                   сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    :param text: Текст сообщения для отправки.
    :param buttons: Словарь с кнопками (
                    ключ - callback_data, значение - текст кнопки).
    :return: Объект Message, представляющий отправленное сообщение.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        update.effective_message.chat_id,
        text=text, reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id)


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str) -> Message:
    """
    Посылает в чат изображение.

    :param update: Объект Update, содержащий информацию о полученном сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    :param name: Имя файла изображения (без расширения).
    :return: Объект Message, представляющий отправленное сообщение.
    """
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         commands: dict) -> None:
    """
    Отображает команду и главное меню.

    :param update: Объект Update, содержащий информацию о полученном сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    :param commands: Словарь команд (ключ - команда, значение - описание).
    """
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(
        chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(),
                                           chat_id=update.effective_chat.id)


async def hide_main_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Удаляет команды для конкретного чата.

    :param update: Объект Update, содержащий информацию о полученном сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    """
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(),
                                           chat_id=update.effective_chat.id)


def load_message(name: str) -> str:
    """
    Загружает сообщение из папки /resources/messages/.

    :param name: Имя файла сообщения (без расширения).
    :return: Содержимое файла сообщения.
    """
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


def load_prompt(name: str) -> str:
    """
    Загружает промпт из папки /resources/prompts/.

    :param name: Имя файла промпта (без расширения).
    :return: Содержимое файла промпта.
    """
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


async def default_callback_handler(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатия на кнопки и отправляет ответ.

    :param update: Объект Update, содержащий информацию о полученном сообщении.
    :param context: Контекст, содержащий информацию о состоянии бота.
    """
    await update.callback_query.answer()
    query = update.callback_query.data
    await send_html(
        update, context, f'You have pressed button with {query} callback')


class Dialog:
    pass
