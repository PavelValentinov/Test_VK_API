import os
import re
from random import randrange

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from DB.database import User, City, Status, Sex, Sort, Query, DatingUser
from VK_SCOPE.conversation import hello, bye, find
from VK_SCOPE.vk_scope import VKUser


class Bot(VKUser):

    def __init__(self):
        """Инициализация бота"""
        # noinspection SpellCheckingInspection
        self.vk_bot = vk_api.VkApi(token=os.getenv("VKINDER_TOKEN"), api_version='5.124')
        # noinspection SpellCheckingInspection
        self.longpoll = VkLongPoll(self.vk_bot)
        self.users = {}

    def write_msg(self, user_id, message, attachment=None, keyboard=None):
        """Отправка сообщения пользователю"""
        values = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        if attachment:
            values['attachment'] = attachment
        if keyboard:
            values['keyboard'] = keyboard

        self.vk_bot.method('messages.send', values)

    def listen_msg(self, scan=True):
        """Ожидание сообщений от пользователя и их обработка"""

        def scan_request(event):
            """Разбор сообщений от пользователя c удалением знаков препинания, чисткой пробелов"""
            request = event.text.lower().strip()
            query = re.findall(r'([А-Яа-яЁёA-Za-z0-9]+)', request)
            if len(query) > 1:
                query = ' '.join(query)
            else:
                try:
                    query = query[0]
                except IndexError:
                    query = request
            return query

        for event in self.longpoll.listen():
            try:
                if event.user_id not in self.users:
                    self.users[event.user_id] = [VKUser(event.user_id)]
                    user = self.users[event.user_id][0]
                    if user.select_from_db(User.id, User.id == user.user_id).first() is None:
                        self.write_msg(user.user_id, f"&#128522; Привет, {user.first_name.capitalize()}!")
                    else:
                        self.write_msg(user.user_id,
                                       f"&#128522; Привет, {user.first_name.capitalize()}! Давно не виделись!")
                else:
                    user = self.users[event.user_id][0]
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        if scan is True:
                            return scan_request(event), user
                        else:
                            return event.text, user
            except AttributeError:
                pass

    def short_questionnaire(self, user, search_values):  # Smile =)
        search_values = search_values

        # город
        self.write_msg(user.user_id, f'В каком городе будем искать?\n Названия зарубежных городов, таких как Лондон '
                                     f'или Париж, должны быть написаны латиницей и полностью.\nНа всякий случай: тот самый '
                                     f'Нью-Йорк, о котором ты так много слышал, правильно пишется New York City.')
        while True:
            answer = self.listen_msg(scan=False)[0].strip().lower()

            try:
                symbol = re.search(r'\W', answer)[0]
                words = re.split(symbol, answer)
                if len(words) < 3:
                    for word in words:
                        words[words.index(word)] = word.capitalize()
                    answer = symbol.join(words)
                else:
                    if '-' == symbol:
                        words[0] = words[0].capitalize()
                        words[-1] = words[-1].capitalize()
                        answer = symbol.join(words)
                    else:
                        answer = answer.title()
            except TypeError:
                answer = answer.lower().capitalize()

            try:
                city = user.select_from_db(City.id, City.title == answer).all()
                if city is None or not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
            except IndexError:
                city = user.select_from_db(City.id, City.title == answer).first()
                if city is None or not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
        if len(city) == 1:
            search_values['city'] = city[0][0]
        elif len(city) > 1:
            self.write_msg(user.user_id, f'Нужно уточнить, город в каком именно регионе ты имеешь в виду:')
            ids = sorted([city[0] for city in city])
            regions = {}
            message = ''
            for num, id in enumerate(ids, start=1):
                region_name = user.select_from_db(City.region, City.id == id).first()[0]
                regions[str(num)] = region_name
                area = user.select_from_db(City.area, City.id == id).first()[0]
                if area:
                    message += f'{num} - {region_name}, {area}\n'
                else:
                    message += f'{num} - {region_name}\n'
            self.write_msg(user.user_id, message)
            expected_answers = [str(i) for i in range(1, len(city) + 1)]
            answer = self.listen_msg()[0].strip()
            while answer not in expected_answers:
                self.write_msg(user.user_id, f'Мне нужен один из порядковых номеров, которые ты видишь чуть выше.')
                answer = self.listen_msg()[0].strip()
            else:
                city = user.select_from_db(City.id, City.region == regions[answer]).first()[0]
                search_values['city'] = city

        # начальный возраст
        self.write_msg(user.user_id, f'Укажи минимальный возраст в цифрах.')
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id, f'Укажи минимальный возраст в ЦИФРАХ.')
            else:
                search_values['age_from'] = abs(answer)
                break

        # конечный возраст
        self.write_msg(user.user_id, f'Укажи максимальный возраст в цифрах или отправь 0, если тебе это неважно.')
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id,
                               f'Укажи максимальный возраст в ЦИФРАХ или отправь 0, если тебе это неважно.')
            else:
                if answer != 0:
                    search_values['age_to'] = abs(answer)
                else:
                    search_values['age_to'] = 100
                break

        # семейное положение
        message = ''
        db_status_names = [name[0] for name in user.select_from_db(Status.title, Status.id == Status.id).all()]
        for num, name in enumerate(db_status_names, start=1):
            message += f'{num} - {name}\n'
        self.write_msg(user.user_id, f'Какой из статусов тебя интересует:\n'
                                     f'{message}?')
        expected_answers = range(1, len(db_status_names) + 1)
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id, f'Мне нужен один из порядковых номеров, указанных выше.')
            else:
                while answer not in expected_answers:
                    self.write_msg(user.user_id, f'Мне нужен один из порядковых номеров, указанных выше.')
                    break
                else:
                    search_values['status'] = answer
                    break

        # сортировка
        message = ''
        db_sort_names = [name[0] for name in user.select_from_db(Sort.title, Sort.id == Sort.id).all()]
        for num, name in enumerate(db_sort_names, start=0):
            message += f'{num} - {name}\n'
        self.write_msg(user.user_id, f'Как отсортировать поиск:\n'
                                     f'{message}?')
        expected_answers = range(len(db_sort_names))
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id, f'Мне нужен один из номеров, указанных выше.')
            else:
                while answer not in expected_answers:
                    self.write_msg(user.user_id, f'Мне нужен один из номеров, указанных выше.')
                    break
                else:
                    search_values['sort'] = answer
                    break
        return self.search_users(user, search_values)

    def full_questionnaire(self, user, values=None):

        # пол
        if values:
            search_values = values
        else:
            search_values = {
                'city': None,
                'sex': None,
                'age_from': None,
                'age_to': None,
                'status': None,
                'sort': None,
            }

        message = ''
        db_sex_names = [name[0] for name in user.select_from_db(Sex.title, Sex.id == Sex.id).all()]
        for num, name in enumerate(db_sex_names, start=0):
            message += f'{num} - {name}\n'
        self.write_msg(user.user_id, f'Людей какого пола мы будем искать:\n'
                                     f'{message}?')
        expected_answers = range(len(db_sex_names))
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id, f'Мне нужен один из номеров, указанных выше.')
            else:
                while answer not in expected_answers:
                    self.write_msg(user.user_id, f'Мне нужен один из номеров, указанных выше.')
                    break
                else:
                    search_values['sex'] = answer
                    break
        return self.short_questionnaire(user, search_values)

    def main(self):
        """Метод общения с юзером в целях получения его требований к поиску"""

        def initial_questionnaire():
            expected_answers = ['да', 'нет']
            answer = self.listen_msg()[0].strip()
            while answer not in expected_answers:
                self.write_msg(user.user_id, '&#129300; Не понимаю... Просто скажи "да" или "нет".')
                answer = self.listen_msg()[0].strip()
            else:
                if answer == 'да':
                    self.write_msg(user.user_id, f"Какой поиск будем использовать:\n"
                                                 f"1 - стандартный или\n"
                                                 f"2 - детализированный?")
                    answer1 = self.listen_msg()[0].strip()
                    if answer1 == '1' or answer1 == "стандартный":
                        self.write_msg(user.user_id, f"&#128077; Прекрасный выбор!")
                        return self.search_users(user, search_values)
                    elif answer1 == '2' or answer1 == "детализированный":
                        self.write_msg(user.user_id,
                                       f"&#128076; Ок! Тогда тебе нужно будет ответить на несколько вопросов.")
                        return self.short_questionnaire(user, search_values)
                elif answer == 'нет':
                    return self.full_questionnaire(user, search_values)

        find_values = []
        for val in find.values():
            for item in val:
                find_values.append(item)

        query, user = self.listen_msg()
        search_values = {
            'city': user.city['id'],
            'sex': None,
            'age_from': 18,
            'age_to': 99,
            'status': 6,
            'sort': 0,
        }

        if query in hello:
            if user.sex == 2:
                search_values['sex'] = 1
                self.write_msg(user.user_id, f"Хочешь найти девушку?")
                results = initial_questionnaire()
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.')
                else:
                    self.show_results(user, results=results)
            elif user.sex == 1:
                search_values['sex'] = 2
                self.write_msg(user.user_id, f"Хочешь найти парня?")
                results = initial_questionnaire()
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.')
                else:
                    self.show_results(user, results=results)
            else:
                search_values['sex'] = 0
                self.write_msg(user.user_id, f"Кого ты хочешь найти?")
                results = self.full_questionnaire(user, search_values)
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.')
                else:
                    self.show_results(user, results=results)

        elif query in bye:
            self.write_msg(user.user_id, "Пока!")

        elif query in find_values:
            if query in find['female']:
                search_values['sex'] = 1
            elif query in find['male']:
                search_values['sex'] = 2
            elif query in find['unisex']:
                search_values['sex'] = 0
            self.write_msg(user.user_id, f"Какой поиск будем использовать:\n"
                                         f"1 - стандартный или\n"
                                         f"2 - детализированный?")
            answer = self.listen_msg()[0].strip()
            if answer == '1' or answer == "стандартный":
                self.write_msg(user.user_id, f"&#128077; Прекрасный выбор!")
                results = self.search_users(user, search_values)
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.')
                else:
                    self.show_results(user, results=results)
            elif answer == '2' or answer == "детализированный":
                self.write_msg(user.user_id, f"&#128076; Ок! Тогда тебе нужно будет ответить на несколько вопросов.")
                results = self.short_questionnaire(user, search_values)
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.')
                else:
                    self.show_results(user, results=results)
            else:
                self.write_msg(user.user_id, "&#129300; Не понимаю... Попробуй выразить свою мысль иначе.")
        elif query == "show":
            self.show_results(user)
        else:
            self.write_msg(user.user_id, "&#129300; Не понимаю... Попробуй выразить свою мысль иначе.")

    def show_results(self, user, results=None):
        if results:
            remainder = results[0] % 10
            if remainder == 0 or remainder >= 5 or (10 <= results[0] <= 19):
                var = 'вариантов'
            elif remainder == 1:
                var = 'вариант'
            else:
                var = 'варианта'
            self.write_msg(user.user_id, f'&#128515; Мы нашли {results[0]} {var}!!!')
            query_id = results[1]
        else:
            query_id = self.select_from_db(Query.id, Query.user_id == user.user_id).all()[-1][0]

        # получаем список юзеров из БД
        dating_users = self.get_datingusers_from_db(query_id)
        for d_user in dating_users:
            d_user.photos = d_user.get_photo()
            name = d_user.first_name + ' ' + d_user.last_name
            link = d_user.link
            if len(d_user.photos) > 1:
                photos_list = []
                for photo in d_user.photos:
                    photo_id, owner_id, _, _ = photo
                    photos_list.append(f'photo{owner_id}_{photo_id}')
                photos = ','.join(photos_list)
            else:
                photo_id, owner_id, _, _ = d_user.photos[0]
                photos = f'photo{owner_id}_{photo_id}'
            message = f'{name} {link} \n '

            keyboard = VkKeyboard(one_time=True)
            # keyboard = VkKeyboard(inline=True)

            keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
            keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()
            keyboard.add_button("Новый поиск", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)

            self.write_msg(user.user_id, message=message, attachment=photos)
            self.write_msg(user.user_id, message='Нравится?', keyboard=keyboard.get_keyboard())
            expected_answers = ['да', 'нет', 'новый поиск', 'отмена']
            answer = self.listen_msg()[0]
            while answer not in expected_answers:
                self.write_msg(user.user_id, "&#129300; Не понимаю... Используй кнопки.")
                answer = self.listen_msg()[0]
            else:
                if answer == "да":
                    fields = {DatingUser.viewed: True, DatingUser.black_list: False}
                    self.update_data(DatingUser.id, DatingUser.id == d_user.db_id, fields=fields)
                    continue
                elif answer == "нет":
                    fields = {DatingUser.viewed: True, DatingUser.black_list: True}
                    self.update_data(DatingUser.id, DatingUser.id == d_user.db_id, fields=fields)
                    continue
                elif answer == "новый поиск":
                    pass
                    self.full_questionnaire(user, )
                elif answer == "отмена":
                    break


def main():
    bot = Bot()
    while True:
        bot.main()


if __name__ == '__main__':
    main()
