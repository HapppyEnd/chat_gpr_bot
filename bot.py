from telegram import Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)

from constants import (CORRECT_ANSWER, PERSONS, QUIZ_BUTTONS,
                       TRANSLATE_PERSONS, TRANSLATE_QUIZ_TOPICS)
from credentials import BOT_TOKEN, ChatGPT_TOKEN
from gpt import ChatGptService
from util import (Dialog, default_callback_handler, load_message, load_prompt,
                  send_html, send_image, send_response, send_text,
                  send_text_buttons, show_main_menu)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    Отправляет пользователю приветственное сообщение и главное меню.
    """
    dialog.mode = 'main'
    text: str = load_message('main')
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
    Отправляет случайный интересный факт пользователю.
    """
    dialog.mode = 'random'
    prompt: str = load_prompt('random')
    message: str = load_message('random')
    message = await send_response(update, context, 'random', message)

    try:
        answer: str = await chat_gpt.send_question(prompt, '')
        await message.edit_text(answer)
        buttons: dict[str, str] = {'random_fact': 'Еще рандомный факт'}
        await send_text_buttons(
            update, context, 'Хотите еще один факт?', buttons)

    except Exception as e:
        await message.edit_text(f'Произошла ошибка: {str(e)}')


async def random_fact(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик для кнопки "Еще рандомный факт".
    Вызывает повторное выполнение функции random для получения нового факта.
    """
    await update.callback_query.answer()
    await random(update, context)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /gpt.
    Настраивает режим бота на общение с ChatGPT и отправляет
    соответствующее сообщение.
    """
    dialog.mode = 'gpt'
    prompt: str = load_prompt('gpt')
    chat_gpt.set_prompt(prompt)
    message: str = load_message('gpt')
    await send_response(update, context, 'gpt', message)


async def gpt_dialog(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений в режиме диалога с ChatGPT.
    Отправляет введенное сообщение в ChatGPT и возвращает ответ пользователю.
    """
    text: str = update.message.text
    message = await send_text(update, context, 'Думаю над вопросом...')

    try:
        answer: str = await chat_gpt.add_message(text)
        await message.edit_text(answer)
    except Exception as e:
        await message.edit_text(f'Произошла ошибка: {str(e)}')


async def show_persons(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает пользователю выбор личностей для разговора.
    Отправляет список доступных личностей и кнопки для выбора.
    """
    await send_response(update, context, 'talk', load_message('talk'))
    buttons: dict[str, str] = {name: TRANSLATE_PERSONS[name]
                               for name in PERSONS.keys()}
    await send_text_buttons(update, context, '🔍 Выберите личность:', buttons)


async def select_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает выбор личности пользователем.
    Сохраняет выбранную личность и переходит в режим разговора с ней.
    """
    await update.callback_query.answer()
    person: str = update.callback_query.data
    context.user_data['person'] = person
    dialog.mode = 'talk'
    await talk_with_person(update, context)


async def talk_with_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Начинает разговор с выбранной личностью.
    Отправляет изображение и сообщение, информирующее пользователя о
    начале разговора.
    """
    person: str = context.user_data.get('person')

    if person:
        chat_gpt.set_prompt(PERSONS[person]['prompt'])
        image: str = f'talk_{person.lower().replace(" ", "_")}'
        await send_image(update, context, image)
        await send_text(
            update, context,
            f'Вы начали разговор с {TRANSLATE_PERSONS[person]}. '
            'Напишите что-нибудь!')
    else:
        await show_persons(update, context)


async def change_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает запрос на изменение личности.
    Возвращает пользователя к списку доступных личностей для выбора.
    """
    await update.callback_query.answer()
    await show_persons(update, context)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения в режиме разговора с личностью.
    Отправляет сообщение пользователю и предлагает выбрать другую личность.
    """
    person: str = context.user_data.get('person')

    if person:
        user_message: str = update.message.text
        answer: str = await chat_gpt.add_message(user_message)
        await send_text(update, context, answer)
        buttons: dict[str, str] = {'change_person': 'Выбрать другую личность'}
        await send_text_buttons(
            update, context, 'Выбрать другую личность?', buttons)
    else:
        await show_persons(update, context)


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /quiz.
    Отправляет сообщение с инструкциями и кнопками для выбора темы квиза.
    """
    dialog.mode = 'quiz'
    await send_response(update, context, 'quiz', load_message('quiz'))
    await send_text_buttons(update, context, 'Выберите тему:', QUIZ_BUTTONS)


async def quiz_topic_selected(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает выбор темы квиза.
    Сохраняет выбранную тему и отправляет первый вопрос по ней.
    """
    await update.callback_query.answer()
    chat_gpt.set_prompt(load_prompt('quiz'))
    user_message: str = update.callback_query.data
    context.user_data['quiz_topic'] = user_message
    context.user_data['correct_answers'] = 0
    answer: str = await chat_gpt.add_message(user_message)
    await send_html(update, context, answer)


async def handle_quiz_answer(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает ответ пользователя на вопрос квиза.
    Проверяет правильность ответа и отправляет результат пользователю.
    """
    user_answer: str = (
        update.message.text if update.message else update.callback_query.data
    )
    if user_answer:
        answer: str = await chat_gpt.add_message(user_answer)
        if answer == CORRECT_ANSWER:
            context.user_data['correct_answers'] += 1
        await send_html(update, context, answer)
        current_score: int = context.user_data.get('correct_answers', 0)
        topic_key: str = context.user_data.get('quiz_topic')
        current_topic: str = TRANSLATE_QUIZ_TOPICS.get(topic_key)
        await send_html(
            update, context,
            f'Правильных ответов по теме {current_topic}: {current_score}')
        buttons: dict[str, str] = {'quiz_more': 'Задать ещё вопрос',
                                   'change_quiz_topic': 'Сменить тему квиза'}
        await send_text_buttons(
            update, context, 'Хотите задать ещё вопрос или сменить тему?',
            buttons)


async def change_quiz_topic(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает запрос на изменение темы квиза.
    Возвращает пользователя к списку доступных тем для выбора.
    """
    await update.callback_query.answer()
    await send_text_buttons(
        update, context, 'Выберите новую тему:', QUIZ_BUTTONS)


async def quiz_more(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает запрос на получение ещё одного вопроса по текущей теме квиза.
    Отправляет новый вопрос пользователю.
    """

    await update.callback_query.answer()
    topic: str = context.user_data.get('quiz_topic')
    if topic:
        question: str = f"Задай вопрос по теме {topic}."
        answer: str = await chat_gpt.add_message(question)
        await send_html(update, context, answer)
    else:
        await send_text_buttons(
            update, context, 'Выберите тему:', QUIZ_BUTTONS)


async def text_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений. Определяет режим работы бота
    и вызывает соответствующий обработчик.
    """
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'talk':
        await talk(update, context)
    elif dialog.mode == 'quiz':
        await handle_quiz_answer(update, context)
    else:
        await start(update, context)


dialog: Dialog = Dialog()
dialog.mode = None
chat_gpt: ChatGptService = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(random_fact, pattern='^random_fact$'))
app.add_handler(CallbackQueryHandler(
    select_person, pattern='^(Cobain|Hawking|Nietzsche|Queen|Tolkien)$'))
app.add_handler(CallbackQueryHandler(
    change_person, pattern='^change_person$'))
app.add_handler(CallbackQueryHandler(
    quiz_topic_selected, pattern='^(quiz_prog|quiz_math|quiz_biology)$'))
app.add_handler(CallbackQueryHandler(quiz_more, pattern='^quiz_more$'))
app.add_handler(CallbackQueryHandler(
    change_quiz_topic, pattern='^change_quiz_topic$'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
