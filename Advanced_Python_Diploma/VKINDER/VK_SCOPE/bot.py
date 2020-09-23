import os
import re
from random import randrange

import vk_api
# from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

# from DB.database import Query, User,  DatingUser, Photos, City, Status
from VK_SCOPE.conversation import hello, bye, find, like, dislike
from VK_SCOPE.vk_scope import VKUser


class Bot(VKUser):

    def __init__(self):
        """Инициализация бота"""
        # noinspection SpellCheckingInspection
        self.vk_bot = vk_api.VkApi(token=os.getenv("VKINDER_TOKEN"))
        # noinspection SpellCheckingInspection
        self.longpoll = VkLongPoll(self.vk_bot)
        self.users = {}

    def write_msg(self, user_id, message):
        """Отправка сообщения пользователю"""
        self.vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def listen_msg(self):
        """Ожидание сообщений от пользователя и их обработка"""
        for event in self.longpoll.listen():
            try:
                if event.user_id not in self.users:
                    self.users[event.user_id] = VKUser(event.user_id)
                user = self.users[event.user_id]
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text.lower().strip()
                        print(request)
                        query = re.findall(r'([А-Яа-яЁёA-Za-z0-9]+)', request)
                        # try:
                        if len(query) > 1:
                            query = ' '.join(query)
                        else:
                            query = query[0]
                        # except IndexError:
                        #     continue
                        if query in hello:
                            self.write_msg(event.user_id, f"Привет, {user.first_name.capitalize()}! Чем могу помочь?")
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
            except AttributeError:
                continue
            # if event.type == VkEventType.USER_OFFLINE:
            #     print(event.user_id)
            # self.ids['ids'].pop(event.user_id)
            # self.write_msg(event.user_id, f'Всего хорошего, {user.first_name.capitalize()}!')


bot = Bot()
bot.listen_msg()
