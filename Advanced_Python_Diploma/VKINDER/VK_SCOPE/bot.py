import os
import re
from random import randrange

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from VK_SCOPE.conversation import hello, bye, find, like, dislike
from VK_SCOPE.vk_scope import VKUser


class Bot(VKUser):

    def __init__(self):
        """Инициализация бота"""
        self.vk_bot = vk_api.VkApi(token=os.getenv("VKINDER_TOKEN"))
        self.longpoll = VkLongPoll(self.vk_bot)

    def write_msg(self, user_id, message):
        """Отправка сообщения пользователю"""
        self.vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def listen_msg(self):
        """Ожидание сообщений от пользователя и их обработка"""
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                name = self.get_self_name(event.user_id)
                if event.to_me:
                    request = event.text.lower().strip()
                    query = re.findall(r'([А-яЁё]+)', request)
                    if len(query) > 1:
                        query = ' '.join(query)
                    else:
                        query = query[0]
                    if query in hello:
                        self.write_msg(event.user_id, f"Привет, {name.capitalize()}! Чем могу помочь?")
                        keyboard = VkKeyboard(one_time=True)

                        keyboard.add_button('Белая кнопка', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)

                        keyboard.add_line()  # Переход на вторую строку
                        keyboard.add_location_button()

                        keyboard.add_line()
                        keyboard.add_vkpay_button(hash="action=transfer-to-group&group_id=74030368&aid=6222115")

                        keyboard.add_line()
                        keyboard.add_vkapps_button(app_id=7595057,
                                                   owner_id=604152544,
                                                   label="Отправить клавиатуру",
                                                   hash="sendKeyboard")

                    elif query in bye:
                        self.write_msg(event.user_id, "Пока((")
                    elif query in find:
                        self.write_msg(event.user_id, self.search_users())
                        if query in like:
                            pass
                        elif query in dislike:
                            pass
                        else:
                            self.write_msg(event.user_id, "Не понимаю вашего ответа...")
                    else:
                        self.write_msg(event.user_id, "Не понимаю вашего ответа...")


bot = Bot()
bot.listen_msg()
