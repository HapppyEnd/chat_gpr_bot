from util import load_prompt

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
