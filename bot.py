from telegram import Message, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)

from credentials import BOT_TOKEN, ChatGPT_TOKEN
from gpt import ChatGptService
from util import (Dialog, default_callback_handler, load_message, load_prompt,
                  send_image, send_text, send_text_buttons, show_main_menu)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    """
    dialog.mode = 'main'
    text = load_message('main')
    await send_response(update, context, 'main', text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /random.
    """
    dialog.mode = 'random'
    prompt = load_prompt('random')
    message = load_message('random')
    message = await send_response(update, context, 'random', message)

    try:
        answer = await chat_gpt.send_question(prompt, '')
        await message.edit_text(answer)
        buttons = {'random_fact': 'Еще рандомный факт'}
        await send_text_buttons(
            update, context, 'Хотите еще один факт?', buttons)

    except Exception as e:
        await message.edit_text(f'Произошла ошибка: {str(e)}')


async def random_fact(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик для инлайн-кнопки "Еще рандомный факт".
    """
    await update.callback_query.answer()
    await random(update, context)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /gpt.
    """
    dialog.mode = 'gpt'
    prompt = load_prompt('gpt')
    chat_gpt.set_prompt(prompt)
    message = load_message('gpt')
    await send_response(update, context, 'gpt', message)


async def gpt_dialog(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений в режиме диалога с ChatGPT.
    """
    text = update.message.text
    message = await send_text(update, context, 'Думаю над вопросом...')

    try:
        answer = await chat_gpt.add_message(text)
        await message.edit_text(answer)
    except Exception as e:
        await message.edit_text(f'Произошла ошибка: {str(e)}')


async def send_response(update: Update, context: ContextTypes.DEFAULT_TYPE,
                        image_key: str, text: str) -> Message:
    """
    Отправляет изображение и текстовое сообщение.
    """
    await send_image(update, context, image_key)
    message = await send_text(update, context, text)
    return message


persons: dict = {
    'Cobain': {
        'prompt': load_prompt('talk_cobain')
    },
    'Hawking': {
        'prompt': load_prompt('talk_hawking')
    },
    'Nietzsche': {
        'prompt': load_prompt('talk_nietzsche')
    },
    'Queen': {
        'prompt': load_prompt('talk_queen')
    },
    'Tolkien': {
        'prompt': load_prompt('talk_tolkien')
    },
}

translate_persons: dict = {
    'Cobain': 'Курт Кобейн',
    'Hawking': 'Стивен Хокинг',
    'Nietzsche': 'Фридрих Ницше',
    'Queen': 'Елизавета II',
    'Tolkien': 'Джон Толкиен'
}


async def show_persons(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает пользователю выбор личностей для разговора.
    """
    await send_response(update, context, 'talk', load_message('talk'))
    buttons = {name: translate_persons[name]
               for name in persons.keys()}
    await send_text_buttons(update, context, '🔍 Выберите личность:', buttons)


async def select_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает выбор личности пользователем.
    """
    await update.callback_query.answer()
    person = update.callback_query.data
    context.user_data['person'] = person
    dialog.mode = 'talk'
    await talk_with_person(update, context)


async def talk_with_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Начинает разговор с выбранной личностью.
    """
    person = context.user_data.get('person')

    if person:
        chat_gpt.set_prompt(persons[person]['prompt'])
        image_key = f'talk_{person.lower().replace(" ", "_")}'
        await send_image(update, context, image_key)
        await send_text(
            update, context,
            f'Вы начали разговор с {translate_persons[person]}. '
            'Напишите что-нибудь!')
    else:
        await show_persons(update, context)


async def change_personality(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает запрос на изменение личности.
    """
    await update.callback_query.answer()
    await show_persons(update, context)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения в режиме разговора с личностью.
    """
    person = context.user_data.get('person')

    if person:
        user_message = update.message.text
        answer = await chat_gpt.add_message(user_message)
        await send_text(update, context, answer)
        buttons = {'change_personality': 'Выбрать другую личность'}
        await send_text_buttons(
            update, context, 'Выбрать другую личность?', buttons)
    else:
        await show_persons(update, context)


async def text_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений. Определяет режим работы бота.
    """
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'talk':
        await talk(update, context)
    else:
        await start(update, context)


dialog = Dialog()
dialog.mode = None
chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(random_fact, pattern='^random_fact$'))
app.add_handler(CallbackQueryHandler(select_person,
                pattern='^(Cobain|Hawking|Nietzsche|Queen|Tolkien)$'))
app.add_handler(CallbackQueryHandler(
    change_personality, pattern='^change_personality$'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
