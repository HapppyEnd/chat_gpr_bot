import logging

from telegram import Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from constants import (BUTTON_TEXTS, CALLBACK_CHANGE_PERSON,
                       CALLBACK_CHANGE_QUIZ_TOPIC, CALLBACK_MAIN_MENU,
                       CALLBACK_NEW_WORD, CALLBACK_PERSONS, CALLBACK_QUIZ_MORE,
                       CALLBACK_QUIZ_TOPIC, CALLBACK_RANDOM_FACT,
                       CHANGE_PERSON, CHANGE_QUIZ_TOPIC_OR_CONTINUE,
                       CORRECT_ANSWER, ERROR_MESSAGE, GPT, GPT_MESSAGE,
                       LOADING_MESSAGE, MAIN, MAIN_MENU_BUTTONS, NEW_WORD,
                       NEW_WORD_MESSAGE, NEW_WORD_MORE, PERSONS, QUIZ,
                       QUIZ_BUTTONS, QUIZ_MESSAGE, RANDOM, RANDOM_MESSAGE,
                       RANDOM_MORE, RETURN_TO_MAIN, SELECT_PERSON,
                       SELECT_QUIZ_TOPIC, START_MESSAGE, TALK, TALK_MESSAGE,
                       TRANSLATE_PERSONS, TRANSLATE_QUIZ_TOPICS)
from credentials import BOT_TOKEN
from gpt import ChatGptService
from util import (load_message, load_prompt, send_html, send_image,
                  send_response, send_text, send_text_buttons, show_main_menu)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

chat_gpt: ChatGptService = ChatGptService.get_instance()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает команду /start и показывает главное меню."""
    logger.info('Старт команды /start от пользователя %s',
                update.effective_user.id)
    text: str = load_message(START_MESSAGE)
    await send_response(update, context, START_MESSAGE, text)
    await show_main_menu(update, context, MAIN_MENU_BUTTONS)
    return MAIN


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отправляет пользователю рандомный факт."""
    logger.info('Запрос на рандомный факт от пользователя %s',
                update.effective_user.id)
    prompt: str = load_prompt(RANDOM_MESSAGE)
    message: str = load_message(RANDOM_MESSAGE)
    message = await send_response(update, context, RANDOM_MESSAGE, message)

    try:
        answer: str = await chat_gpt.send_question(prompt, '')
        await message.edit_text(answer)
        buttons: dict[str, str] = {
            'random_fact': BUTTON_TEXTS['random_fact'],
            'main_menu': BUTTON_TEXTS['main_menu']
        }
        await send_text_buttons(update, context, RANDOM_MORE, buttons)
        logger.info('Рандомный факт отправлен пользователю %s',
                    update.effective_user.id)
    except Exception as e:
        logger.error('Ошибка при получении рандомного факта: %s', str(e))
        await message.edit_text(ERROR_MESSAGE.format(error=str(e)))
    return RANDOM


