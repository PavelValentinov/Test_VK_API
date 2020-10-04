""" Модуль бота Вконтакте, отвечающий за:
    - сценарий общения бота с пользователем,
    - формирование запросов на поиск,
    - направление результатов поиска на обработку,
    - выдачу пользователю результатов."""

import os
import re
from datetime import datetime
from random import randrange
from typing import Dict, Any, Tuple, List

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from DB.database import User, City, Status, Sex, Sort, Query, DatingUser, Country, Region, Connect
from VK_SCOPE.vk_scope import VKUser, VKDatingUser, VKAuth


# noinspection SpellCheckingInspection
class Bot(VKAuth, Connect):
    def __init__(self):
        # noinspection SpellCheckingInspection
        # FIXME: укажите Ваш токен сообщества (группы) Вконтакте вместо os.getenv("VKINDER_TOKEN")
        TOKEN = os.getenv("VKINDER_TOKEN")
        self.vk_bot = vk_api.VkApi(token=TOKEN, api_version='5.124')
        # noinspection SpellCheckingInspection
        self.longpoll = VkLongPoll(self.vk_bot)
        self.empty_keyboard = VkKeyboard().get_empty_keyboard()
        self.users = {}

    def _check_city_and_region(self, user) -> None:
        """Метод проверки наличия города и региона в БД. При отсутствии - собираем и дописываем"""

        if not self.select_from_db(City.id, City.id == user.city['id']).first():
            city, region = self._get_city(user.country['id'], user.city['title'])
            if not self.select_from_db(Region.id, Region.id == region['id']).first():
                self.insert_to_db(Region, region)
            self.insert_to_db(City, city)

    def _get_region(self, country_id: int, region_title: str) -> Dict[str, Any]:
        """Метод для поиска региона юзера, если его вдруг нет в БД"""
        search_values = {'country_id': country_id, 'q': region_title}
        return self.vk_session.method('database.getRegions', values=search_values)

    def _get_city(self, country_id: int, city_title: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Метод для поиска города юзера, если его вдруг нет в БД"""
        search_values = {'country_id': country_id, 'q': city_title, 'need_all': 1}
        city = self.vk_session.method('database.getCities', values=search_values)
        city_items = city['items'][0]
        region_title = city_items['region'].split()[0]
        region = self._get_region(country_id, region_title)
        region_items = region['items'][0]
        region_items.update({'country_id': country_id})
        city_items['region_id'] = region_items['id']
        return city_items, region_items

    def write_msg(self, user_id, message, attachment=None, keyboard=None) -> None:
        """Отправка сообщения пользователю"""
        values = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        if attachment:
            values['attachment'] = attachment
        if keyboard:
            values['keyboard'] = keyboard

        self.vk_bot.method('messages.send', values)

    def listen_msg(self, scan=True) -> Tuple:
        """Ожидание сообщений от пользователя и их обработка.
        Метод отслеживает события в VKLongPoll и при первом событии от юзера инициализирует его экземпляр VKUser"""

        def scan_request(event) -> str:
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
                    self.users[event.user_id] = VKUser(event.user_id)
                    user = self.users[event.user_id]

                    keyboard = VkKeyboard(one_time=False)

                    check_user = user.select_from_db(User.id, User.id == user.user_id).first()

                    if not check_user:
                        user.insert_self_to_db()

                        keyboard.add_button("Привет", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)

                        self.write_msg(user.user_id, f"&#128522; Привет, {user.first_name.capitalize()}!",
                                       keyboard=keyboard.get_keyboard())

                    else:
                        check_query = user.select_from_db(Query.id, Query.user_id == user.user_id).all()
                        if not check_query:

                            keyboard.add_button("Привет", color=VkKeyboardColor.PRIMARY)
                            keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)

                            self.write_msg(user.user_id,
                                           f"&#128522; Привет, {user.first_name.capitalize()}! Давно не виделись!",
                                           keyboard=keyboard.get_keyboard())
                        else:
                            keyboard.add_button("Привет", color=VkKeyboardColor.POSITIVE)
                            keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)
                            keyboard.add_line()
                            keyboard.add_button(f"Результаты последнего поиска", color=VkKeyboardColor.PRIMARY)
                            keyboard.add_line()
                            keyboard.add_button(f"Все лайкнутые", color=VkKeyboardColor.POSITIVE)
                            keyboard.add_button(f"Все непонравившиеся", color=VkKeyboardColor.NEGATIVE)
                            self.write_msg(user.user_id,
                                           f"&#128522; Привет, {user.first_name.capitalize()}! Давно не виделись!",
                                           keyboard=keyboard.get_keyboard())
                else:
                    user = self.users[event.user_id]
                    self._check_city_and_region(user)

                    # проверяем не поменялся ли у юзера его город
                    user_db_city = self.select_from_db(User.city_id, User.id == user.user_id).first()[0]
                    if user_db_city != user.city['id']:
                        self._check_city_and_region(user)  # если нового города юзера вдруг нет в БД
                        self.update_data(User.id, User.id == user.user_id, {User.city_id: user.city['id']})

                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        if scan is True:
                            return scan_request(event), user
                        else:
                            return event.text, user
            except AttributeError:
                pass

    def short_questionnaire(self, user, values) -> Tuple[int, int] or int:  # Smile =)
        """ "Краткий" пошаговый опросник пользователя для поиска подходящих юзеров:
            - город,
            - начальный возраст,
            - конечный возраст,
            - статус,
            - порядов сортировки результатов."""

        search_values = values

        # город
        self.write_msg(user.user_id, f'В каком городе будем искать?\n\nНазвания зарубежных городов, таких как Лондон '
                                     f'или Париж, должны быть написаны латиницей и полностью.\n\nНа всякий случай: '
                                     f'тот самый Нью-Йорк, о котором все так много слышали, правильно пишется '
                                     f'New York City.',
                       keyboard=cancel_button())
        while True:
            answer = self.listen_msg(scan=False)[0].strip().lower()
            if answer == "отмена":
                return -1
            else:
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
                    answer = answer.capitalize()

            try:
                city = user.select_from_db(City.id, City.title == answer).order_by(City.region).all()
                if not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
            except IndexError:
                city = user.select_from_db(City.id, City.title == answer).first()
                if not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
        if len(city) == 1:
            search_values['city'] = city[0][0]
        elif len(city) > 1:
            self.write_msg(user.user_id, f'Нужно уточнить, город в каком именно регионе ты имеешь в виду:')
            ids = [city[0] for city in city]
            regions = {}
            message = ''
            for num, id in enumerate(ids, start=1):
                regions[str(num)] = id

                region_name, region_id, area = user.select_from_db((City.region, City.region_id, City.area),
                                                                   City.id == id).first()
                country = user.select_from_db(Country.title, Region.id == region_id,
                                              join=(Region, Country.id == Region.country_id)).first()[0]
                if area:
                    message += f'{num} - {region_name}, {area} ({country})\n'
                else:
                    message += f'{num} - {region_name} ({country})\n'
            self.write_msg(user.user_id, message)
            expected_answers = [str(i) for i in range(1, len(city) + 1)]
            answer = self.listen_msg()[0].strip()
            expected_answers.append('отмена')
            while answer not in expected_answers:
                self.write_msg(user.user_id, f'Мне нужен один из порядковых номеров, которые ты видишь чуть выше.')
                answer = self.listen_msg()[0].strip()
            else:
                if answer == "отмена":
                    return -1
                else:
                    search_values['city'] = regions[answer]

        # начальный возраст
        self.write_msg(user.user_id, f'Укажи минимальный возраст в цифрах.', keyboard=cancel_button())
        while True:
            answer = self.listen_msg()[0].strip().lower()
            try:
                answer = int(answer)
            except ValueError:
                if answer == "отмена":
                    return -1
                else:
                    self.write_msg(user.user_id, f'Укажи минимальный возраст в ЦИФРАХ.')
            else:
                search_values['age_from'] = abs(answer)
                break

        # конечный возраст
        self.write_msg(user.user_id, f'Укажи максимальный возраст в цифрах или отправь 0, если тебе это неважно.',
                       keyboard=cancel_button())
        while True:
            answer = self.listen_msg()[0].strip().lower()
            try:
                answer = int(answer)
            except ValueError:
                if answer == "отмена":
                    return -1
                else:
                    self.write_msg(user.user_id,
                                   f'Укажи максимальный возраст в ЦИФРАХ или отправь 0, если тебе это неважно.')
            else:
                if answer != 0:
                    search_values['age_to'] = abs(answer)
                else:
                    search_values['age_to'] = 100
                break

        # семейное положение
        statuses = [name[0] for name in user.select_from_db(Status.title, Status.id == Status.id).all()]
        statuses.append("Отмена")

        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(statuses[0], VkKeyboardColor.POSITIVE)
        keyboard.add_button(statuses[1], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(statuses[2], VkKeyboardColor.SECONDARY)
        keyboard.add_button(statuses[3], VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(statuses[5], VkKeyboardColor.POSITIVE)
        keyboard.add_button(statuses[4], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(statuses[6], VkKeyboardColor.SECONDARY)
        keyboard.add_button(statuses[7], VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button("Отмена", VkKeyboardColor.NEGATIVE)
        keyboard = keyboard.get_keyboard()

        self.write_msg(user.user_id, f'Какой из статусов тебя интересует?', keyboard=keyboard)

        answer = self.listen_msg(scan=False)[0].strip()

        while answer not in statuses:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
            answer = self.listen_msg()[0].strip()
        else:
            if answer == "Отмена":
                return -1
            else:
                search_values['status'] = statuses.index(answer) + 1

        # сортировка
        sort_names = [name[0] for name in user.select_from_db(Sort.title, Sort.id == Sort.id).all()]
        sort_names.append("отмена")
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sort_names[0], VkKeyboardColor.POSITIVE)
        keyboard.add_button(sort_names[1], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Отмена", VkKeyboardColor.NEGATIVE)
        keyboard = keyboard.get_keyboard()
        self.write_msg(user.user_id, f'Как отсортировать пользователей?', keyboard=keyboard)

        answer = self.listen_msg()[0].strip()
        while answer not in sort_names:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
            answer = self.listen_msg()[0].strip()
        else:
            if answer == "отмена":
                return -1
            else:
                search_values['sort'] = sort_names.index(answer)

        return self.search_users(user, search_values)

    def full_questionnaire(self, user) -> Tuple[int, int] or int:
        """ "Полный" пошаговый опросник пользователя для поиска подходящих юзеров: пол.
        Остальные вопросы в "кратком" опроснике."""

        search_values = {
            'city': None,
            'sex': None,
            'age_from': None,
            'age_to': None,
            'status': None,
            'sort': None,
        }

        # пол
        sex = [name[0] for name in user.select_from_db(Sex.title, Sex.id == Sex.id).all()]
        sex.append("отмена")

        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sex[1].capitalize(), VkKeyboardColor.NEGATIVE)
        keyboard.add_button(sex[2].capitalize(), VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(sex[0].capitalize(), VkKeyboardColor.SECONDARY)
        keyboard.add_button('Отмена', VkKeyboardColor.NEGATIVE)
        keyboard = keyboard.get_keyboard()

        self.write_msg(user.user_id, f'Людей какого пола мы будем искать?', keyboard=keyboard)

        answer = self.listen_msg()[0].strip().lower()

        while answer not in sex:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
            answer = self.listen_msg()[0].strip().lower()
        else:
            if answer == "отмена":
                return -1
            else:
                search_values['sex'] = sex.index(answer)

        return self.short_questionnaire(user, search_values)

    def initial_questionnaire(self, user, search_values) -> Tuple[int, int] or int:
        """ Начальный пошаговый опросник пользователя для поиска подходящих юзеров"""
        expected_answers = ['да', 'нет']
        answer = self.listen_msg()[0].strip()
        while answer not in expected_answers:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Просто скажи "да" или "нет" '
                                         'или используй кнопки. &#128071;')
            answer = self.listen_msg()[0].strip()
        else:
            if answer == 'да':

                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button("стандартный", VkKeyboardColor.PRIMARY)
                keyboard.add_button("детализированный", VkKeyboardColor.SECONDARY)
                keyboard = keyboard.get_keyboard()
                self.write_msg(user.user_id, f"Какой вид поиска будем использовать? &#128071;", keyboard=keyboard)

                expected_answers = ["стандартный", "детализированный"]
                answer = self.listen_msg()[0].strip()
                while answer not in expected_answers:
                    self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
                    answer = self.listen_msg()[0].strip()
                else:
                    if answer == "стандартный":
                        self.write_msg(user.user_id, f"&#128077; Прекрасный выбор!")
                        return self.search_users(user, search_values)
                    elif answer == "детализированный":
                        self.write_msg(user.user_id,
                                       f"&#128076; Ок! Тогда тебе нужно будет ответить на несколько вопросов.")
                        return self.short_questionnaire(user, search_values)
            elif answer == 'нет':
                return self.full_questionnaire(user)

    def start(self) -> None:
        """Основной метод работы бота, отвечающий за сценарий развития диалога пользователя с ботом."""

        answer, user = self.listen_msg()

        search_values = {
            'city': user.city['id'],
            'sex': None,
            'age_from': 18,
            'age_to': 99,
            'status': 6,
            'sort': 0,
        }

        expected_answers = ['привет', 'новый поиск', "результаты последнего поиска",
                            "все лайкнутые", "все непонравившиеся"]
        while answer not in expected_answers:
            self.write_msg(user.user_id, "&#129300; Не понимаю... Используй кнопки. &#128071;")
            answer = self.listen_msg()[0]
        else:
            if answer == "привет":
                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button("Да", VkKeyboardColor.POSITIVE)
                keyboard.add_button("Нет", VkKeyboardColor.NEGATIVE)

                if user.sex == 2:
                    search_values['sex'] = 1
                    self.write_msg(user.user_id, f"Хочешь найти девушку?", keyboard=keyboard.get_keyboard())
                    results = self.initial_questionnaire(user, search_values)
                elif user.sex == 1:
                    search_values['sex'] = 2
                    self.write_msg(user.user_id, f"Хочешь найти парня?", keyboard=keyboard.get_keyboard())
                    results = self.initial_questionnaire(user, search_values)
                else:
                    results = self.full_questionnaire(user)

                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.', keyboard=self.empty_keyboard)
                else:
                    if results != -1:
                        self.show_results(user, results=results)

            elif answer == "новый поиск":
                results = self.full_questionnaire(user)
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.', keyboard=self.empty_keyboard)
                else:
                    if results != -1:
                        self.show_results(user, results=results)

            elif answer == "результаты последнего поиска":
                self.show_results(user)

            elif answer == "все лайкнутые":
                liked_users = self.get_datingusers_from_db(user.user_id, blacklist=False)
                message_list = []
                message = ''
                for num, d_user in enumerate(liked_users, start=1):
                    if len(message + f'{num}. {d_user}\n') > 4097:  # предельная длина сообщения ВК
                        message_list.append(message)
                        message = ''
                    message += f'{num}. {d_user}\n'
                message_list.append(message)
                for message in message_list:
                    self.write_msg(user.user_id, message)
                self.show_results(user, datingusers=liked_users)

            elif answer == "все непонравившиеся":
                blacklist = self.get_datingusers_from_db(user.user_id, blacklist=True)
                message_list = []
                message = ''
                for num, d_user in enumerate(blacklist, start=1):
                    if len(message + f'{num}. {d_user}\n') > 4097:  # предельная длина сообщения ВК
                        message_list.append(message)
                        message = ''
                    message += f'{num}. {d_user}\n'
                message_list.append(message)
                for message in message_list:
                    self.write_msg(user.user_id, message)
            return

    def show_results(self, user, results=None, datingusers=None) -> None:
        """Метод выдачи пользователю результатов поиска"""
        if results and not datingusers:
            remainder = results[0] % 10
            if remainder == 0 or remainder >= 5 or (10 <= results[0] <= 19):
                var = 'вариантов'
            elif remainder == 1:
                var = 'вариант'
            else:
                var = 'варианта'
            self.write_msg(user.user_id, f'&#128515; Мы нашли {results[0]} {var}!!!')
            query_id = results[1]
            dating_users = self.get_datingusers_from_db(user.user_id, query_id)
        elif not results and not datingusers:
            dating_users = self.get_datingusers_from_db(user.user_id)
        else:
            dating_users = datingusers

        if dating_users:
            # получаем список юзеров из БД
            for d_user in dating_users:
                d_user.photos = d_user.get_photo()
                name = d_user.first_name + ' ' + d_user.last_name
                link = d_user.link
                if len(d_user.photos) > 1:
                    photos_list = []
                    for photo in d_user.photos:
                        photo_id, owner_id, _ = photo
                        photos_list.append(f'photo{owner_id}_{photo_id}')
                    photos = ','.join(photos_list)
                    message = f'{name} {link} \n '
                elif len(d_user.photos) == 1:
                    photo_id, owner_id, _ = d_user.photos[0]
                    photos = f'photo{owner_id}_{photo_id}'
                    message = f'{name} {link} \n '
                else:
                    message = f'{name} {link} \n Фоток нет, но вы держитесь!\n'
                    photos = ''

                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
                keyboard.add_line()
                keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
                keyboard = keyboard.get_keyboard()
                if photos:
                    self.write_msg(user.user_id, message=message, attachment=photos)
                else:
                    self.write_msg(user.user_id, message=message)
                self.write_msg(user.user_id, message='Нравится?', keyboard=keyboard)

                expected_answers = ['да', 'нет', 'отмена']
                answer = self.listen_msg()[0]
                while answer not in expected_answers:
                    self.write_msg(user.user_id, "&#129300; Не понимаю... Используй кнопки. &#128071;",
                                   keyboard=keyboard)
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
                    elif answer == "отмена":
                        self.write_msg(user.user_id, "Заходи ещё! &#128406;",
                                       keyboard=self.empty_keyboard)
                        return
        self.write_msg(user.user_id, "&#128579; Похоже, что ты уже всех посмотрел. Попробуй новый поиск! &#128373;",
                       keyboard=self.empty_keyboard)
        return

    def insert_query(self, user_id, search_values) -> int:
        """ Метод записи в БД информации об условиях поиска пользователя """
        fields = {
            'datetime': datetime.utcnow(),
            'sex_id': search_values['sex'],
            'city_id': search_values['city'],
            'age_from': search_values['age_from'],
            'age_to': search_values['age_to'],
            'status_id': search_values['status'],
            'sort_id': search_values['sort'],
            'user_id': user_id
        }
        self.insert_to_db(Query, fields)

        return self.select_from_db(Query.id, Query.id == Query.id).order_by(Query.datetime.desc()).first()[0]

    def search_users(self, vk_user, values: Dict[str, Any] = None) -> Tuple[int, int] or None:
        """ Метод поиска подходящих юзеров по запросу пользователя"""

        search_values = {
            'city': 1,
            'sex': 1,
            'age_from': 33,
            'age_to': 43,
            'status': 6,
            'sort': 1,
            'count': 1000,
            'has_photo': 1,
            'is_closed': 0,
            'can_access_closed': 1,
            'fields': 'id, verified, domain'
        }

        if values:
            search_values.update(values)

        users_list = self.vk_session.method('users.search', values=search_values)['items']

        if not users_list:
            return
        query_id = self.insert_query(vk_user.user_id, search_values)
        dusers = 0
        for user in users_list:
            if user['is_closed'] == 1:
                continue

            user['vk_id'] = user.pop('id')
            user['city_id'] = search_values['city']
            user['city_title'] = self.select_from_db(City.title, City.id == search_values['city']).first()[0]
            user['link'] = 'https://vk.com/' + user.pop('domain')
            user['verified'] = user.get('verified')
            user['query_id'] = query_id
            user['viewed'] = False
            user['user_id'] = vk_user.user_id

            user.pop('is_closed')
            user.pop('can_access_closed')
            user.pop('track_code')

            shown_user = self.select_from_db(DatingUser.viewed, (DatingUser.vk_id == user['vk_id'],
                                                                 DatingUser.user_id == vk_user.user_id)).first()
            if shown_user:
                if shown_user[0] is True:
                    continue
                elif shown_user[0] is False:
                    self.update_data(DatingUser.id, (DatingUser.vk_id == user['vk_id'],
                                                     DatingUser.user_id == vk_user.user_id,
                                                     DatingUser.viewed.is_(False)),
                                     {DatingUser.query_id: query_id})
                    dusers += 1
            else:
                self.insert_to_db(DatingUser, user)
                dusers += 1

        return dusers, query_id

    def get_datingusers_from_db(self, user_id, query_id=None, blacklist=None) -> List:
        """Метод получения юзеров из БД и создания из них экземпляров класса VKDatingUser"""
        fields = (
            DatingUser.id,
            DatingUser.vk_id,
            DatingUser.first_name,
            DatingUser.last_name,
            DatingUser.link,
        )

        if query_id and blacklist:
            raise AttributeError("Не нужно передавать в эту функцию одновременно query_id и blacklist")

        if query_id:
            vk_users = self.select_from_db(fields, (DatingUser.query_id == query_id,
                                                    DatingUser.viewed.is_(False))).all()
        else:
            if blacklist is None:
                query_id = self.select_from_db(Query.id,
                                               Query.user_id == user_id).order_by(Query.datetime.desc()).first()[0]
                vk_users = self.select_from_db(fields, (DatingUser.query_id == query_id,
                                                        DatingUser.viewed.is_(False))).all()

            elif blacklist is False:
                vk_users = self.select_from_db(fields, (DatingUser.user_id == user_id,
                                                        DatingUser.black_list.is_(False))).all()

            else:
                vk_users = self.select_from_db(fields, (DatingUser.user_id == user_id,
                                                        DatingUser.black_list.is_(True))).all()

        datingusers = [VKDatingUser(user[0], user[1], user[2], user[3], user[4]) for user in vk_users]
        return datingusers


def cancel_button() -> VkKeyboard:
    """Кнопка экстренного выхода из диалога с ботом"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def main() -> None:
    while True:
        bot = Bot()
        bot.start()


if __name__ == '__main__':
    main()
