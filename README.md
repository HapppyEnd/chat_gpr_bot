# AI Ассистент для Telegram

## Описание

Этот проект представляет собой Telegram-бота, который использует ChatGPT для взаимодействия с пользователями. Бот предоставляет различные функции, включая случайные факты, диалоги с личностями, викторины и изучение новых слов.

## Функциональность

1. **Команда `/start`**: Запускает бота и показывает главное меню.
2. **Команда `/random`**: Отправляет пользователю случайный факт.
3. **Команда `/gpt`**: Начинает диалог с ChatGPT.
4. **Команда `/talk`**: Позволяет пользователю общаться с выбранной личностью.
5. **Команда `/quiz`**: Предлагает пользователю выбрать тему викторины и отвечает на вопросы.
6. **Команда `/new_word`**: Отправляет пользователю новое слово для изучения.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/HapppyEnd/chat_gpt_bot.git
   ```

2. Перейдите в директорию проекта:

   ```bash
   cd chat_gpt_bot
   ```

3. Установите необходимые библиотеки из файла `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл .env в корневой директории проекта и добавьте ваши токены:

    ```bash
    BOT_TOKEN=ваш_токен_бота
    ChatGPT_TOKEN=ваш_токен
    ```
5. Убедитесь, что файл .env загружается в вашем коде с помощью 
`load_dotenv().`

6. Настройте `gpt.py` для работы с ChatGPT, если это необходимо.

## Использование OpenAI

В проекте используется класс `ChatGptService`, который взаимодействует с моделью ChatGPT через API OpenAI. Этот класс управляет отправкой сообщений и получением ответов от модели, обеспечивая пользователям возможность общения с ChatGPT.

## Запуск

Запустите бота с помощью следующей команды:

```bash
python bot.py
```

## Логирование

Логи бота будут выводиться в консоль. Вы можете изменить уровень логирования в функции `basicConfig`.

## Использование

После запуска бота вы можете начать взаимодействовать с ним через Telegram, используя команды, указанные выше.


Этот файл содержит всю необходимую информацию о проекте, его установке, функциональности и использовании.