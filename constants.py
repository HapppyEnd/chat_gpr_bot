from util import load_prompt

# Статусы состояний
MAIN, RANDOM, GPT, TALK, QUIZ = range(5)

# Кнопки главного меню
MAIN_MENU_BUTTONS = {
    'start': 'Главное меню',
    'random': 'Узнать случайный интересный факт 🧠',
    'gpt': 'Задать вопрос чату GPT 🤖',
    'talk': 'Поговорить с известной личностью 👤',
    'quiz': 'Поучаствовать в квизе ❓'
}

# Паттерны для CallbackQueryHandler
CALLBACK_MAIN_MENU = '^main_menu'
CALLBACK_RANDOM_FACT = '^random_fact'
CALLBACK_CHANGE_PERSON = '^change_person'
CALLBACK_QUIZ_TOPIC = '^(quiz_prog|quiz_math|quiz_biology)'
CALLBACK_QUIZ_MORE = '^quiz_more'
CALLBACK_CHANGE_QUIZ_TOPIC = '^change_quiz_topic'
CALLBACK_PERSONS = '^(Cobain|Hawking|Nietzsche|Queen|Tolkien)'

# Сообщения
ERROR_MESSAGE = 'Произошла ошибка: {error}'
LOADING_MESSAGE = 'Думаю над вопросом...'
SELECT_PERSON = '🔍 Выберите личность:'
SELECT_QUIZ_TOPIC = 'Выберите тему:'
START_MESSAGE = 'main'
RANDOM_MESSAGE = 'random'
GPT_MESSAGE = 'gpt'
TALK_MESSAGE = 'talk'
QUIZ_MESSAGE = 'quiz'
RETURN_TO_MAIN = 'Вернутья в главное меню'
RANDOM_MORE = 'Хотите еще один факт?'
CHANGE_PERSON = 'Выбрать другую личность?'
CHANGE_QUIZ_TOPIC_OR_CONTINUE = 'Хотите задать ещё вопрос или сменить тему?'
NEW_QUIZ_TOPIC = 'Выберите тему:'

# Тексты кнопок
BUTTON_TEXTS = {
    'random_fact': 'Еще рандомный факт',
    'main_menu': 'Главное меню',
    'change_person': 'Выбрать другую личность',
    'change_quiz_topic': 'Сменить тему квиза',
    'quiz_more': 'Задать ещё вопрос',
}


# Константы для разговора с известными личностями
PERSONS: dict = {
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

TRANSLATE_PERSONS: dict = {
    'Cobain': 'Курт Кобейн',
    'Hawking': 'Стивен Хокинг',
    'Nietzsche': 'Фридрих Ницше',
    'Queen': 'Елизавета II',
    'Tolkien': 'Джон Толкиен'
}
# Константы для квиза
QUIZ_BUTTONS = {
    'quiz_prog': 'Программирование (Python)',
    'quiz_math': 'Математика',
    'quiz_biology': 'Биология'
}

CORRECT_ANSWER = 'Правильно!'

TRANSLATE_QUIZ_TOPICS = {
    'quiz_prog': 'Программирование',
    'quiz_math': 'Математика',
    'quiz_biology': 'Биология',
}
