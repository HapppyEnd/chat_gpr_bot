import httpx as httpx
from openai import OpenAI


class ChatGptService:
    client: OpenAI = None
    message_list: list[dict[str, str]] = None

    def __init__(self, token: str) -> None:
        token = "sk-proj-" + token[:3:-1] if token.startswith(
            'gpt:') else token
        self.client = OpenAI(
            http_client=httpx.Client(proxies="http://18.199.183.77:49232"),
            api_key=token
        )
        self.message_list = []

    async def send_message_list(self) -> str:
        """
        Отправляет список сообщений в модель и возвращает ответ.

        Returns:
            str: Ответ от модели в виде строки.
        """
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",  # gpt-4o, gpt-4-turbo, GPT-4o mini
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    def set_prompt(self, prompt_text: str) -> None:
        """
        Устанавливает системный промпт и очищает список сообщений.

        Args:
            prompt_text (str): Текст системного промпта.
        """
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        """
        Добавляет сообщение пользователя в список и получает ответ от модели.

        Args:
            message_text (str): Текст сообщения пользователя.

        Returns:
            str: Ответ от модели в виде строки.
        """
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        """
        Устанавливает системный промпт, добавляет сообщение пользователя
        и получает ответ.

        Args:
            prompt_text (str): Текст системного промпта.
            message_text (str): Текст вопроса пользователя.

        Returns:
            str: Ответ от модели в виде строки.
        """
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()
