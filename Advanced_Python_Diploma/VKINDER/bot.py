import os
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from VKINDER.vk_scope import VKUser, DatingUser


class Bot:
    def __init__(self, username: str, password: str):
        """Инициализация бота"""
        self.vk_bot = vk_api.VkApi(token=os.getenv("VKINDER_TOKEN"))
        self.longpoll = VkLongPoll(self.vk_bot)
        self.session = VKUser(username, password)
        self.vk = self.session.vk

    def write_msg(self, user_id, message):
        """Отправка сообщения пользователю"""
        self.vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def listen_msg(self):
        """Ожидание сообщений от пользователя и их обработка"""
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                name = self.vk.users.get(user_id=event.user_id, v='5.120')[0]['first_name']
                if event.to_me:
                    request = event.text.lower().strip()
                    if request == "привет":
                        self.write_msg(event.user_id, f"Хай, {name.capitalize()}")
                    elif request == "пока":
                        self.write_msg(event.user_id, "Пока((")
                    else:
                        self.write_msg(event.user_id, "Не поняла вашего ответа...")


bot = Bot(os.getenv("VK_USER_LOGIN"), os.getenv("VK_USER_PASS"))
bot.listen_msg()
