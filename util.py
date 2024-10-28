from telegram import (BotCommand, BotCommandScopeChat, InlineKeyboardButton,
                      InlineKeyboardMarkup, MenuButtonCommands,
                      MenuButtonDefault, Message, Update)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def dialog_user_info_to_str(user_data: dict[str, str]) -> str:
    """
    Конвертирует объект user в строку.

    Args:
        user_data (dict[str, str]): Словарь с данными пользователя.

    Returns:
        str: Строка, представляющая информацию о пользователе.
    """
    mapper: dict[str, str] = {
        'language_from': 'Язык оригинала', 'language_to': 'Язык перевода',
        'text_to_translate': 'Текст для перевода'}
    return '\n'.join(map(lambda k, v: (mapper[k], v), user_data.items()))


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    """
    Посылает в чат текстовое сообщение.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении или колбэк-запросе.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        text (str): Текст сообщения для отправки.

    Returns:
        Message: Объект Message, представляющий отправленное сообщение.
    """
    if text.count('_') % 2 != 0:
        message: str = (f"Строка '{text}' является невалидной с точки зрения "
                        "markdown. Воспользуйтесь методом send_html()")
        print(message)

        if update.callback_query:
            await update.callback_query.answer()
            return await update.callback_query.message.reply_text(message)
        else:
            return await update.message.reply_text(message)

    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    chat_id: int = (
        update.callback_query.message.chat.id
        if update.callback_query
        else update.effective_chat.id
    )
    if update.callback_query:
        await update.callback_query.answer()

    return await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN
    )


async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    """
    Посылает в чат HTML сообщение.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении или колбэк-запросе.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        text (str): Текст сообщения для отправки.

    Returns:
        Message: Объект Message, представляющий отправленное сообщение.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    chat_id: int = (
        update.callback_query.message.chat.id
        if update.callback_query
        else update.effective_chat.id
    )
    if update.callback_query:
        await update.callback_query.answer()

    return await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.HTML
    )


async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            text: str, buttons: dict[str, str]) -> Message:
    """
    Посылает в чат текстовое сообщение с кнопками.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        text (str): Текст сообщения для отправки.
        buttons (dict[str, str]): Словарь с кнопками
        (ключ - callback_data, значение - текст кнопки).

    Returns:
        Message: Объект Message, представляющий отправленное сообщение.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard: list[list[InlineKeyboardButton]] = []
    for key, value in buttons.items():
        button: InlineKeyboardButton = InlineKeyboardButton(
            str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        update.effective_message.chat_id,
        text=text, reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id)


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str) -> Message:
    """
    Посылает в чат изображение.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        name (str): Имя файла изображения (без расширения).

    Returns:
        Message: Объект Message, представляющий отправленное сообщение.
    """
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         commands: dict[str, str]) -> None:
    """
    Отображает команду и главное меню.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        commands (dict[str, str]): Словарь команд (ключ - команда,
        значение - описание).
    """
    command_list: list[BotCommand] = [BotCommand(
        key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(
        chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(),
                                           chat_id=update.effective_chat.id)


async def hide_main_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Удаляет команды для конкретного чата.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
    """
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(),
                                           chat_id=update.effective_chat.id)


def load_message(name: str) -> str:
    """
    Загружает сообщение из папки /resources/messages/.

    Args:
        name (str): Имя файла сообщения (без расширения).

    Returns:
        str: Содержимое файла сообщения.
    """
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


def load_prompt(name: str) -> str:
    """
    Загружает промпт из папки /resources/prompts/.

    Args:
        name (str): Имя файла промпта (без расширения).

    Returns:
        str: Содержимое файла промпта.
    """
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


async def default_callback_handler(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатия на кнопки и отправляет ответ.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
    """
    await update.callback_query.answer()
    query: str = update.callback_query.data
    await send_html(
        update, context, f'You have pressed button with {query} callback')


async def send_response(update: Update, context: ContextTypes.DEFAULT_TYPE,
                        image: str, text: str) -> Message:
    """
    Отправляет изображение и текстовое сообщение.

    Args:
        update (Update): Объект Update, содержащий информацию о
        полученном сообщении.
        context (ContextTypes.DEFAULT_TYPE): Контекст, содержащий
        информацию о состоянии бота.
        image (str): Имя файла изображения (без расширения).
        text (str): Текст сообщения для отправки.

    Returns:
        Message: Объект Message, представляющий отправленное сообщение.
    """
    await send_image(update, context, image)
    message: Message = await send_text(update, context, text)
    return message


class Dialog:
    pass