async def random_fact(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запрос на получение еще одного рандомного факта."""
    logger.info('Пользователь %s запрашивает еще рандомный факт',
                update.effective_user.id)
    await update.callback_query.answer()
    await random(update, context)
    return RANDOM


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает команду /gpt и начинает диалог с ChatGPT."""
    logger.info('Пользователь %s вызвал команду /gpt',
                update.effective_user.id)
    prompt: str = load_prompt(GPT_MESSAGE)
    chat_gpt.set_prompt(prompt)
    message: str = load_message(GPT_MESSAGE)
    await send_response(update, context, GPT_MESSAGE, message)
    return GPT


async def gpt_dialog(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает сообщения от пользователя в режиме GPT."""
    logger.info('Обработка сообщения от пользователя %s в режиме GPT',
                update.effective_user.id)
    text: str = update.message.text
    message = await send_text(update, context, LOADING_MESSAGE)

    try:
        answer: str = await chat_gpt.add_message(text)
        await message.edit_text(answer)
        buttons: dict[str, str] = {'main_menu': BUTTON_TEXTS['main_menu']}
        await send_text_buttons(update, context, RETURN_TO_MAIN, buttons)
        logger.info('Ответ от ChatGPT отправлен пользователю %s',
                    update.effective_user.id)
    except Exception as e:
        logger.error('Ошибка при обработке сообщения GPT: %s', str(e))
        await message.edit_text(ERROR_MESSAGE.format(error=str(e)))
    return GPT


async def show_persons(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отправляет пользователю список доступных личностей для общения."""
    logger.info('Показ списка личностей пользователю %s',
                update.effective_user.id)
    await send_response(
        update, context, TALK_MESSAGE, load_message(TALK_MESSAGE))
    buttons: dict[str, str] = {name: TRANSLATE_PERSONS[name]
                               for name in PERSONS.keys()}
    await send_text_buttons(update, context, SELECT_PERSON, buttons)
    return TALK


async def select_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор личности пользователем."""
    await update.callback_query.answer()
    person: str = update.callback_query.data
    context.user_data['person'] = person
    logger.info('Пользователь %s выбрал личность %s',
                update.effective_user.id, person)
    await talk_with_person(update, context)
    return TALK


async def talk_with_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор с выбранной личностью."""
    person: str = context.user_data.get('person')

    if person:
        chat_gpt.set_prompt(PERSONS[person]['prompt'])
        image: str = f'talk_{person.lower().replace(" ", "_")}'
        try:
            await send_image(update, context, image)
            await send_text(
                update,
                context,
                f'Вы начали разговор с {TRANSLATE_PERSONS[person]}. '
                'Напишите что-нибудь!')
            logger.info('Начало разговора с личностью %s для пользователя %s',
                        person, update.effective_user.id)
        except Exception as e:
            logger.error('Ошибка при начале разговора: %s', str(e))
            await send_text(
                update, context, f'Не удалось начать разговор: {str(e)}')
    else:
        await show_persons(update, context)
    return TALK


async def change_person(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запрос пользователя на изменение личности."""
    logger.info('Пользователь %s запрашивает изменение личности',
                update.effective_user.id)
    await update.callback_query.answer()
    await show_persons(update, context)
    return TALK


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщения от пользователя в режиме разговора с
    личностью.
    """
    person: str = context.user_data.get('person')

    if person:
        user_message: str = update.message.text
        answer: str = await chat_gpt.add_message(user_message)
        await send_text(update, context, answer)
        buttons: dict[str, str] = {
            'change_person': BUTTON_TEXTS['change_person'],
            'main_menu': BUTTON_TEXTS['main_menu']
        }
        await send_text_buttons(update, context, CHANGE_PERSON, buttons)
        logger.info('Пользователь %s отправил сообщение: %s',
                    update.effective_user.id, user_message)
    else:
        await show_persons(update, context)
    return TALK


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает команду /quiz и показывает доступные темы квизов."""
    logger.info('Пользователь %s вызвал команду /quiz',
                update.effective_user.id)
    await send_response(
        update, context, QUIZ_MESSAGE, load_message(QUIZ_MESSAGE))
    await send_text_buttons(update, context, SELECT_QUIZ_TOPIC, QUIZ_BUTTONS)
    return QUIZ


async def quiz_topic_selected(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор темы квиза пользователем."""
    await update.callback_query.answer()
    chat_gpt.set_prompt(load_prompt(QUIZ_MESSAGE))
    user_message: str = update.callback_query.data
    context.user_data['quiz_topic'] = user_message
    context.user_data['correct_answers'] = 0
    answer: str = await chat_gpt.add_message(user_message)
    await send_html(update, context, answer)
    logger.info('Пользователь %s выбрал тему квиза: %s',
                update.effective_user.id, user_message)
    return QUIZ


async def handle_quiz_answer(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает ответ пользователя на вопрос квиза."""
    user_answer: str = (
        update.message.text if update.message else update.callback_query.data
    )
    if user_answer:
        try:
            answer: str = await chat_gpt.add_message(user_answer)
            if answer == CORRECT_ANSWER:
                context.user_data['correct_answers'] += 1
            await send_html(update, context, answer)
            current_score: int = context.user_data.get('correct_answers', 0)
            topic_key: str = context.user_data.get('quiz_topic')
            current_topic: str = TRANSLATE_QUIZ_TOPICS.get(topic_key)
            await send_html(
                update,
                context,
                f'Правильных ответов по теме {current_topic}: {current_score}')
            buttons: dict[str, str] = {
                'quiz_more': BUTTON_TEXTS['quiz_more'],
                'change_quiz_topic': BUTTON_TEXTS['change_quiz_topic'],
                'main_menu': BUTTON_TEXTS['main_menu']
            }
            await send_text_buttons(
                update, context, CHANGE_QUIZ_TOPIC_OR_CONTINUE, buttons)
            logger.info('Пользователь %s ответил на вопрос квиза: %s',
                        update.effective_user.id, user_answer)
        except Exception as e:
            logger.error(
                'Ошибка при обработке ответа на вопрос квиза: %s', str(e))
            await send_html(update, context, f'Произошла ошибка: {str(e)}')
    return QUIZ


async def change_quiz_topic(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запрос пользователя на изменение темы квиза."""
    logger.info('Пользователь %s запрашивает изменение темы квиза',
                update.effective_user.id)
    await update.callback_query.answer()
    await send_text_buttons(update, context, SELECT_QUIZ_TOPIC, QUIZ_BUTTONS)
    return QUIZ


async def quiz_more(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрашивает новый вопрос по текущей теме квиза."""
    await update.callback_query.answer()
    topic: str = context.user_data.get('quiz_topic')
    if topic:
        question: str = f'Задай вопрос по теме {topic}.'
        try:
            answer: str = await chat_gpt.add_message(question)
            await send_html(update, context, answer)
            logger.info(
                'Пользователь %s запрашивает еще один вопрос по теме %s',
                update.effective_user.id, topic)
        except Exception as e:
            logger.error('Ошибка при получении нового вопроса: %s', str(e))
            await send_text_buttons(
                update,
                context,
                f'Не удалось получить новый вопрос: {str(e)}', QUIZ_BUTTONS)
    else:
        await send_text_buttons(
            update, context, SELECT_QUIZ_TOPIC, QUIZ_BUTTONS)
    return QUIZ


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отправляет пользователю новое слово."""
    logger.info('Запрос на новое слово от пользователя %s',
                update.effective_user.id)

    prompt: str = load_prompt(NEW_WORD_MESSAGE)
    message: str = load_message(NEW_WORD_MESSAGE)
    message = await send_response(update, context, NEW_WORD_MESSAGE, message)

    try:
        answer: str = await chat_gpt.send_question(prompt, '')
        logger.info('Ответ от GPT: %s', answer)

        if message is not None:
            await message.edit_text(answer)
        else:
            logger.error('Сообщение не инициализировано корректно.')

        buttons: dict[str, str] = {
            'new_word': BUTTON_TEXTS['new_word'],
            'main_menu': BUTTON_TEXTS['main_menu']
        }
        await send_text_buttons(update, context, NEW_WORD_MORE, buttons)
        logger.info('Слово отправлено пользователю %s',
                    update.effective_user.id)
    except Exception as e:
        logger.error('Ошибка при получении слова: %s', str(e))
        await update.message.reply_text(ERROR_MESSAGE.format(error=str(e)))
    return NEW_WORD


async def one_more_new_word(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запрос на получение еще одного слова."""
    logger.info('Пользователь %s запрашивает новое слово',
                update.effective_user.id)
    await update.callback_query.answer()
    await new_word(update, context)
    return NEW_WORD


async def main_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возвращает пользователя в главное меню."""
    logger.info('Пользователь %s возвращается в главное меню',
                update.effective_user.id)
    await update.callback_query.answer()
    await start(update, context)
    return MAIN

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('random', random),
        CommandHandler('gpt', gpt),
        CommandHandler('talk', talk),
        CommandHandler('quiz', quiz),
        CommandHandler('new_word', new_word)
    ],
    states={
        MAIN: [
            CallbackQueryHandler(random_fact, pattern=CALLBACK_RANDOM_FACT),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU),
        ],
        RANDOM: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, random),
            CallbackQueryHandler(random_fact, pattern=CALLBACK_RANDOM_FACT),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU),
        ],
        GPT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU),
        ],
        TALK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk),
            CallbackQueryHandler(select_person, pattern=CALLBACK_PERSONS),
            CallbackQueryHandler(
                change_person, pattern=CALLBACK_CHANGE_PERSON),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU)
        ],
        QUIZ: [
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           handle_quiz_answer),
            CallbackQueryHandler(quiz_topic_selected,
                                 pattern=CALLBACK_QUIZ_TOPIC),
            CallbackQueryHandler(quiz_more, pattern=CALLBACK_QUIZ_MORE),
            CallbackQueryHandler(
                change_quiz_topic, pattern=CALLBACK_CHANGE_QUIZ_TOPIC),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU),
        ],
        NEW_WORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, new_word),
            CallbackQueryHandler(one_more_new_word, pattern=CALLBACK_NEW_WORD),
            CallbackQueryHandler(main_menu, pattern=CALLBACK_MAIN_MENU),

        ]
    },
    fallbacks=[
        CommandHandler('start', start)
    ],
    allow_reentry=True,
)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(conv_handler)
    app.run_polling()
